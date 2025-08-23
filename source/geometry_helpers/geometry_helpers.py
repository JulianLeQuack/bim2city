# Imports

import numpy as np
from shapely.geometry import MultiPolygon, Polygon
from shapely.affinity import rotate, translate
from shapely.ops import unary_union
import ifcopenshell
import ifcpatch
import trimesh
from trimesh import Trimesh
import mapbox_earcut
import pigar # to add it to requirements usign pigar itself



def get_angle_between_vectors(vector_1: np.ndarray, vector_2: np.ndarray) -> float:
    """
    From three points, get the angle they span.
    @param vector_1: Source vector.
    @param vector_2: Target vector.
    @return: Angle spanned between the vectors in radians.
    """
    try:
        # Compute turning angle
        cross_product = vector_1[0] * vector_2[1] - vector_1[1] * vector_2[0]
        dot_product = np.dot(vector_1, vector_2)
        turning_angle = np.arctan2(cross_product, dot_product)
        return turning_angle
    
    except Exception as e:
        print(f"An error occurred getting the turning angle: {e}")
        return None
    


def flatten_nested_list(input_list: list) -> np.ndarray:
    """
    Turns any list into a flattened version of itself.
    Example: [[[3, 4], 5, (2, 3, 9), 6], 6] -> [3, 4, 5, 2, 3, 9, 6, 6]
    """
    flattened_list = []
    for item in input_list:
        if isinstance(item, (list, tuple, np.ndarray)):
            flattened_list.extend(flatten_nested_list(item))
        else:
            flattened_list.append(item)
    return np.array(flattened_list)

def flatten_nested_coordinate_list(input_list: list) -> np.ndarray:
    """
    Flattens any nested list of 2D point coordinates into a flat list of 2D points.
    Example: [[[0, 1], [2, 3]], [4, 5], [[6, 7], [[8, 9]]]] -> [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
    """
    flattened_list = []
    for item in input_list:
        # Check if item is a 2D point (list/tuple of length 2 with both elements numbers)
        if (isinstance(item, (list, tuple, np.ndarray)) and len(item) == 2 and
            all(isinstance(coord, (int, float, np.integer, np.floating)) for coord in item)):
            flattened_list.append(np.array(item))
        elif isinstance(item, (list, tuple, np.ndarray)):
            flattened_list.extend(flatten_nested_coordinate_list(item))
        else: 
            flattened_list.append(item)
    return np.array(flattened_list)



def rotate_points(input_points: np.ndarray, center: np.ndarray, angle_rad: float) -> np.ndarray:
    """
    Rotate an array of 2D points around a specified center.
    @param input_points: 2D points to be rotated.
    @param center: Rotation center point.
    @param angle_rad: Angle of rotation in radians.
    @return: Array of 2D points
    """
    translated = input_points - center
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad),  np.cos(angle_rad)]
    ])
    rotated = translated @ rotation_matrix.T + center
    return rotated


def rotate_points_3d(input_points: np.ndarray, center: np.ndarray, angle_rad:float) -> np.ndarray:
    """
    Rotate an array of 3D points around a specified center.
    @param input_points: 3D points to be rotated.
    @param center: Rotation center point.
    @param angle_rad: Angle of rotation in radians.
    @return: Array of 3D points
    """
    center_3d = np.array([center[0], center[1], 0])
    translated = input_points - center_3d
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad), 0],
        [np.sin(angle_rad),  np.cos(angle_rad), 0],
        [0,                  0,                 1]
    ])
    rotated = translated @ rotation_matrix.T + center_3d
    return rotated


def rotate_multipolygon(input_mp: MultiPolygon, center: np.ndarray, angle_rad: float) -> MultiPolygon:
    """
    Rotates a shapely multipolygon around a point by an angle given in radians.

    @param input_mp: Multipolygon to rotate.
    @param center: Point around which the roation is performed.
    @param angle_rad: Angle by which to rotate, given in radians.
    @return: Multipolygon after rotation.
    """
    rotated = rotate(input_mp, angle_rad, tuple(center), use_radians=True)
    return rotated


