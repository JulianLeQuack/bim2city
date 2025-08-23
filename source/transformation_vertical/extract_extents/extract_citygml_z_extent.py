# Imports

import xml.etree.ElementTree as ET
import numpy as np

import traceback

from source.transformation_horizontal.footprint_creation.create_citygml_footprint import get_citygml_namespace


# Helper functions



# Main functions

def extract_citygml_z_extent(citygml_model: ET.ElementTree, building_ids: list) -> dict:
    """
    Returns the overall height of the model.

    @param citygml_model: A parsed element tree of the citygml model.
    @return: Z extent or height of the model.
    """
    try:
        # Get the CityGML version/namespace.
        namespace = get_citygml_namespace(citygml_model)
        # Get the model root.
        root = citygml_model.getroot()

        # List to collect z values.
        z_values = []

        for building_id in building_ids:
            # Get building by ID
            building = root.find(f".//bldg:Building[@gml:id='{building_id}']", namespace)
            if building is None:
                print(f"Warning: No building found with ID {building_id}.")
                continue
            posLists = building.findall(".//gml:posList", namespace)
            for posList in posLists:
                # Get coordinates from posList. PosList looks like this: X Y Z X Y Z X Y Z
                coordinates = list(map(float, posList.text.split()))
                # Extract Z coordinates and append to list of z values.
                z_values.extend(coordinates[2::3])
        #Return dict with min and max z value.
        return {"min_z": min(z_values), "max_z": max(z_values)}
    
    except Exception as e:
        print(f"An error occurred extracting the CityGML Z extent: {e}")
        print(traceback.format_exc())
        return None