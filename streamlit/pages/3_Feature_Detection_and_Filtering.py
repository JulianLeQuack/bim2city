import streamlit as st
import os, sys
import numpy as np

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from source.transformation_horizontal.horizontal_registration.detect_and_filter_footprint_features import detect_footprint_features, filter_footprint_features

st.set_page_config(
    page_title="bim2city",
    page_icon="./images/bim2city_logo.png",
    layout="wide"
)
st.title("Feature Detection and Filtering")

from Utilities import init_session_state, plot
init_session_state()

file_path = "./test_data/streamlit/files/"

col_citygml, col_ifc, col_dxf = st.columns(3)


#CityGML Column
with col_citygml:
    st.subheader("CityGML Features")

    if st.session_state.citygml_model is None:
        st.warning("Upload a CityGML model first.")
    else:
        plot(footprints=st.session_state.citygml_footprint, features_raw=st.session_state.citygml_features_raw, features_filtered=st.session_state.citygml_features_filtered, key="citygml_features_plot")
        st.session_state.citygml_features_angle_threshold = st.number_input(
            "Input CityGML angle threshold.",
            min_value=0.1,
            max_value=np.pi - 0.1,
            value=st.session_state.citygml_features_angle_threshold
        )
        
        st.session_state.citygml_features_area_threshold = st.number_input(
            "Input CityGML area threshold.",
            min_value=0.0,
            max_value=500.0,
            value=st.session_state.citygml_features_area_threshold
        )
        
        if st.button("Detect and Filter CityGML Features"):
            st.session_state.citygml_features_raw = detect_footprint_features(st.session_state.citygml_footprint, st.session_state.citygml_features_angle_threshold)
            st.session_state.citygml_features_filtered = filter_footprint_features(st.session_state.citygml_features_raw, st.session_state.citygml_features_area_threshold)
            st.rerun()
        st.info(f"Number of features: {len(st.session_state.citygml_features_filtered)}")


#IFC Column
with col_ifc:
    st.subheader("IFC Features")

    if st.session_state.ifc_model is None:
        st.warning("Upload an IFC model first.")
    else:
        plot(footprints=st.session_state.ifc_footprint, features_raw=st.session_state.ifc_features_raw, features_filtered=st.session_state.ifc_features_filtered, key="ifc_features_plot")
        st.session_state.ifc_features_angle_threshold = st.number_input(
            "Input IFC angle threshold.",
            min_value=0.1,
            max_value=np.pi - 0.1,
            value=st.session_state.ifc_features_angle_threshold
        )
        
        st.session_state.ifc_features_area_threshold = st.number_input(
            "Input IFC area threshold.",
            min_value=0.0,
            max_value=500.0,
            value=st.session_state.ifc_features_area_threshold
        )
        
        if st.button("Detect and Filter IFC Features"):
            st.session_state.ifc_features_raw = detect_footprint_features(st.session_state.ifc_footprint, st.session_state.ifc_features_angle_threshold)
            st.session_state.ifc_features_filtered = filter_footprint_features(st.session_state.ifc_features_raw, st.session_state.ifc_features_area_threshold)
            st.rerun()        
        st.info(f"Number of features: {len(st.session_state.ifc_features_filtered)}")


#DXF Column
with col_dxf:
    st.subheader("DXF Features (Optional)")

    if st.session_state.dxf_model is None:
        st.warning("Upload a DXF model first.")
    else:
        plot(footprints=st.session_state.dxf_footprint, features_raw=st.session_state.dxf_features_raw, features_filtered=st.session_state.dxf_features_filtered, key="dxf_features_plot")
        st.session_state.dxf_features_angle_threshold = st.number_input(
            "Input DXF angle threshold.",
            min_value=0.1,
            max_value=np.pi - 0.1,
            value=st.session_state.dxf_features_angle_threshold
        )
        
        st.session_state.dxf_features_area_threshold = st.number_input(
            "Input DXF area threshold.",
            min_value=0.0,
            max_value=500.0,
            value=st.session_state.dxf_features_area_threshold
        )
        
        if st.button("Detect and Filter DXF Features"):
            st.session_state.dxf_features_raw = detect_footprint_features(st.session_state.dxf_footprint, st.session_state.dxf_features_angle_threshold)
            st.session_state.dxf_features_filtered = filter_footprint_features(st.session_state.dxf_features_raw, st.session_state.dxf_features_area_threshold)
            st.rerun()
        st.info(f"Number of features: {len(st.session_state.dxf_features_filtered)}")