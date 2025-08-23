# Imports

import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

import traceback

from source.transformation_horizontal.footprint_creation.create_citygml_footprint import get_citygml_namespace



# Helper functions



# Main functions

def create_citygml_sideview(citygml_tree: ET.ElementTree, building_ids: list) -> MultiPolygon:
    """
    
    """
    try:
        root = citygml_tree.getroot()
        ns = get_citygml_namespace(citygml_tree=citygml_tree)

        polygons = []
        polygons_windows = []

        for building_id in building_ids:
            building = root.find(f".//bldg:Building[@gml:id='{building_id}']", ns)
            if building is None:
                print(f"Warning: No building found with ID {building_id}.")
                continue
            surfaces = building.findall(".//bldg:GroundSurface", ns)
            surfaces.extend(building.findall(".//bldg:WallSurface", ns))
            surfaces.extend(building.findall(".//bldg:RoofSurface", ns))
            # surfaces.extend(building.findall(".//bldg:Window", ns))

            if not surfaces:
                print(f"Warning: No GroundSurface found for building with ID {building_id}.")
                continue
            for surface in surfaces:
                entity_polygons = []
                posLists = surface.findall(".//gml:posList", ns)
                if posLists is None:
                    print(f"No posList was found for a GroundSurface. Skipping.")
                    continue
                for posList in posLists:
                    coordinates = list(map(float, posList.text.split()))
                    coordinates_2d = []
                    for i in range(0, len(coordinates), 3):
                        coordinates_2d.append((coordinates[i+1], coordinates[i+2]))
                    if len(coordinates_2d) >= 3:
                        polygon = Polygon(coordinates_2d)
                        if polygon.is_valid:
                            entity_polygons.append(polygon)
                entity_union = unary_union(entity_polygons)
                if entity_union.geom_type == "Polygon" and entity_union.is_valid:
                    polygons.append(Polygon(entity_union.exterior))
                elif entity_union.geom_type == "MultiPolygon":
                    for geom in entity_union.geoms:
                        if geom.is_valid:
                            polygons.append(Polygon(geom.exterior))
            
        if not polygons:
            polygons = []
        unionized = unary_union(polygons)
        if unionized.geom_type == "Polygon":
            polygons = [unionized]
        elif unionized.geom_type == "MultiPolygon":
            polygons = unionized

        return MultiPolygon(polygons)
    
    except ET.ParseError as e:
        print(f"Error parsing CityGML file: {citygml_tree}, Error: {e}")
        return MultiPolygon([])
    except ValueError as e:
        print(e)
        return MultiPolygon([])
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        return MultiPolygon([])