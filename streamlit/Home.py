import streamlit as st
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

st.set_page_config(
    page_title="bim2city",
    page_icon="./images/bim2city_logo.png",
    layout="wide"
)

st.title("Welcome to bim2city!")

st.subheader("Start here:")
st.page_link("pages/1_File_Import.py")