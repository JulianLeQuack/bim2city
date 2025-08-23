# Imports

import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

import traceback



# Helper Functions

def parse_citygml_file(citygml_path: str) -> ET.ElementTree:
    """
    Parses CityGML file and returns the XML element tree.

    @params citygml_path: Path to the CityGML file.
    @return: XML element tree.
    """
    try:
        tree = ET.parse(citygml_path)
        return tree
    
    except ET.ParseError as e:
        print(f"Error parsing CityGML file {citygml_path}: {e}")
        return None
    
    except Exception as e:
        print(f"An error occurred parsing the CityGML file: {e}")
        print(traceback.format_exc())
        return None



def get_citygml_namespace(citygml_tree: ET.ElementTree) -> dict:
    """
    Detects whether the citygml file is version 1.0 or 2.0.

    @param citygml_tree: Parsed CityGML model.
    @return: Namespace for correct version.
    """
    try:
        # Define namespaces for CityGML 1.0 and 2.0
        ns_1 = {
                "bldg": "http://www.opengis.net/citygml/building/1.0",
                "gml": "http://www.opengis.net/gml"
        }
        ns_2 = {
            "bldg": "http://www.opengis.net/citygml/building/2.0",
            "gml": "http://www.opengis.net/gml"
        }
        # Try to get buildings with namespaces and return the correct namespace.
        root = citygml_tree.getroot()
        if root.findall(".//bldg:Building", ns_1):
            return ns_1
        elif root.findall(".//bldg:Building", ns_2):
            return ns_2
        
    except Exception as e:
        print(f"An error occurred getting the CityGML namespace: {e}")
        print(traceback.format_exc())
        return None



def get_citygml_building_ids(citygml_tree: ET.ElementTree) -> list:
    """
    Get all building ids in the citygml file.

    @param citygml_tree: Parsed CityGML model.
    @return: List of building ids found in the CityGML file.
    """
    try:
        root = citygml_tree.getroot()
        ns = get_citygml_namespace(citygml_tree=citygml_tree)

        # Empty list for building ids
        building_ids = []
        # Find all builiding elements
        for building in root.findall(".//bldg:Building", ns):
            # Attribute key is in the full URI wrapped in "{}"
            key = f"{{{ns['gml']}}}id"
            building_id = building.attrib.get(key)
            building_ids.append(building_id)
        return building_ids
    
    except Exception as e:
        print(f"An error occurred getting the CityGML building IDs: {e}")
        print(traceback.format_exc())
        return None



# Main functions

def create_citygml_footprint(citygml_tree: ET.ElementTree, building_ids: list) -> MultiPolygon:
    """
    Generates a multipolygon from CityGML GroundSurfaces and RoofSurfaces for buildings given in building_id list.

    @param citygml_tree: XML-parsed CityGML model.
    @param building_ids: List of building ids to process.
    @return: 2D multipolygon of the building surfaces.
    """
    try:
        root = citygml_tree.getroot()
        ns = get_citygml_namespace(citygml_tree=citygml_tree)

        polygons = []
        for building_id in building_ids:
            # Get building by ID
            building = root.find(f".//bldg:Building[@gml:id='{building_id}']", ns)
            if building is None:
                print(f"Warning: No building found with ID {building_id}.")
                continue
            # Get GroundSurfaces from the building
            surfaces = building.findall(".//bldg:GroundSurface", ns)
            surfaces.extend(building.findall(".//bldg:RoofSurface", ns))
            if not surfaces:
                print(f"Warning: No GroundSurface found for building with ID {building_id}.")
                continue
            for surface in surfaces:
                entity_polygons = []
                # Get GroundSurface posList
                posLists = surface.findall(".//gml:posList", ns)
                if posLists is None:
                    print(f"No posList was found for a GroundSurface. Skipping.")
                    continue
                for posList in posLists:
                    # Get coordinates from posList. PosList looks like this: X Y Z X Y Z X Y Z
                    coordinates = list(map(float, posList.text.split()))
                    # Extract X and Y from coordinates for 2D representation
                    coordinates_2d = []
                    for i in range(0, len(coordinates), 3):
                        coordinates_2d.append((coordinates[i], coordinates[i+1]))
                    # Check if at least 3 points so a valid poylgon can be created
                    if len(coordinates_2d) >= 3:
                        polygon = Polygon(coordinates_2d)
                        # Check if polygonis valid
                        if polygon.is_valid:
                            entity_polygons.append(polygon)
                # Create a simplified polygon for every entity by appending the exterior.
                entity_union = unary_union(entity_polygons)
                if entity_union.geom_type == "Polygon" and entity_union.is_valid:
                    polygons.append(Polygon(entity_union.exterior))
                elif entity_union.geom_type == "MultiPolygon":
                    for geom in entity_union.geoms:
                        if geom.is_valid:
                            polygons.append(Polygon(geom.exterior))

        return MultiPolygon(polygons)

    except Exception as e:
        print(f"An error occurred creating the CityGML footprint: {e}")
        print(traceback.format_exc())
        return MultiPolygon()