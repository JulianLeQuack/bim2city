import streamlit as st
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from source.transformation_horizontal.footprint_creation.create_citygml_footprint import parse_citygml_file
from source.transformation_horizontal.footprint_creation.create_ifc_footprint import parse_ifc_file
from source.transformation_horizontal.footprint_creation.create_dxf_footprint import parse_dxf_file

st.set_page_config(
    page_title="bim2city",
    page_icon="./images/bim2city_logo.png",
    layout="wide"
)
st.title("File Import")

from Utilities import init_session_state, clear_session_state
init_session_state()

file_path = "./test_data/streamlit/files/"

if st.button("Clear Session State"):
    clear_session_state()

col_citygml, col_ifc, col_dxf = st.columns(3)


# Citygml Column
with col_citygml:
    st.subheader("CityGML Model")

    citygml_file = st.file_uploader(label="Upload CityGML file.", type=["gml"], key="citygml_uploader")
    if citygml_file is not None:
        with open(file_path + "citygml_file.gml", "wb") as f:
            f.write(citygml_file.read())
        st.session_state.citygml_model = parse_citygml_file(file_path + "citygml_file.gml")
    if st.session_state.citygml_model is not None:
        st.info("CityGML model uploaded.")

# IFC Column
with col_ifc:
    st.subheader("IFC Model")

    ifc_file = st.file_uploader(label="Upload IFC file.", type=["ifc"], key="ifc_uploader")
    if ifc_file is not None:
        with open(file_path + "ifc_file.ifc", "wb") as f:
            f.write(ifc_file.read())
        st.session_state.ifc_model = parse_ifc_file(file_path + "ifc_file.ifc")
    if st.session_state.ifc_model is not None:
        st.info("IFC model uploaded.")

# DXF Column
with col_dxf:
    st.subheader("DXF Model (Optional)")

    dxf_file = st.file_uploader(label="Upload DXF file.", type=["dxf"], key="dxf_uploader")
    if dxf_file is not None:
        with open(file_path + "dxf_file.dxf", "wb") as f:
            f.write(dxf_file.read())
        st.session_state.dxf_model = parse_dxf_file(file_path + "dxf_file.dxf")
    if st.session_state.dxf_model is not None:
        st.info("DXF model uploaded.")