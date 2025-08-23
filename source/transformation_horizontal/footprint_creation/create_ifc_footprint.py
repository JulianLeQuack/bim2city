# Imports

import ifcopenshell, ifcopenshell.geom, ifcopenshell.util.shape, ifcopenshell.file, ifcpatch

from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

import numpy as np
import traceback



# Helper functions

def parse_ifc_file(ifc_path: str) -> ifcopenshell.file:
    """
    Parses IFC file and returns it for further use.

    @param ifc_path: Path to the IFC file.
    @return: Parsed IFC model.
    """
    try:
        ifc_model_raw = ifcopenshell.open(ifc_path)

        ifc_model = ifcpatch.execute({
            "file": ifc_model_raw,
            "recipe": "ConvertLengthUnit",
            "arguments": ["METER"]
        })

        return ifc_model

    except Exception as e:
        print(f"An error occurred parsing the IFC file: {e}")
        print(traceback.format_exc())
        return None



def get_building_stories(ifc_model: ifcopenshell.file) -> list:
    """
    Returns all IfcBuildingStorey IDs from an IFC file.

    @param ifc_model: Parsed IFC model.
    @return: List of the building story IDss.
    """
    try:
        stories = []
        for entity in ifc_model.by_type("IfcBuildingStorey"):
            if entity.GlobalId not in stories:
                stories.append(entity.GlobalId)
        return stories

    except Exception as e:
        print(f"An error occurred getting the building stories: {e}")
        print(traceback.format_exc())
        return None
    


def get_ifc_classes(ifc_model: ifcopenshell.file) -> list:
    """
    Get all classes that appear in an IFC file.

    @param ifc_model: Parsed IFC model.
    @return: List of the class names.
    """
    try:
        classes = []
        for entity in ifc_model:
            if entity.is_a() not in classes:
                classes.append(entity.is_a())
        return classes

    except Exception as e:
        print(f"An error occurred getting the IFC classes: {e}")
        print(traceback.format_exc())
        return None



# Main functions

def create_ifc_footprint(ifc_model: ifcopenshell.file, ifc_types: list, building_stories: list, detailed: bool=False) -> MultiPolygon:
    """
    Generates a 2D multipolygon footprint from an IFC model.

    @param ifc_model: Parsed IFC model.
    @param ifc_types: List of IFC classes to use for footprint creation.
    @param building_stories: List of building story IDs for footprint creation.
    @param detailed: Returns detailed entity geometries if needed for floor plan-like representation.
    @return 2D multipolygon footprint.
    """


    try:
        # Get all elements in the given building stories
        elements = []
        for rel in ifc_model.by_type("IfcRelContainedInSpatialStructure"):
            # Check if name appears in building story names
            if rel.RelatingStructure.GlobalId in building_stories:
                for element in rel.RelatedElements:
                    # Check if name appears in the ifc class names
                    if element.is_a() in ifc_types:
                        elements.append(element)
        if len(elements) == 0:
            print(f"No IFC elements found for Building Stories {building_stories} and IFC Classes {ifc_types}.")
            return MultiPolygon()

        settings = ifcopenshell.geom.settings()
        polygons = []

        # Extract geometry from every element
        for element in elements:
            try:
                shape = ifcopenshell.geom.create_shape(settings, element)
            except Exception as e:
                continue

            # Get element vertices and faces and the transformation matrix
            verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
            faces = ifcopenshell.util.shape.get_faces(shape.geometry)
            matrix = ifcopenshell.util.shape.get_shape_matrix(shape)

            # Transform vertices
            transformed_verts = []
            for v in verts:
                v_homog = np.array([v[0], v[1], v[2], 1.0])
                v_transformed = matrix @ v_homog
                transformed_verts.append(v_transformed[:3])

            # List of polygons that belong to one IFC entity.
            entity_polygons = []

            # Create polygons using the faces and their vertices, only take X and Y so 2D representation
            for face in faces:
                coordinates = [transformed_verts[i] for i in face]
                coordinates_2d = []
                for coord in coordinates:
                    coordinates_2d.append((coord[0], coord[1]))
                polygon = Polygon(coordinates_2d)
                if polygon.is_valid:
                    # polygons.append(polygon)
                    entity_polygons.append(polygon)
            # Create a simplified polygon for every entity by appending the exterior.
            entity_union = unary_union(entity_polygons)
            if entity_union.geom_type == "Polygon" and entity_union.is_valid:
                polygons.append(Polygon(entity_union.exterior))
            elif entity_union.geom_type == "MultiPolygon":
                for geom in entity_union.geoms:
                    if geom.is_valid:
                        polygons.append(Polygon(geom.exterior)) 

        if not detailed:
            # If detailed is False, return unary union of the polygons.
            union_poly = unary_union(polygons)
            if union_poly.geom_type == "Polygon":
                return MultiPolygon([union_poly])
            elif union_poly.geom_type == "MultiPolygon":
                return union_poly
            else:
                return MultiPolygon()
        else:
            # If detailed is set to true, return polygons directly.
            valid_polygons = []
            for polygon in polygons:
                if isinstance(polygon, Polygon) and polygon.is_valid:
                    valid_polygons.append(polygon)
            if valid_polygons:
                return(MultiPolygon(valid_polygons))
            else:
                return MultiPolygon()

    except Exception as e:
        print(f"An error occurred creating the IFC footprint: {e}")
        print(traceback.format_exc())
        return MultiPolygon()