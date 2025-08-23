import streamlit as st
import os, sys
from shapely.geometry import MultiPolygon
import plotly.graph_objects as go
import numpy as np
import shutil

def init_session_state():
    # Persistant file path
    file_path = "./test_data/streamlit/files/"
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    output_path = "./test_data/output"
    if not os.path.exists(output_path):
        os.makedirs(output_path)


    # Models
    if "citygml_model" not in st.session_state:
        st.session_state.citygml_model = None

    if "ifc_model" not in st.session_state:
        st.session_state.ifc_model = None

    if "dxf_model" not in st.session_state:
        st.session_state.dxf_model = None


    # Footprints
    if "citygml_footprint" not in st.session_state:
        st.session_state.citygml_footprint = MultiPolygon()
    if "citygml_building_ids_all" not in st.session_state:
        st.session_state.citygml_building_ids_all = []
    if "citygml_building_ids_selected" not in st.session_state:
        st.session_state.citygml_building_ids_selected = []

    if "ifc_footprint" not in st.session_state:
        st.session_state.ifc_footprint = MultiPolygon()
    if "ifc_types_all" not in st.session_state:
        st.session_state.ifc_types_all = []
    if "ifc_types_selected" not in st.session_state:
        st.session_state.ifc_types_selected = []
    if "ifc_building_stories_all" not in st.session_state:
        st.session_state.ifc_building_stories_all = []
    if "ifc_building_stories_selected" not in st.session_state:
        st.session_state.ifc_building_stories_selected = []
    if "ifc_footprint_detailed" not in st.session_state:
        st.session_state.ifc_footprint_detailed = False  

    if "dxf_footprint" not in st.session_state:
        st.session_state.dxf_footprint = MultiPolygon()
    if "dxf_layers_all" not in st.session_state:
        st.session_state.dxf_layers_all = []
    if "dxf_layers_selected" not in st.session_state:
        st.session_state.dxf_layers_selected = []
    if "dxf_footprint_detailed" not in st.session_state:
        st.session_state.dxf_footprint_detailed = False

    
    # Features
    if "citygml_features_angle_threshold" not in st.session_state:
        st.session_state.citygml_features_angle_threshold = 0.1
    if "citygml_features_area_threshold" not in st.session_state:
        st.session_state.citygml_features_area_threshold = 30.0
    if "citygml_features_raw" not in st.session_state:
        st.session_state.citygml_features_raw = []
    if "citygml_features_filtered" not in st.session_state:
        st.session_state.citygml_features_filtered = []

    if "ifc_features_angle_threshold" not in st.session_state:
        st.session_state.ifc_features_angle_threshold = 0.1
    if "ifc_features_area_threshold" not in st.session_state:
        st.session_state.ifc_features_area_threshold = 30.0
    if "ifc_features_raw" not in st.session_state:
        st.session_state.ifc_features_raw = []
    if "ifc_features_filtered" not in st.session_state:
        st.session_state.ifc_features_filtered = []

    if "dxf_features_angle_threshold" not in st.session_state:
        st.session_state.dxf_features_angle_threshold = 0.1
    if "dxf_features_area_threshold" not in st.session_state:
        st.session_state.dxf_features_area_threshold = 30.0
    if "dxf_features_raw" not in st.session_state:
        st.session_state.dxf_features_raw = []
    if "dxf_features_filtered" not in st.session_state:
        st.session_state.dxf_features_filtered = []


    # Horizontal Registration
    if "citygml_rotational_symmetry_angles" not in st.session_state:
        st.session_state.citygml_rotational_symmetry_angles = []
    if "ifc_rotational_symmetry_angles" not in st.session_state:
        st.session_state.ifc_rotational_symmetry_angles = []
    if "dxf_rotational_symmetry_angles" not in st.session_state:
        st.session_state.dxf_rotational_symmetry_angles = []

    if "citygml_matching_features_ifc" not in st.session_state:
        st.session_state.citygml_matching_features_ifc = []
    if "citygml_matching_features_dxf" not in st.session_state:
        st.session_state.citygml_matching_features_dxf = []
    if "ifc_matching_features_citygml" not in st.session_state:
        st.session_state.ifc_matching_features_citygml = []
    if "ifc_matching_features_dxf" not in st.session_state:
        st.session_state.ifc_matching_features_dxf = []
    if "dxf_matching_features_citygml" not in st.session_state:
        st.session_state.dxf_matching_features_citygml = []
    if "dxf_matching_features_ifc" not in st.session_state:
        st.session_state.dxf_matching_features_ifc = []

    if "ifc_transformation_dxf" not in st.session_state:
        st.session_state.ifc_transformation_dxf = {}
    if "ifc_transformation_citygml" not in st.session_state:
        st.session_state.ifc_transformation_citygml = {}
    if "dxf_transformation_citygml" not in st.session_state:
        st.session_state.dxf_transformation_citygml = {}

    if "current_horizontal_registration" not in st.session_state:
        st.session_state.current_horizontal_registration = None

    if "dxf_features_filtered_transformed" not in st.session_state:
        st.session_state.dxf_features_filtered_transformed = []
    if "dxf_footprint_transformed" not in st.session_state:
        st.session_state.dxf_footprint_transformed = MultiPolygon()
    if "ifc_footprint_transformed_to_citygml" not in st.session_state:
        st.session_state.ifc_footprint_transformed_to_citygml = MultiPolygon()
    if "ifc_footprint_transformed_to_dxf" not in st.session_state:
        st.session_state.ifc_footprint_transformed_to_dxf = MultiPolygon()

    if "horizontal_transformation" not in st.session_state:
        st.session_state.horizontal_transformation = {}
    if "ifc_footprint_horizontally_transformed" not in st.session_state:
        st.session_state.ifc_footprint_horizontally_transformed = MultiPolygon()
    if "ifc_model_horizontally_transformed" not in st.session_state:
        st.session_state.ifc_model_horizontally_transformed = None


    # Vertical Registration
    if "citygml_sideview" not in st.session_state:
        st.session_state.citygml_sideview = MultiPolygon()
    if "ifc_sideview" not in st.session_state:
        st.session_state.ifc_sideview = MultiPolygon()
    if "citygml_z_extent" not in st.session_state:
        st.session_state.citygml_z_extent = None
    if "ifc_z_extent" not in st.session_state:
        st.session_state.ifc_z_extent = None
    if "citygml_windows" not in st.session_state:
        st.session_state.citygml_windows = None
    if "ifc_windows" not in st.session_state:
        st.session_state.ifc_windows = None

    if "terrain_level" not in st.session_state:
        st.session_state.terrain_level = 0
    if "ifc_story_mapping_story_id" not in st.session_state:
        st.session_state.ifc_story_mapping_story_id = None
    if "ifc_story_mapping_story_number" not in st.session_state:
        st.session_state.ifc_story_mapping_story_number = None
    if "manual_elevation" not in st.session_state:
        st.session_state.manual_elevation = None
    if "lod2_transformation" not in st.session_state:
        st.session_state.lod2_transformation = {}
    if "lod3_transformation" not in st.session_state:
        st.session_state.lod3_transformation = {}
    if "z_extent_is_similar" not in st.session_state:
        st.session_state.z_extent_is_similar = False

    if "final_transformation" not in st.session_state:
        st.session_state.final_transformation = {}
    if "ifc_model_vertically_transformed" not in st.session_state:
        st.session_state.ifc_model_vertically_transformed = None



