# Imports

import numpy as np
import traceback

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape



# Helper functions



# Main functions

def extract_ifc_windows(ifc_model: ifcopenshell.file) -> dict:
    """
    Extracts window centroids from an IFC model.

    @param ifc_model: Parsed ifcopenshell model.
    @return: Dictionary of from: {'window_id': '2MPOlgJ$1VdW0100000f7p', 'x': 41.45, 'y': -41.82, 'z': 7.73, 'height': 3.45}.
    """
    try:
        settings = ifcopenshell.geom.settings()
        window_centroids = []

        # Get all IfcWindow elements
        windows = ifc_model.by_type("IfcWindow")
        for window in windows:
            window_id = window.GlobalId
            # List for all geometries that belong to the window.
            all_points = []
            try:
                shape = ifcopenshell.geom.create_shape(settings, window)
            except Exception:
                continue
            verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
            matrix = ifcopenshell.util.shape.get_shape_matrix(shape)
            # Extract geometries.
            for v in verts:
                v_homog = np.array([v[0], v[1], v[2], 1.0])
                v_transformed = matrix @ v_homog
                all_points.append(v_transformed[:3])
            if all_points:
                # Assemble per-window dictionary entry.
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
        print(f"Error extracting IFC window centroids: {e}")
        print(traceback.format_exc())
        return None