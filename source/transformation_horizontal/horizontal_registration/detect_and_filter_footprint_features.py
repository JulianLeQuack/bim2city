# Imports

import numpy as np
from shapely.geometry import MultiPolygon

import traceback

from source.geometry_helpers.geometry_helpers import get_angle_between_vectors


# Helper functions

def get_triangle_area(p: np.ndarray, c: np.ndarray, n: np.ndarray) -> float:
    """
    From three points, get the area of the triangle they span.
    @param p: Previous adjacent point.
    @param c: Current point.
    @param n: Next adjacent point.
    @return: Area spanned by the three input points.
    """
    try:
        #Compute triangle area with shoelace formula.
        triangle_area = 0.5 * abs((p[0] * c[1] + c[0] * n[1] + n[0] * p[1]) - (p[1] * c[0] + c[1] * n[0] + n[1] * p[0]))
        return triangle_area

    except Exception as e:
        print(f"An error occurred getting the triangle area: {e}")
        print(traceback.format_exc())
        return None
    


# Main functions

def detect_footprint_features(footprint: MultiPolygon, angle_threshold_rad: float=0.1) -> list:
    """
    Detects corners in a multipolygon footprint as a feature if they span an angle larger than a specific turning angle.
    For each polygon in the multipolygon, the angle is spanned with its adjacent vertices.

    @param footprint: A multipolygon that is the footprint of a model.
    @param angle_threshold_rad: Threshold above and below which corners are not detected. If it is 0.1 radians, then corners between 0.1 and pi - 0.1 will be detected.
    @return: List of lists of points per source polygon as array objects.
    """
    try:
        # Create list for all features grouped by source polygon.
        features = []
        # Iterate over all polygons in the footprint multipolygon.
        for polygon in footprint.geoms:
            # Create list for all features in one polygon.
            polygon_features = []
            
            # Remove duplicate vertex of closed polygon for correct turning angle computation if it exists.
            vertices = np.array(polygon.exterior.coords)
            if np.allclose(vertices[0][:2], vertices[-1][:2]):
                vertices = vertices[:-1]
            
            # Iterate over all vertices in the polygon. Use the vertex_id to find the adjacent vertices of the current one.
            for vertex_id, vertex in enumerate(vertices):
                previous_vertex = vertices[vertex_id - 1]
                next_vertex = vertices[(vertex_id + 1) % len(vertices)] # % (modulo operator) for wrap around if last vertexis reached
                
                # Compute the turning angle that the 3 adjacent vertices span.
                vector_1 = vertex - previous_vertex
                vector_2 = next_vertex - vertex
                turning_angle = abs(get_angle_between_vectors(vector_1, vector_2))

                # Add information to features list if it is larger than the threshold and less than close to colinear.
                if angle_threshold_rad < turning_angle < np.pi - angle_threshold_rad:
                    polygon_features.append(vertex)
            unique_polygon_features = np.unique(np.array(polygon_features).round(1), axis=0)
            features.append(polygon_features)
        return features

    except Exception as e:
        print(f"An error occurred detecting the footprint features: {e}")
        print(traceback.format_exc())
        return None



def filter_footprint_features(features: list, area_threshold_squaremeters: float=0) -> np.ndarray:
    """
    Filters out insignificant features by finding the area of the triangle a feature spans with its adjacent features.
    If that area is smaller than the threshold, the feature is defined as insignificant.

    @param features: List of grouped by source polygon detected features from footprint polygons.
    @param area_threshold_squaremeters: Minimum area a feature must span to be significant.
    @return: Flattened np.ndarray of the filtered features.
    """
    try:
        filtered_features = []
        # Iterate over all polygons inside the features list.
        for polygon_features in features:
            polygon_features = np.unique(np.array(polygon_features).round(2), axis=0)
            # Iterate over all featrues per polygon
            for feature_id, feature in enumerate(polygon_features):
                previous_feature = polygon_features[feature_id - 1]
                next_feature = polygon_features[(feature_id + 1) % len(polygon_features)]

                # Compute the area of the triangle spanned by the 3 adjacent features.
                triangle_area = get_triangle_area(previous_feature, feature, next_feature)

                # Check against threshold area
                if triangle_area >= area_threshold_squaremeters:
                    filtered_features.append(feature)
        filtered_features = np.unique(np.array(filtered_features).round(2), axis=0)
        # # Remove double features in same place.
        # unique_filtered_features = np.unique(filtered_features.round(2), axis=0)
        return filtered_features

    except Exception as e:
        print(f"An error occurred detecting the footprint features: {e}")
        print(traceback.format_exc())
        return None