def translate_points(input_points: np.ndarray, translation: np.ndarray) -> np.ndarray:
    """
    Translates an array of 2D points by a 2D input vector.

    @param input_points: 2D points to be translated.
    @param translation: Vector by which the points are translated.
    @return: Array of translated 2D points.
    """
    translated = input_points + translation
    return translated


def translate_multipolygon(input_mp: MultiPolygon, translation: np.ndarray) -> MultiPolygon:
    """
    Translates a shapely multipolygon by a 2D translation vector.

    @param input_mp: Multipolygon to translate.
    @param translation: Translation vector.
    @return: Translated multipolygon.
    """
    translated = translate(input_mp, translation[0], translation[1])
    return translated


# For sideview IFC

def extrude_multipolygon(multipolygon: MultiPolygon, height: float) -> Trimesh:
    meshes = []
    hull = multipolygon.convex_hull
    mesh = trimesh.creation.extrude_polygon(hull, height)
    return mesh
    # for poly in multipolygon.geoms:
    #     mesh = trimesh.creation.extrude_polygon(poly, height)
    #     meshes.append(mesh)
    # return trimesh.util.concatenate(meshes)

def mesh_to_sideview_multipolygon(mesh) -> MultiPolygon:
    """
    Projects a 3D mesh onto the YZ plane and returns a MultiPolygon representing the side view.
    """
    polygons = []
    for face in mesh.faces:
        # Get the 3D coordinates of the face's vertices
        verts = mesh.vertices[face]
        # Project to YZ plane (drop X)
        yz = [(v[1], v[2]) for v in verts]
        # Only add valid polygons (at least 3 unique points)
        if len(set(yz)) >= 3:
            polygons.append(Polygon(yz))
    # Union all polygons to avoid overlaps and return as MultiPolygon
    unioned = unary_union(polygons)
    if unioned.is_empty or unioned is None:
        return MultiPolygon()
    if isinstance(unioned, Polygon):
        return MultiPolygon([unioned])


def transform_ifc(ifc_model: ifcopenshell.file, transformation: dict) -> ifcopenshell.file:
    """
    Rotates and translates an IFC model and returns it.

    @param ifc_model: A parsed ifcopenshell model.
    @param transformation: A dictionary created by the registration estimation.
    @return: Transformed ifcopenshell model.
    """
    rotation_angle_rad = transformation["rotation_angle"]
    rotation_angle = np.degrees(rotation_angle_rad)
    rotation_center = transformation["rotation_center"]

    translation = transformation["translation"]
    if len(translation) == 2:
        x, y, z = translation[0], translation[1], 0
    elif len(translation) == 3:
        x, y, z = translation[0], translation[1], translation[2]

    print(f"Transforming IFC model: {transformation}\nRotation Angle: {rotation_angle}\nRotation Center: {rotation_center}\nTranslation: {x,y,z}")
    
    translated_to_origin = ifcpatch.execute({
        "file": ifc_model,
        "recipe": "OffsetObjectPlacements",
        "arguments": [-rotation_center[0], -rotation_center[1], 0, False, 0, 0, 0]
    })

    translated_to_origin_and_rotated = ifcpatch.execute({
        "file": translated_to_origin,
        "recipe": "OffsetObjectPlacements",
        "arguments": [0, 0, 0, True, 0, 0, rotation_angle]
    })

    retranslated = ifcpatch.execute({
        "file": translated_to_origin_and_rotated,
        "recipe": "OffsetObjectPlacements",
        "arguments": [rotation_center[0], rotation_center[1], 0, False, 0, 0, 0]
    })

    transformed_hor = ifcpatch.execute({
        "file": retranslated,
        "recipe": "OffsetObjectPlacements",
        "arguments": [x, y, 0, False, 0, 0, 0]
    })

    transformed_vert = ifcpatch.execute({
        "file": transformed_hor,
        "recipe": "OffsetObjectPlacements",
        "arguments": [0, 0, z, False, 0, 0, 0]
    })

    return transformed_vert

