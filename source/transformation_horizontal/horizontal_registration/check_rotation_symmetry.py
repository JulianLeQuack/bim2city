# Imports

import numpy as np
import traceback

from shapely.geometry import MultiPolygon, Polygon
from shapely import unary_union

from source.geometry_helpers.geometry_helpers import rotate_multipolygon


# Helper functions



# Main functions

def check_rotational_symmetry(footprint: MultiPolygon) -> list:
    """
    
    """
    try:
        footprint = unary_union(footprint)
        footprint = footprint.buffer(0)
        k_max = 12
        centroid = [footprint.centroid.x, footprint.centroid.y]

        symmetry_angles = set()

        for k in range(2, k_max):
            # Define rotation angle for k-fold symmetry.
            rotation_angle = 2 * np.pi / k
            # Rotate footprint by that angle. If k is 4 and the footprint has a 4-fold rotation symmetry (every 90 deg), the IoU is already close to 1 after rotating by 90 deg.
            rotated_footprint = rotate_multipolygon(footprint, centroid, rotation_angle).buffer(0)
            # Compute intersection and union areas between original and rotated footprint.
            intersection = footprint.intersection(rotated_footprint)
            intersection_area = intersection.area
            union = footprint.union(rotated_footprint)
            union_area = union.area
            
            # Compute intersection over union.
            iou = intersection_area / union_area
            # If IoU is greater than 95%, the angle is a rotation angle.
            if iou > 0.95:
                for step in range (1, k):
                    symmetry_angles.add(rotation_angle * step)        
        return list(symmetry_angles)

    except Exception as e:
        print(f"An error occurred checking the point symmetry: {e}")
        print(traceback.format_exc())
        return None
