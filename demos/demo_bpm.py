from source.geometry_helpers.geometry_helpers import *
from source.transformation_horizontal.footprint_creation.create_citygml_footprint import *
from source.transformation_horizontal.footprint_creation.create_ifc_footprint import *
from source.transformation_horizontal.footprint_creation.create_dxf_footprint import *
from source.transformation_horizontal.horizontal_registration.check_rotation_symmetry import *
from source.transformation_horizontal.horizontal_registration.detect_and_filter_footprint_features import *
from source.transformation_horizontal.horizontal_registration.estimate_horizontal_transformation import *
from source.transformation_vertical.vertical_registration.estimate_vertical_registration import *

import matplotlib.pyplot as plt
import ifcpatch
import copy


# plotting
def plot_multipolygon(footprint, title):
    plt.figure(figsize=(8, 8))
    if type(footprint) == MultiPolygon:
        for poly in footprint.geoms:
            x, y = poly.exterior.xy
            plt.plot(x, y, linewidth=2)
    else:
        for mp in footprint:
            for poly in mp.geoms:
                x, y = poly.exterior.xy
                plt.plot(x, y, linewidth=2)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title(title)
    plt.show()
    plt.close()

def plot_points(points, title, highlights=[]):
    plt.figure(figsize=(8,8))
    x = [point[0] for point in points]
    y = [point[1] for point in points]
    plt.scatter(x, y, color="red")
    for point_id, point  in enumerate(points):
        if point_id in highlights:
            plt.scatter(point[0], point[1], color="green")
    for i in range(len(points)):
        plt.text(x[i], y[i], str(i))
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title(title)
    plt.show()
    plt.close()


# input paths
citygml_path = "./test_data/citygml/DEBY_LOD3_4959457.gml"
citygml_building_ids = ["DEBY_LOD2_4959457"]

# ifc_path = "./test_data/ifc/bpm/F2.ifc"
# ifc_types = ["IfcWall", "IfcWallStandardCase"]
# ifc_building_stories = ["2ogdg1D3v9OuoD2lPrUfdK"]

ifc_path = "./test_data/ifc/bpm/F3.ifc"
ifc_types = ["IfcWall", "IfcWallStandardCase"]
ifc_building_stories = ["2ogdg1D3v9OuoD2lPrUfdK"]

# dxf_path = "./test_data/dxf/01-05-0501_2.OG.dxf"
# dxf_layer_names = ["A_01_TRAGWAND"]

dxf_path = "./test_data/dxf/01-05-0501_3.OG.dxf"
dxf_layer_names = ["A_01_TRAGWAND"]



# footprint creation
citygml_model = parse_citygml_file(citygml_path)
citygml_footprint = create_citygml_footprint(citygml_model, citygml_building_ids)
plot_multipolygon(citygml_footprint, title="CityGML Footprint")

ifc_model = parse_ifc_file(ifc_path)
ifc_footprint = create_ifc_footprint(ifc_model, ifc_types, ifc_building_stories, True)
plot_multipolygon(ifc_footprint, title="IFC Footprint")

dxf_model = parse_dxf_file(dxf_path)
dxf_footprint_rough = create_dxf_footprint(dxf_model, dxf_layer_names, False)
dxf_footprint_detailed = create_dxf_footprint(dxf_model, dxf_layer_names, True)
plot_multipolygon(dxf_footprint_rough, title="DXF Footprint Rough")
plot_multipolygon(dxf_footprint_detailed, title="DXF Footprint Detailed")



# feature detection and filering
citygml_features_raw = detect_footprint_features(citygml_footprint)
citygml_features = filter_footprint_features(citygml_features_raw, 10)

ifc_features_raw = detect_footprint_features(ifc_footprint)
ifc_features = filter_footprint_features(ifc_features_raw, 1)

dxf_features_rough_raw = detect_footprint_features(dxf_footprint_rough)
dxf_features_rough = filter_footprint_features(dxf_features_rough_raw, 10)

dxf_features_detailed_raw = detect_footprint_features(dxf_footprint_detailed)
dxf_features_detailed = filter_footprint_features(dxf_features_detailed_raw, 1)



# check for symmetry
citygml_rotation_symmetry_angles = check_rotational_symmetry(citygml_footprint)
ifc_rotation_symmetry_angles = check_rotational_symmetry(ifc_footprint)
dxf_rough_rotation_symmetry_angles = check_rotational_symmetry(dxf_footprint_rough)
dxf_detailed_rotation_symmetry_angles = check_rotational_symmetry(dxf_footprint_detailed)

print(f"Results of rotation symmetry checking. If a risk of rotation symmetry is detected, the rotation angle is returned:\nCityGML Features: {citygml_rotation_symmetry_angles}\nIFC Features: {ifc_rotation_symmetry_angles}\nDXF Rough Features: {dxf_rough_rotation_symmetry_angles}\nDXF Detailed Features: {dxf_detailed_rotation_symmetry_angles}")
plot_points(citygml_features, title="CityGML Features")
plot_points(ifc_features, title="IFC Features")
plot_points(dxf_features_rough, title="DXF Rough Features")
plot_points(dxf_features_detailed, title="DXF Detailed Features")



# manual hints for rotation symmetric footprint registration
dxf_rough_match = [[0],[21]]
dxf_detailed_match = [[4,171],[21,40]]

