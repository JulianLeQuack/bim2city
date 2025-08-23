import streamlit as st
import os, sys
import datetime
from shapely import unary_union

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from source.transformation_vertical.vertical_registration.estimate_vertical_registration import estimate_vertical_registration_manual, estimate_vertical_registration_story_mapping, estimate_vertical_registration_z_extent, z_extent_is_similar, refine_vertical_registration_with_windows
from source.transformation_vertical.vertical_registration.get_terrain_elevation import get_terrain_elevation
from source.transformation_vertical.create_sideviews.create_citygml_sideview import create_citygml_sideview
from source.transformation_vertical.create_sideviews.create_ifc_sideview import create_ifc_sideview
from source.transformation_vertical.extract_extents.extract_citygml_z_extent import extract_citygml_z_extent
from source.transformation_vertical.extract_extents.extract_ifc_z_extent import extract_ifc_z_extent
from source.geometry_helpers.geometry_helpers import transform_ifc, translate_multipolygon, extrude_multipolygon, mesh_to_sideview_multipolygon
from source.transformation_horizontal.footprint_creation.create_ifc_footprint import parse_ifc_file
from source.transformation_vertical.extract_windows.extract_citygml_windows import extract_citygml_windows
from source.transformation_vertical.extract_windows.extract_ifc_windows import extract_ifc_windows

st.set_page_config(
    page_title="bim2city",
    page_icon="./images/bim2city_logo.png",
    layout="wide"
)
st.title("Vertical Registration")

from Utilities import init_session_state, plot
init_session_state()

file_path = "./test_data/streamlit/files/"
output_path = "./test_data/output/"

if st.session_state.citygml_model is None or st.session_state.ifc_model is None:
    st.warning("Upload an IFC model and a CityGML model first.")
elif not st.session_state.horizontal_transformation:
    st.warning("Estimate the horizontal registration first.")
else:

    col_settings, col_plot = st.columns(2)

    with col_settings:
        
        st.subheader("Matching Height-based Vertical Registration")
        if not st.session_state.citygml_z_extent or not st.session_state.ifc_z_extent:
            print("Extracting Z extents.")
            st.session_state.citygml_z_extent = extract_citygml_z_extent(st.session_state.citygml_model, st.session_state.citygml_building_ids_selected)
            st.session_state.ifc_z_extent = extract_ifc_z_extent(st.session_state.ifc_model)
        st.session_state.z_extent_is_similar = z_extent_is_similar(st.session_state.citygml_z_extent, st.session_state.ifc_z_extent)

        if not st.session_state.citygml_windows and not st.session_state.ifc_windows:
            print("Extracting windows.")
            st.session_state.citygml_windows = extract_citygml_windows(st.session_state.citygml_model, st.session_state.citygml_building_ids_selected)
            st.session_state.ifc_windows = extract_ifc_windows(st.session_state.ifc_model)

        if st.session_state.z_extent_is_similar:
            if st.button("Run Vertical Registration Automatically"):
                st.session_state.lod2_transformation = estimate_vertical_registration_z_extent(
                    horizontal_transformation=st.session_state.horizontal_transformation,
                    citygml_z_extent=st.session_state.citygml_z_extent,
                    ifc_z_extent=st.session_state.ifc_z_extent,
                    z_extent_is_similar=st.session_state.z_extent_is_similar
                )
        else:
            st.warning("Model Z extents do not match. Story mapping or manual elevation required.")

        st.subheader("Story Mapping-based Vertical Registration")

        ifc_story_mapping_story_id = st.multiselect(
            "Select IFC story for story mapping.",
            options=st.session_state.ifc_building_stories_all,
            max_selections=1
        )
        ifc_story_mapping_story_number = st.number_input(
            "Input story number for IFC story mapping. (Ground floor = 0, First floor = 1, etc.)",
            step=1,
            value=st.session_state.ifc_story_mapping_story_number
        )

        if st.button("Run Vertical Registration with Story Mapping"):
            st.session_state.lod2_transformation = estimate_vertical_registration_story_mapping(
                horizontal_transformation=st.session_state.horizontal_transformation,
                story_id=ifc_story_mapping_story_id[0],
                story_number=ifc_story_mapping_story_number,
                ifc_footprint=st.session_state.ifc_footprint_horizontally_transformed,
                ifc_z_extent=st.session_state.ifc_z_extent
            )

        st.subheader("Manual Vertical Registration")
        manual_elevation = st.number_input(
            "Input a Z offset manually.",
            value=st.session_state.manual_elevation
        )

        if st.button("Run Vertical Registration with Manual Offset"):
            st.session_state.lod2_transformation = estimate_vertical_registration_manual(
                horizontal_transformation=st.session_state.horizontal_transformation,
                manual_elevation=manual_elevation
            )

        if st.session_state.lod2_transformation:
            st.session_state.lod3_transformation = refine_vertical_registration_with_windows(
                citygml_windows=st.session_state.citygml_windows,
                ifc_windows=st.session_state.ifc_windows,
                lod2_transformation=st.session_state.lod2_transformation,
                ifc_z_extent=st.session_state.ifc_z_extent
            )
            st.session_state.final_transformation = st.session_state.lod3_transformation


    with col_plot:
        
        if st.session_state.ifc_z_extent is not None:
            st.session_state.citygml_sideview = create_citygml_sideview(st.session_state.citygml_model, st.session_state.citygml_building_ids_selected)
            max_z_ifc = max(story['max_z'] for story in st.session_state.ifc_z_extent if story['max_z'] is not None)
            min_z_ifc = min(story['min_z'] for story in st.session_state.ifc_z_extent if story['min_z'] is not None)
            st.session_state.ifc_sideview = mesh_to_sideview_multipolygon(
                extrude_multipolygon(
                    st.session_state.ifc_footprint_horizontally_transformed,
                    height=(max_z_ifc - min_z_ifc)
                )
            )

            if st.session_state.terrain_level == 0:
                footprint = unary_union(st.session_state.ifc_footprint_horizontally_transformed)
                centroid = [footprint.centroid.x, footprint.centroid.y]
                st.session_state.terrain_level = get_terrain_elevation(*centroid)

            if st.session_state.final_transformation:
                st.session_state.ifc_sideview = translate_multipolygon(st.session_state.ifc_sideview, [0, st.session_state.final_transformation["translation"][2]+min_z_ifc])

                plot(
                    footprints=[st.session_state.citygml_sideview, st.session_state.ifc_sideview],
                    key="citygml_and_ifc_sideview",
                    terrain_level=st.session_state.terrain_level
                    )

                st.info(f"Final transformation: {st.session_state.final_transformation}")
    
    if st.button(
        "Export IFC Model",
        key="export_ifc_model"
    ):
        ifc_model_transformed = parse_ifc_file(file_path + "ifc_file.ifc")
        ifc_model_transformed = transform_ifc(ifc_model_transformed, st.session_state.final_transformation)
        ifc_model_transformed.write(output_path + f"ifc_file_transformed_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.ifc")