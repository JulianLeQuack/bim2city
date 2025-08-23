import streamlit as st
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from source.transformation_horizontal.footprint_creation.create_citygml_footprint import create_citygml_footprint, get_citygml_building_ids
from source.transformation_horizontal.footprint_creation.create_ifc_footprint import create_ifc_footprint, get_building_stories, get_ifc_classes
from source.transformation_horizontal.footprint_creation.create_dxf_footprint import create_dxf_footprint, extract_dxf_layers

st.set_page_config(
    page_title="bim2city",
    page_icon="./images/bim2city_logo.png",
    layout="wide"
)
st.title("Footprint Creation")

from Utilities import init_session_state, plot
init_session_state()

file_path = "./test_data/streamlit/files/"

col_citygml, col_ifc, col_dxf = st.columns(3)


# CityGML Column
with col_citygml:
    st.subheader("CityGML Footprint")

    if st.session_state.citygml_model is None:
        st.warning("Upload a CityGML model first.")
    else:
        plot(footprints=st.session_state.citygml_footprint, key="citygml_footprint_plot")
        st.session_state.citygml_building_ids_all = get_citygml_building_ids(st.session_state.citygml_model)
        st.session_state.citygml_building_ids_selected = st.multiselect(
            "Select CityGML building IDs.",
            options=st.session_state.citygml_building_ids_all,
            default=st.session_state.citygml_building_ids_selected
        )

        if st.button("Create CityGML Footprint"):
            st.session_state.citygml_footprint = create_citygml_footprint(st.session_state.citygml_model, st.session_state.citygml_building_ids_selected)
            st.rerun()
        st.info(f"Selected CityGML building IDs: {st.session_state.citygml_building_ids_selected}")


# IFC Column
with col_ifc:
    st.subheader("IFC Footprint")

    if st.session_state.ifc_model is None:
        st.warning("Upload an IFC model first.")
    else:
        plot(footprints=st.session_state.ifc_footprint, key="ifc_footprint_plot")
        st.session_state.ifc_types_all = get_ifc_classes(st.session_state.ifc_model)
        st.session_state.ifc_types_selected = st.multiselect(
            "Select IFC types.",
            options=st.session_state.ifc_types_all,
            default=st.session_state.ifc_types_selected
        )
        st.session_state.ifc_building_stories_all = get_building_stories(st.session_state.ifc_model)
        st.session_state.ifc_building_stories_selected = st.multiselect(
            "Select IFC building stories.",
            options=st.session_state.ifc_building_stories_all,
            default=st.session_state.ifc_building_stories_selected
        )

        st.session_state.ifc_footprint_detailed = st.checkbox(
            "Detailed IFC fooprint",
            value=st.session_state.ifc_footprint_detailed
        )

        if st.button("Create IFC Footprint"):
            st.session_state.ifc_footprint = create_ifc_footprint(st.session_state.ifc_model, st.session_state.ifc_types_selected, st.session_state.ifc_building_stories_selected, st.session_state.ifc_footprint_detailed)
            st.rerun()
        st.info(f"Selected IFC types: {st.session_state.ifc_types_selected}")
        st.info(f"Selected IFC building stories: {st.session_state.ifc_building_stories_selected}")


# DXF Column
with col_dxf:
    st.subheader("DXF Footprint (Optional)")

    if st.session_state.dxf_model is None:
        st.warning("Upload a DXF model first.")
    else:
        plot(footprints=st.session_state.dxf_footprint, key="dxf_footprint_plot")
        st.session_state.dxf_layers_all = extract_dxf_layers(st.session_state.dxf_model)
        st.session_state.dxf_layers_selected = st.multiselect(
            "Select DXF layers.",
            options=st.session_state.dxf_layers_all,
            default=st.session_state.dxf_layers_selected
        )

        st.session_state.dxf_footprint_detailed = st.checkbox(
            "Detailed DXF footprint",
            value=st.session_state.dxf_footprint_detailed
        )

        if st.button("Create DXF Footprint"):
            st.session_state.dxf_footprint = create_dxf_footprint(st.session_state.dxf_model, st.session_state.dxf_layers_selected, st.session_state.dxf_footprint_detailed)
            st.rerun()
        st.info(f"Selected DXF layers: {st.session_state.dxf_layers_selected}")