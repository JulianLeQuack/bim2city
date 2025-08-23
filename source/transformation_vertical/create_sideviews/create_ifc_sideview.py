# Imports

import ifcopenshell, ifcopenshell.geom, ifcopenshell.util.shape, ifcopenshell.file, ifcpatch

from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

import numpy as np
import traceback



# Helper functions



# Main functions

def create_ifc_sideview(ifc_model: ifcopenshell.file) -> MultiPolygon:
    """
    
    """
    try:
        settings = ifcopenshell.geom.settings()
        polygons = []

        elements = ifc_model.by_type("IfcWall")
        elements.extend(ifc_model.by_type("IfcSlab"))
        # elements.extend(ifc_model.by_type("IfcWindow"))

        for element in elements:
            try:
                shape = ifcopenshell.geom.create_shape(settings, element)
            except Exception as e:
                continue

            verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
            faces = ifcopenshell.util.shape.get_faces(shape.geometry)
            matrix = ifcopenshell.util.shape.get_shape_matrix(shape)

            transformed_verts = []
            for v in verts:
                v_homog = np.array([v[0], v[1], v[2], 1.0])
                v_transformed = matrix @ v_homog
                transformed_verts.append(v_transformed[:3])

            entity_polygons = []

            for face in faces:
                coordinates = [transformed_verts[i] for i in face]
                coordinates_2d = []
                for coord in coordinates:
                    coordinates_2d.append((coord[1], coord[2]))
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

        valid_polygons = []
        for polygon in polygons:
            if isinstance(polygon, Polygon) and polygon.is_valid:
                valid_polygons.append(polygon)
        
        if not valid_polygons:
            polygons = []
        unionized = unary_union(valid_polygons)
        if unionized.geom_type == "Polygon":
            polygons = [unionized]
        elif unionized.geom_type == "MultiPolygon":
            polygons = unionized

            if not polygons:
                polygons = []
            unionized = unary_union(polygons)
            if unionized.geom_type == "Polygon":
                polygons = [unionized]
            elif unionized.geom_type == "MultiPolygon":
                polygons = unionized

        return MultiPolygon(polygons)

    except Exception as e:
        print(f"An error occurred creating the IFC footprint: {e}")
        print(traceback.format_exc())
        return MultiPolygon()    