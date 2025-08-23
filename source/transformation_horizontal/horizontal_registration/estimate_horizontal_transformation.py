# Imports
import numpy as np
from multiprocessing import Pool
import itertools
from scipy.spatial import KDTree

import traceback

from source.geometry_helpers.geometry_helpers import get_angle_between_vectors, rotate_points, translate_points


# Helper functions

def get_horizontal_transformation_for_point_pairs(pair_1: np.ndarray, pair_2: np.ndarray) -> dict:
    """
    Get the translation and rotation required to align two pairs of points.

    @param pair_1: First match of points from source and target.
    @param pair_2: Second match of points from source and target.
    @return: Dict of form: {"rotation_angle": rotation_in_radians, "rotation_center": rotation_center_point, "translation": array([x, y])}.
    """
    try:
        rotation_angle = None
        translation_vector = None
        # Create vectors between the source points and target points.
        source_vector = pair_2[0] - pair_1[0]
        target_vector = pair_2[1] - pair_1[1]

        # Check if the point pairs are similarly distant apart. If not, cant be matches.
        source_vector_length = np.linalg.norm(source_vector)
        target_vector_length = np.linalg.norm(target_vector)
        if abs(source_vector_length - target_vector_length) >= source_vector_length * 0.05:
            return None

        # Get the rotation angle to align the vectors.
        rotation_angle = get_angle_between_vectors(source_vector, target_vector)

        # Get vector midpoints for translation.
        source_vector_midpoint = (pair_1[0] + pair_2[0]) / 2
        target_vector_midpoint = (pair_1[1] + pair_2[1]) / 2

        # Get the translation vector to alig the midpoints.
        translation_vector = target_vector_midpoint - source_vector_midpoint
        
        # Create the transformation dict and return it.
        transformation = {"rotation_angle": rotation_angle, "rotation_center": source_vector_midpoint, "translation": translation_vector}
        return transformation

    except Exception as e:
        print(f"An error occurred getting the horizontal transformation from point pairs: {e}")
        print(traceback.format_exc())
        return



def get_inliers_for_transformation(source_features: np.ndarray, inlier_threshold: float, target_tree: KDTree, transformation: dict) -> dict:
    """
    Applies the transformation to the source features and checks for inliers with target features.
    
    @param source_features: Source features to apply the transformation to.
    @param cource_centroid: Source centroid used as rotation point.
    @param inlier_threshold: Defines max distance between nearest neighbors between transformed source features and target features before they do not match.
    @param target_tree: KDTree of target features needed for nearet neighbor query.
    @param transformation: Transformation dict as produced in get_horizontal_registration_for_point_pairs.
    @return: Dict with the transformation and number of inliers as a measure of how well the estimated transformation fits the overall dataset.
    """
    try:
        # Check if transformation is none.
        if transformation == None:
            return None
        # Apply the transformation to the source features.
        transformed_source = translate_points(rotate_points(source_features, transformation["rotation_center"], transformation["rotation_angle"]), transformation["translation"])
        # Create a list to store matching pairs of inliers.
        inlier_pairs = []
        # Iterate over all source points and query the target tree for every source point to find the nearest neighbors.
        for source_id, source_feature in enumerate(transformed_source):
            # Get distances and target ids for current source point to nearest neighbors for inlier check.
            distance, target_id = target_tree.query(source_feature)
            # Check if the nearest neighbor is within the distance threshold and add if yes to inlier pairs.
            if distance < inlier_threshold:
                inlier_pairs.append([source_id, int(target_id)])
        # Add full list of inliers by source and target is to the transformation dict.
        transformation["inliers"] = inlier_pairs
        return transformation
    
    except Exception as e:
        print(f"An error occurred getting the inliers for a transformation: {e}")
        print(traceback.format_exc())
        return




# Main functions

