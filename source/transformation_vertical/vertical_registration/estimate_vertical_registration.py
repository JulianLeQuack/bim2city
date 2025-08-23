# Imports
from shapely.geometry import MultiPolygon
from shapely import unary_union
import numpy as np
from scipy.spatial import KDTree
import traceback
import copy

from source.transformation_vertical.vertical_registration.get_terrain_elevation import get_terrain_elevation
from source.geometry_helpers.geometry_helpers import translate_points, rotate_points_3d


# Helper functions


# Main functions

def z_extent_is_similar(citygml_z_extent: dict, ifc_z_extent: list) -> bool:
        # Check min and max z values for CityGML and IFC Stories
        max_z_ifc = max(story['max_z'] for story in ifc_z_extent if story['max_z'] is not None)
        min_z_ifc = min(story['min_z'] for story in ifc_z_extent if story['min_z'] is not None)
        max_z_citygml = citygml_z_extent["max_z"]
        min_z_citygml = citygml_z_extent["min_z"]

        tolerance = 0.05 * (max_z_ifc - min_z_ifc)

        if -tolerance <= (max_z_ifc - min_z_ifc) - (max_z_citygml - min_z_citygml) <= tolerance:
            return True
        else:
            return False
        

def estimate_vertical_registration_manual(horizontal_transformation: dict, manual_elevation: float) -> dict:
    """
    
    """
    try:
        vertical_transformation = copy.deepcopy(horizontal_transformation)
        # If a manual Z offset is given, return it directly.
        if manual_elevation is not None:
            translation_2d = vertical_transformation["translation"]
            vertical_transformation["translation"] = np.array([translation_2d[0], translation_2d[1], manual_elevation])
            return vertical_transformation
        
    except Exception as e:
        print(f"An error occurred estimating the vertical registration: {e}")
        print(traceback.format_exc())
        return None
    

def estimate_vertical_registration_story_mapping(horizontal_transformation: dict, story_id: str, story_number: int, ifc_footprint: MultiPolygon, ifc_z_extent: list) -> dict:
    """
    
    """
    try:
        vertical_transformation = copy.deepcopy(horizontal_transformation)
        max_z_ifc = max(story['max_z'] for story in ifc_z_extent if story['max_z'] is not None)
        min_z_ifc = min(story['min_z'] for story in ifc_z_extent if story['min_z'] is not None)

        footprint = unary_union(ifc_footprint)
        centroid = [footprint.centroid.x, footprint.centroid.y]
        terrain_elevation = get_terrain_elevation(*centroid)
        ifc_story_min_z = [item["min_z"] for item in ifc_z_extent if item["story_id"] == story_id][0]
        avg_story_height = (max_z_ifc - min_z_ifc) / len(ifc_z_extent)
        offset = terrain_elevation - ifc_story_min_z + (story_number * avg_story_height)
        lod2_offset = round(offset, 2)
        translation_2d = vertical_transformation["translation"]
        vertical_transformation["translation"] = np.array([translation_2d[0], translation_2d[1], lod2_offset])
        return vertical_transformation
    
    except Exception as e:
        print(f"An error occurred estimating the vertical registration: {e}")
        print(traceback.format_exc())
        return None
    

def estimate_vertical_registration_z_extent(horizontal_transformation: dict, citygml_z_extent: dict, ifc_z_extent: list, z_extent_is_similar: bool=False) -> dict:
    """
    
    """
    try:
        if not z_extent_is_similar:
            print("Z extents do not match. Use story mapping or manual offset.")
            return None
        else:
            vertical_transformation = copy.deepcopy(horizontal_transformation)
            max_z_ifc = max(story['max_z'] for story in ifc_z_extent if story['max_z'] is not None)
            min_z_ifc = min(story['min_z'] for story in ifc_z_extent if story['min_z'] is not None)
            max_z_citygml = citygml_z_extent["max_z"]
            min_z_citygml = citygml_z_extent["min_z"]

            offset = (min_z_citygml + (max_z_citygml - min_z_citygml)/2) - (min_z_ifc + (max_z_ifc - min_z_ifc)/2)
            lod2_offset = round(offset, 2)
            translation_2d = vertical_transformation["translation"]
            vertical_transformation["translation"] = np.array([translation_2d[0], translation_2d[1], lod2_offset])
            return vertical_transformation
        
    except Exception as e:
        print(f"An error occurred estimating the vertical registration: {e}")
        print(traceback.format_exc())
        return None
    

def refine_vertical_registration_with_windows(citygml_windows: list, ifc_windows: list, lod2_transformation: dict, ifc_z_extent: list) -> float:
    """
    
    """
    try:
        lod3_transformation = copy.deepcopy(lod2_transformation)
        print(lod3_transformation)

        # Check min and max z values for CityGML and IFC Stories
        max_z_ifc = max(story['max_z'] for story in ifc_z_extent if story['max_z'] is not None)
        min_z_ifc = min(story['min_z'] for story in ifc_z_extent if story['min_z'] is not None)
        avg_story_height = (max_z_ifc - min_z_ifc) / len(ifc_z_extent)

        # If no windows, return LoD2 estimate
        if not citygml_windows or not ifc_windows:
            print(f"IFC or CityGML models have no windows. Returning LoD2 Offset.")
            return lod3_transformation
        else:
            # Prepare arrays of centroids and heights
            citygml_points = np.array([[w['x'], w['y'], w['z']] for w in citygml_windows])
            citygml_heights = np.array([w["height"] for w in citygml_windows])
            ifc_points = np.array([[w['x'], w['y'], w['z']] for w in ifc_windows])

            ifc_points_translated = translate_points(
                rotate_points_3d(
                    input_points=ifc_points,
                    center=lod3_transformation['rotation_center'],
                    angle_rad=lod3_transformation['rotation_angle']
                ),
                translation=lod3_transformation['translation']
            )

            ifc_heights = np.array([w["height"] for w in ifc_windows])

            # Build KDTree for CityGML window centroids
            tree = KDTree(citygml_points)

            # For each IFC window, find nearest CityGML window and compare heights
            z_offsets = []
            for idx, (ifc_pt, ifc_h) in enumerate(zip(ifc_points_translated, ifc_heights)):
                dist, nn_idx = tree.query(ifc_pt, distance_upper_bound=avg_story_height)
                if dist == np.inf:
                    continue  # No valid neighbor found
                citygml_h = citygml_heights[nn_idx]
                # Check that corresponding windows are not more than 1 meter different in vertical extent.
                if abs(ifc_h - citygml_h) <= 1.0:
                    z_offset = citygml_points[nn_idx][2] - ifc_pt[2]
                    z_offsets.append(z_offset)

            if z_offsets:
                # Use median to be robust to outliers
                final_offset = round(float(np.median(z_offsets)) + lod3_transformation["translation"][2], 2)
                print(f"Refined offset using matching windows: {final_offset}")
                lod3_transformation["translation"][2] = final_offset
                return lod3_transformation
            else:
                print("No matching window pairs found within 1 meter height difference. Falling back to LoD2 offset.")
                return lod3_transformation

    except Exception as e:
        print(f"An error occurred estimating the vertical registration: {e}")
        print(traceback.format_exc())
        return None