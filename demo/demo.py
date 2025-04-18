# Footprint Creation Imports
from source.transformation_horizontal.create_footprints.create_CityGML_footprint import create_CityGML_footprint
from source.transformation_horizontal.create_footprints.create_IFC_footprint_polygon import create_IFC_footprint_polygon
from source.transformation_horizontal.create_footprints.create_DXF_footprint_polygon import create_DXF_footprint_polygon

# Horizontal Registration Imports
from source.transformation_horizontal.rigid_transformation import Rigid_Transformation
from source.transformation_horizontal.estimate_rigid_transformation import estimate_rigid_transformation, refine_rigid_transformation
from source.transformation_horizontal.detect_features import detect_features, filter_features_by_feature_triangle_area

# Vertical Registration Imports
from source.transformation_vertical.extract_elevation_labels import extract_elevation_labels


# Input Data Paths
ifc_path = "./demo/data/3.002 01-05-0501_EG.ifc"
dxf_path = "./demo/data/01-05-0501_EG.dxf"
dxf_path_point_symmetric = "./demo/data/01-05-0507_EG.1.dxf"
citygml_path = "./demo/data/DEBY_LOD2_4959457.gml"
data_path = "./demo/data/"

# Model footprint settings
citygml_building_ids = ["DEBY_LOD2_4959457"]
ifc_type = "IfcSlab"
dxf_layer = "A_09_TRAGDECKE"

# Create Footprints
print("Creating Footprints...")
ifc_footprint = create_IFC_footprint_polygon(ifc_path=ifc_path, ifc_type=ifc_type)
dxf_footprint = create_DXF_footprint_polygon(dxf_path=dxf_path, layer_name=dxf_layer)
citygml_footprint = create_CityGML_footprint(citygml_path=citygml_path, building_ids=citygml_building_ids)

# Extract Features using Turning Function for detecting corners in footprints
print("Extracting Features...")
ifc_features = detect_features(footprint=ifc_footprint, angle_threshold_deg=30)
dxf_features = detect_features(footprint=dxf_footprint, angle_threshold_deg=30)
citygml_features = detect_features(footprint=citygml_footprint, angle_threshold_deg=30)

# Filter features by eliminating featrues that span up small triangles with adjacent features to only keep significant features
print("Filtering Features...")
ifc_features_filtered = filter_features_by_feature_triangle_area(features=ifc_features, min_area=15)
dxf_features_filtered = filter_features_by_feature_triangle_area(features=dxf_features, min_area=15)
citygml_features_filtered = filter_features_by_feature_triangle_area(features=citygml_features, min_area=15)

# Estimate Rigid Transformation for IFC to CityGML
print("Estimating Rigid Transformation for IFC Footprint...")
rough_transformation_ifc_to_citygml, inlier_pairs_ifc_to_citygml = estimate_rigid_transformation(source_features=ifc_features_filtered, target_features=citygml_features_filtered, distance_tol=1, angle_tol_deg=45)
refined_transformation_ifc_to_citygml = refine_rigid_transformation(inlier_pairs=inlier_pairs_ifc_to_citygml)
print(f"Transformation for IFC to CityGML: {refined_transformation_ifc_to_citygml}")

# Transformation of IFC footprint to CityGML footprint and Feature Extraction
print("Transforming IFC Footprint to CityGML Footprint...")
ifc_footprint_transformed = refined_transformation_ifc_to_citygml.transform_shapely_polygon(ifc_footprint)
ifc_features_transformed = detect_features(footprint=ifc_footprint_transformed, angle_threshold_deg=30)
ifc_features_transformed_filtered = filter_features_by_feature_triangle_area(features=ifc_features_transformed, min_area=15)

# Estimate Rigid Transformation for DXF to IFC
print("Estimating Rigid Transformation for DXF Footprint...")
rough_transformation_dxf_to_ifc, inlier_pairs_dxf_to_ifc = estimate_rigid_transformation(source_features=dxf_features_filtered, target_features=ifc_features_transformed_filtered, distance_tol=1, angle_tol_deg=45)
refined_transformation_dxf_to_ifc = refine_rigid_transformation(inlier_pairs=inlier_pairs_dxf_to_ifc)
print(f"Transformation for DXF to CityGML: {refined_transformation_dxf_to_ifc}")

# Save the transformations to JSON files
print("Saving Transformations to JSON...")
refined_transformation_dxf_to_ifc.export_to_json(data_path + "transformation_dxf_to_citygml.json")
refined_transformation_ifc_to_citygml.export_to_json(data_path + "transformation_ifc_to_citygml.json")




## Vertical Registration

# Extract elevation labels from DXF
print("Extracting Elevation Labels from DXF...")
elevation_labels_dxf = extract_elevation_labels(dxf_path=dxf_path, layer_name=dxf_layer)
transformed_elevation_labels_dxf = refined_transformation_dxf_to_ifc.transform_elevation_labels(elevation_labels=elevation_labels_dxf)

# Apply the transformations to the DXF and IFC files
print("Applying Transformations to DXF and IFC files...")
transformed_ifc_file = refined_transformation_ifc_to_citygml.transform_ifc(input_ifc_path=ifc_path, output_ifc_path=data_path + "transformed_ifc.ifc")