def estimate_rough_horizontal_registration(source_features: np.ndarray, target_features: np.ndarray, inlier_distance_threshold: float=None, fixed_features: list=[[],[]]) -> dict:
    """
    Rough estimation of the rigid transformation parameters to align the source features with the target features.

    @param source_featuers: Features that are to be registered.
    @param target_features: Features the source_features are to be registered to.
    @param fixed_features: List of 0, 1, or 2 predefined matching feature pairs' indices. The form is [[index_of_source_feature_1, index_of_source_feature_2], [index_of_target_feature_1, index_of_target_feature_2]].
    @return: Dictionary containing the translation and rotation estimated.
    """
    try:
        # Check number of features for OOM warning.
        if len(source_features) >= 50 or len(target_features) >= 50:
            print(f"Warning: High number of features detected! This may result in the process dying due to memory constraints!\nNumber of source features: {len(source_features)}\nNumber of target features: {len(target_features)}")
        # Get features extent to define an inlier threshold, if no other threshold is given. 
        min_x = min(point[0] for point in source_features)
        max_x = max(point[0] for point in source_features)
        min_y = min(point[1] for point in source_features)
        max_y = max(point[1] for point in source_features)
        diagonal = np.array(np.array((max_x,max_y)) - np.array((min_x,min_y)))
        if inlier_distance_threshold is None:
            inlier_distance_threshold = np.linalg.norm(diagonal) * 0.01
        print(f"Inlier distance threshold for aligned features: {inlier_distance_threshold}")
        
        # Generate kd tree for target features for checking transformation candidates for inliers.
        target_tree = KDTree(target_features)

        # If more than 2 matches are given, error.
        if len(fixed_features[0]) > 2:
            print(f"Max number of manual featrue matches is 2, received {len(fixed_features)}.")
            return None
        
        # Check if 2 manual matches are give. If so, just get the transformation to align them directly.
        elif len(fixed_features[0]) == 2:
            print(f"Received 2 matching features. Running manual registration.")
            # Get the 2 fixed features from the source and target dataset.
            fixed_source_id_1, fixed_source_id_2 = fixed_features[0][0], fixed_features[0][1]
            fixed_target_id_1, fixed_target_id_2 = fixed_features[1][0], fixed_features[1][1]
            # Create matching pairs from matching given features.
            pair_1 = source_features[fixed_source_id_1], target_features[fixed_target_id_1]
            pair_2 = source_features[fixed_source_id_2], target_features[fixed_target_id_2]
            # Get the transformation.
            transformation = get_horizontal_transformation_for_point_pairs(pair_1, pair_2)
            if transformation == None:
                print("Distance between the selected 2 source points and the paired 2 target points differs by more than 5%. They are likely not a correct match.")
                return None
            else:
                transformation_with_inliers = get_inliers_for_transformation(source_features, inlier_distance_threshold, target_tree, transformation)
                return transformation_with_inliers
        
        # If 1 match is given, run the transformatoin estimation with that point fixed.
        elif len(fixed_features[0]) == 1:
            print(f"Received 1 matching feature. Running semi-automatic registration.")
            # Get the fixed feature from both datasets.
            fixed_source_id, fixed_target_id = fixed_features[0][0], fixed_features[1][0]
            # Create matching pair.
            fixed_pair = source_features[fixed_source_id], target_features[fixed_target_id]
            # Create all possible combinations of the remaining source and target features.
            remaining_source_ids = [i for i in range(len(source_features)) if i != fixed_source_id]
            remaining_target_ids = [i for i in range(len(target_features)) if i != fixed_target_id]
            remaining_combinations = list(itertools.product(remaining_source_ids, remaining_target_ids))

            transformations_raw = []
            for (source_id), (target_id) in remaining_combinations:
                pair = (source_features[source_id], target_features[target_id])
                transformations_raw.append(get_horizontal_transformation_for_point_pairs(fixed_pair, pair))
            transformations = [result for result in transformations_raw if result is not None]

            transformations_with_inliers = []
            for candidate in transformations:
                transformations_with_inliers.append(get_inliers_for_transformation(source_features, inlier_distance_threshold, target_tree, candidate))
            best_transformation_with_inliers = max(transformations_with_inliers, key=lambda t: len(t["inliers"]))
            return best_transformation_with_inliers
            
            # # Prepare arguments for combining the fixed pair with all remaining pairs for parallel transformation.
            # transformation_args = []
            # for (source_id), (target_id) in remaining_combinations:
            #     pair = (source_features[source_id], target_features[target_id])
            #     transformation_args.append((fixed_pair, pair))
            # # Run all transformations in parallel.
            # with Pool() as pool:
            #     transformations_raw = pool.starmap(get_horizontal_transformation_for_point_pairs, transformation_args)
            # # Remove Nones from raw transformation results
            # transformations = [result for result in transformations_raw if result is not None]
            
            # # Prepare arguments to run the inlier funciton in parallel.
            # inlier_args = []
            # for transformation in transformations:
            #     inlier_args.append((source_features, inlier_distance_threshold, target_tree, transformation))
            # # Run inlier detection for all returned transformation results.
            # with Pool() as pool:
            #     transformations_with_inliers = pool.starmap(get_inliers_for_transformation, inlier_args)

            # best_transformation_with_inliers = max(transformations_with_inliers, key=lambda t: len(t["inliers"]))
            # return best_transformation_with_inliers
        
        # If no matches are manually give, run the transformation estimation for all possible combinations.
        else:
            print(f"Received no fixed features. Running fully automatic registration.")
            # Get all ids from the source and target features.
            all_source_ids = range(len(source_features))
            all_target_ids = range(len(target_features))
            # Create all possible combinations of 2 features within the source and target features.
            all_source_pairs = itertools.combinations(all_source_ids, 2)
            all_target_pairs = itertools.combinations(all_target_ids, 2)
            # Create all posible combinations of pairs between the source and target features.
            all_pair_combinations = itertools.product(all_source_pairs, all_target_pairs)

            transformations_raw = []
            for (source_id_1, source_id_2), (target_id_1, target_id_2) in all_pair_combinations:
                pair_1 = (source_features[source_id_1], target_features[target_id_1])
                pair_2 = (source_features[source_id_2], target_features[target_id_2])
                transformations_raw.append(get_horizontal_transformation_for_point_pairs(pair_1, pair_2))
            transformations = [result for result in transformations_raw if result is not None]

            transformations_with_inliers = []
            for candidate in transformations:
                transformations_with_inliers.append(get_inliers_for_transformation(source_features, inlier_distance_threshold, target_tree, candidate))
            best_transformation_with_inliers = max(transformations_with_inliers, key=lambda t: len(t["inliers"]))
            print(f"Rough Transformation: {best_transformation_with_inliers}")
            return best_transformation_with_inliers

            # # Prepare arguments for transformation from pairs parallel run.
            # transformation_args = []
            # for (source_id_1, source_id_2), (target_id_1, target_id_2) in all_pair_combinations:
            #     pair_1 = (source_features[source_id_1], target_features[target_id_1])
            #     pair_2 = (source_features[source_id_2], target_features[target_id_2])
            #     transformation_args.append((pair_1, pair_2))
            # # Run all transformations in parallel.
            # with Pool() as pool:
            #     transformations_raw = pool.starmap(get_horizontal_transformation_for_point_pairs, transformation_args)
            # # Remove Nones from raw transformation results
            # transformations = [result for result in transformations_raw if result is not None]

            # # Prepare arguments to run the inlier funciton in parallel.
            # inlier_args = []
            # for transformation in transformations:
            #     inlier_args.append((source_features, inlier_distance_threshold, target_tree, transformation))
            # # Run inlier detection for all returned transformation results.
            # with Pool() as pool:
            #     transformations_with_inliers = pool.starmap(get_inliers_for_transformation, inlier_args)

            # best_transformation_with_inliers = max(transformations_with_inliers, key=lambda t: len(t["inliers"]))
            # return best_transformation_with_inliers
        
    except Exception as e:
        print(f"An error occurred estimating the rough horizontal registration: {e}")
        print(traceback.format_exc())
        return
        
        