print(f"Manual matches for registration: DXF Detailed to Citygml: {dxf_detailed_match}")
plot_points(citygml_features, title="CityGML Detailed Manual Match", highlights=[dxf_detailed_match[0][1], dxf_detailed_match[1][1]])
plot_points(dxf_features_rough, title="DXF Rough Manual Match", highlights=[dxf_rough_match[0][0]])
plot_points(dxf_features_detailed, title="DXF Detailed Manual Match", highlights=[dxf_detailed_match[0][0], dxf_detailed_match[1][0]])



# Registration Estimation
transformation_dxf_to_citygml_rough_rough = estimate_rough_horizontal_registration(dxf_features_rough, citygml_features, fixed_features=dxf_rough_match)
print(f"DXF to CityGML Rough: {transformation_dxf_to_citygml_rough_rough}")
transformation_dxf_to_citygml_rough_refined = refine_horizontal_registration(dxf_features_rough, citygml_features, transformation_dxf_to_citygml_rough_rough)
print(f"DXF to CityGML Refined: {transformation_dxf_to_citygml_rough_refined}")

dxf_rough_registered = translate_multipolygon(
    rotate_multipolygon(dxf_footprint_rough,
                        transformation_dxf_to_citygml_rough_refined["rotation_center"],
                        transformation_dxf_to_citygml_rough_refined["rotation_angle"]),
                        transformation_dxf_to_citygml_rough_refined["translation"])
plot_multipolygon([citygml_footprint, dxf_rough_registered], title="DXF Rough Registered with CityGML")

transformation_dxf_to_citygml_detailed_rough = estimate_rough_horizontal_registration(dxf_features_detailed, citygml_features, fixed_features=dxf_detailed_match)
print(f"DXF to CityGML Rough: {transformation_dxf_to_citygml_detailed_rough}")
transformation_dxf_to_citygml_detailed_refined = refine_horizontal_registration(dxf_features_detailed, citygml_features, transformation_dxf_to_citygml_detailed_rough)
print(f"DXF to CityGML Refined: {transformation_dxf_to_citygml_detailed_refined}")

dxf_detailed_registered = translate_multipolygon(
    rotate_multipolygon(dxf_footprint_detailed,
                        transformation_dxf_to_citygml_detailed_refined["rotation_center"],
                        transformation_dxf_to_citygml_detailed_refined["rotation_angle"]),
                        transformation_dxf_to_citygml_detailed_refined["translation"])
plot_multipolygon([citygml_footprint, dxf_detailed_registered], title="DXF Detailed Registered with CityGML")



# Transform dxf detailed features for registration with bpm
dxf_features_detailed_transformed = translate_points(
    rotate_points(dxf_features_detailed,
                        transformation_dxf_to_citygml_detailed_refined["rotation_center"],
                        transformation_dxf_to_citygml_detailed_refined["rotation_angle"]),
                        transformation_dxf_to_citygml_detailed_refined["translation"])

# Estimate BPM registration
transformation_ifc_to_dxf_rough = estimate_rough_horizontal_registration(ifc_features, dxf_features_detailed_transformed)
transformation_ifc_to_dxf_refined = refine_horizontal_registration(ifc_features, dxf_features_detailed_transformed, transformation_ifc_to_dxf_rough)

# Apply registration to ifc footprint
ifc_footprint_hor_registered_rough = translate_multipolygon(
    rotate_multipolygon(ifc_footprint,
                        transformation_ifc_to_dxf_rough["rotation_center"],
                        transformation_ifc_to_dxf_rough["rotation_angle"]),
                        transformation_ifc_to_dxf_rough["translation"])
plot_multipolygon([citygml_footprint, ifc_footprint_hor_registered_rough], title="IFC Roughly Registered with CityGML")

# Apply registration to ifc footprint
ifc_footprint_hor_registered = translate_multipolygon(
    rotate_multipolygon(ifc_footprint,
                        transformation_ifc_to_dxf_refined["rotation_center"],
                        transformation_ifc_to_dxf_refined["rotation_angle"]),
                        transformation_ifc_to_dxf_refined["translation"])
plot_multipolygon([citygml_footprint, ifc_footprint_hor_registered], title="IFC Registered with CityGML")

print(f"IFC to CityGML:\n{transformation_ifc_to_dxf_rough}\n{transformation_ifc_to_dxf_refined}")

ifc_model_horizontally_transformed = transform_ifc(ifc_model, transformation_ifc_to_dxf_refined)
ifc_model_horizontally_transformed.write("./test_data/ifc/F3_hor_transformed.ifc")

# # Vertical registration

story_mapping = {
    "story_id": "2ogdg1D3v9OuoD2lPrUfdK",
    "story_number": 3
}
vertical_offset_estimation = estimate_vertical_registration(citygml_model, citygml_building_ids, ifc_model_horizontally_transformed, story_mapping, ifc_footprint_hor_registered)

final_transformation = {
    "rotation_angle": transformation_ifc_to_dxf_refined["rotation_angle"],
    "rotation_center": transformation_ifc_to_dxf_refined["rotation_center"],
    "translation": [
        transformation_ifc_to_dxf_refined["translation"][0],
        transformation_ifc_to_dxf_refined["translation"][1],
        vertical_offset_estimation
    ]
}
print(f"Final transformation for IFC: {final_transformation}")

ifc_model = parse_ifc_file(ifc_path)

# Apply transformation to IFC model.
ifc_model_transformed = transform_ifc(ifc_model, final_transformation)
ifc_model_transformed.write("./test_data/ifc/F3_transformed.ifc")