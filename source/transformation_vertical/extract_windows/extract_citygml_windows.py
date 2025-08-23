# Imports

import xml.etree.ElementTree as ET
import traceback
import numpy as np

from source.transformation_horizontal.footprint_creation.create_citygml_footprint import get_citygml_namespace


# Helper functions

# Main functions

def extract_citygml_windows(citygml_model: ET.ElementTree, building_ids: list) -> dict:
    """
    Extracts window centroids from CityGML LOD3 model.

    @param citygml_model: Parsed CityGML LOD3 model.
    @param building_ids: List of building ids to extract windows from.
    @return: Dictionary of form: {'window_id': 'DEBY_LOD2_4959457_BP.CYiLztRiAXx225bojwTn', 'x': 691016.3, 'y': 5336003.01, 'z': 523.79, 'height': 3.35}.
    """
    try:
        root = citygml_model.getroot()
        namespace = get_citygml_namespace(citygml_model)

        # List to collect window centroids.
        window_centroids = []

        for building_id in building_ids:
            # Get building by ID
            building = root.find(f".//bldg:Building[@gml:id='{building_id}']", namespace)
            if building is None:
                print(f"Warning: No building found with ID {building_id}.")
                continue
            # Find all windows in the building.
            windows = building.findall('.//bldg:Window', namespace)
            for window in windows:
                window_id = window.attrib.get(f"{{{namespace['gml']}}}id", None)
                # Find all posLists in the windows
                posLists = window.findall('.//gml:posList', namespace)
                # List to collect all attirbutes that belong to the window.
                all_points = []
                # Iterate over all posLists and get their X, Y, Z coords
                for poslist in posLists:
                    coords = list(map(float, poslist.text.split()))
                    points = [(coords[i], coords[i+1], coords[i+2]) for i in range(0, len(coords), 3)]
                    all_points.extend(points)
                if all_points:
                    points_np = np.array(all_points)
                    centroid = points_np.mean(axis=0)
                    min_z = float(np.min(points_np[:, 2]))
                    max_z = float(np.max(points_np[:, 2]))
                    window_centroids.append({
                        "window_id": window_id,
                        "x": round(float(centroid[0]), 2),
                        "y": round(float(centroid[1]), 2),
                        "z": round(float(centroid[2]), 2),
                        "height": round(max_z - min_z, 2),
                    })

        if not window_centroids:
            return None
        return window_centroids

    except Exception as e:
        print(f"Error extracting CityGML window centroids: {e}")
        print(traceback.format_exc())
        return None