def refine_horizontal_registration(source_features: np.ndarray, target_features: np.ndarray, rough_transformation: dict) -> dict:
    """
    Refines the best estimated transformation using least squares optimization (Kabsch algorithm).
    Source: https://hunterheidenreich.com/posts/kabsch_algorithm/
    
    @param source_features: Source features before applying the rough registration.
    @param target_features: Target features.
    @param rough_transformation: Estimated registration transformation.
    @return: Dictionary containing the refined translation and rotation.
    """
    try:
        inlier_pairs = rough_transformation["inliers"]
        # If only 1 inlier, rotation can't be refined.
        if not inlier_pairs or len(inlier_pairs) < 2:
            print(f"Not enough inliers for refinement using least squares. Returning rough transformation.")
            return rough_transformation
        
        # Apply rough transformation o source features.
        roughly_registered_source_features = translate_points(rotate_points(source_features, rough_transformation["rotation_center"], rough_transformation["rotation_angle"]), rough_transformation["translation"])

        # Extract source and target points from inlier pairs.
        source_inliers = np.array([roughly_registered_source_features[i[0]] for i in inlier_pairs])
        target_inliers = np.array([target_features[i[1]] for i in inlier_pairs])
        # Translate both sets to origin by the common rotation center.
        source_centroid = np.mean(source_inliers, axis=0)
        target_centroid = np.mean(target_inliers, axis=0)
        source_inliers_centered = source_inliers - source_centroid
        target_inliers_centered = target_inliers - target_centroid

        # Translation adjustment by centroids
        translation = rough_transformation["translation"] + target_centroid - source_centroid

        # Compute the cross-variance matrix.
        H = source_inliers_centered.T @ target_inliers_centered
        # Compute the Single value decomposition of H.
        U, S, Vt = np.linalg.svd(H)
        R = Vt.T @ U.T

        # Ensure proper rotation
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = Vt.T @ U.T

        # Extract the rotation angle.
        rotation_angle = rough_transformation["rotation_angle"] + np.arctan2(R[1,0], R[0,0])

        refined_transformation = {"rotation_angle": rotation_angle, "rotation_center": rough_transformation["rotation_center"], "translation": translation}
        print(f"Refined Transformation: {refined_transformation}")
        return refined_transformation

    except Exception as e:
        print(f"An error occurred refining the horizontal registration: {e}")
        print(traceback.format_exc())        
        return