def plot(footprints=[], features_raw=[], features_filtered=[], key="", features_selected_1=[], features_selected_2=[], feat_sel_label_1="", feat_sel_label_2="", feat_sel_label_1_and_2="", terrain_level=None):

    fig = go.Figure()

    fig.update_layout(
    yaxis=dict(scaleanchor="x", scaleratio=1, showgrid=False),
    )

    if terrain_level:
        fig.add_hline(y=terrain_level, line_color="brown", annotation_text=f"Terrain: {terrain_level}")

    if type(footprints) == MultiPolygon:
        footprints = [footprints]
    footprint_colors = ["gray", "rgb(255,200,0)", "rgb(255,50,0)", "rgb(255,0,0)"]
    for i, footprint in enumerate(footprints):
        color = footprint_colors[i] if i < len(footprint_colors) else "gray"
        for poly in footprint.geoms:
            x, y = poly.exterior.xy
            fig.add_trace(go.Scatter(x=list(x), y=list(y), mode="lines", line_color=color, opacity=0.6, showlegend=False))

    features_raw_x = []
    features_raw_y = []
    for features in features_raw:
        for feature in features:
            features_raw_x.append(feature[0])
            features_raw_y.append(feature[1])
    fig.add_trace(go.Scatter(x=features_raw_x, y=features_raw_y, mode="markers", marker_color="rgb(50,255,100)", opacity=0.3, showlegend=False))

    features_filtered_x = []
    features_filtered_y = []
    features_filtered_selected_1_x = []
    features_filtered_selected_1_y = []
    features_filtered_selected_2_x = []
    features_filtered_selected_2_y = []
    features_filtered_selected_both_x = []
    features_filtered_selected_both_y = []
    features_filtered_index = []
    for index, feature in enumerate(features_filtered):
        features_filtered_index.append(index)
        if index in features_selected_1:
            if index in features_selected_2:
                features_filtered_selected_both_x.append(feature[0])
                features_filtered_selected_both_y.append(feature[1])
            else:
                features_filtered_selected_1_x.append(feature[0])
                features_filtered_selected_1_y.append(feature[1])
        elif index in features_selected_2:
            features_filtered_selected_2_x.append(feature[0])
            features_filtered_selected_2_y.append(feature[1])
        features_filtered_x.append(feature[0])
        features_filtered_y.append(feature[1])
    fig.add_trace(go.Scatter(x=features_filtered_x, y=features_filtered_y, mode="markers", marker_color="rgb(50,255,100)", opacity=0.9, showlegend=False, customdata=features_filtered_index, hovertemplate="Feature Index: %{customdata}"))
    fig.add_trace(go.Scatter(x=features_filtered_selected_1_x, y=features_filtered_selected_1_y, mode="markers", marker_color="rgb(255,50,50)", opacity=0.9, name=feat_sel_label_1))
    fig.add_trace(go.Scatter(x=features_filtered_selected_2_x, y=features_filtered_selected_2_y, mode="markers", marker_color="rgb(50,140,255)", opacity=0.9, name=feat_sel_label_2))
    fig.add_trace(go.Scatter(x=features_filtered_selected_both_x, y=features_filtered_selected_both_y, mode="markers", marker_color="rgb(220,60,255)", opacity=0.9, name=feat_sel_label_1_and_2))

    return st.plotly_chart(figure_or_data=fig, key=key)


def clear_session_state():
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]
    shutil.rmtree("./test_data/streamlit/")
    init_session_state()