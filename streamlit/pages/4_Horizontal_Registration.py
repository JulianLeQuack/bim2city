import streamlit as st
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from source.transformation_horizontal.horizontal_registration.check_rotation_symmetry import check_rotational_symmetry
from source.transformation_horizontal.horizontal_registration.estimate_horizontal_transformation import estimate_rough_horizontal_registration, refine_horizontal_registration
from source.geometry_helpers.geometry_helpers import translate_multipolygon, rotate_multipolygon, translate_points, rotate_points, transform_ifc
from source.transformation_horizontal.footprint_creation.create_ifc_footprint import parse_ifc_file

st.set_page_config(
    page_title="bim2city",
    page_icon="./images/bim2city_logo.png",
    layout="wide"
)
st.title("Horizontal Registration")
st.subheader("Manual Feature Matching")

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
        plot(footprints=st.session_state.citygml_footprint,
             features_filtered=st.session_state.citygml_features_filtered,
             key="citygml_features_plot",
             features_selected_1=st.session_state.citygml_matching_features_ifc,
             features_selected_2=st.session_state.citygml_matching_features_dxf,
             feat_sel_label_1="IFC to CityGML",
             feat_sel_label_2="DXF to CityGML",
             feat_sel_label_1_and_2="IFC and DXF to CityGML")
        
        st.session_state.citygml_rotational_symmetry_angles = check_rotational_symmetry(st.session_state.citygml_footprint)
        if st.session_state.citygml_rotational_symmetry_angles != []:
            st.warning(f"CityGML footprint is rotationally symmetric by {st.session_state.citygml_rotational_symmetry_angles} radians. Select at least 1 common feature manually for registration.")
        else:
            st.info(f"No rotational symmetry detected in CityGML footprint.")

        citygml_all_indices = list([i for i in range(len(st.session_state.citygml_features_filtered))])
        citygml_matching_features_ifc = st.multiselect(
            "Select CityGML feature(s) for IFC to CityGML registration.",
            options=citygml_all_indices,
            default=st.session_state.citygml_matching_features_ifc,
            max_selections=2
        )

        citygml_matching_features_dxf = st.multiselect(
            "Select CityGML feature(s) for DXF to CityGML registration.",
            options=citygml_all_indices,
            default=st.session_state.citygml_matching_features_dxf,
            max_selections=2
        )

        if st.button("Apply CityGML Feature Selection"):
            st.session_state.citygml_matching_features_ifc = [match for match in citygml_matching_features_ifc if match != []]
            st.session_state.citygml_matching_features_dxf = [match for match in citygml_matching_features_dxf if match != []]
            st.rerun()

#IFC Column
with col_ifc:
    st.subheader("IFC Features")

    if st.session_state.ifc_model is None:
        st.warning("Upload an IFC model first.")
    else:
        plot(st.session_state.ifc_footprint,
             features_filtered=st.session_state.ifc_features_filtered,
             key="ifc_features_plot",
             features_selected_1=st.session_state.ifc_matching_features_citygml,
             features_selected_2=st.session_state.ifc_matching_features_dxf,
             feat_sel_label_1="IFC to CityGML",
             feat_sel_label_2="IFC to DXF",
             feat_sel_label_1_and_2="IFC to DXF and CityGML")

        st.session_state.ifc_rotational_symmetry_angles = check_rotational_symmetry(st.session_state.ifc_footprint)
        if st.session_state.ifc_rotational_symmetry_angles != []:
            st.warning(f"IFC footprint is rotationally symmetric by {st.session_state.ifc_rotational_symmetry_angles} radians. Select at least 1 common feature manually for registration.")
        else:
            st.info(f"No rotational symmetry detected in IFC footprint.")

        ifc_all_indices = list([i for i in range(len(st.session_state.ifc_features_filtered))])
        ifc_matching_features_citygml = st.multiselect(
            "Select IFC feature(s) for IFC to CityGML registration.",
            options=ifc_all_indices,
            default=st.session_state.ifc_matching_features_citygml,
            max_selections=2
        )

        ifc_matching_features_dxf = st.multiselect(
            "Select IFC feature(s) for IFC to DXF registration.",
            options=ifc_all_indices,
            default=st.session_state.ifc_matching_features_dxf,
            max_selections=2
        )

        if st.button("Apply IFC Feature Selection"):
            st.session_state.ifc_matching_features_citygml = [match for match in ifc_matching_features_citygml if match != []]
            st.session_state.ifc_matching_features_dxf = [match for match in ifc_matching_features_dxf if match != []]
            st.rerun()

#DXF Column
with col_dxf:
    st.subheader("DXF Features (Optional)")

    if st.session_state.dxf_model is None:
        st.warning("Upload a DXF model first.")
    else:
        plot(st.session_state.dxf_footprint,
             features_filtered=st.session_state.dxf_features_filtered,
             key="dxf_features_plot",
             features_selected_1=st.session_state.dxf_matching_features_citygml,
             features_selected_2=st.session_state.dxf_matching_features_ifc,
             feat_sel_label_1="DXF to CityGML",
             feat_sel_label_2="IFC to DXF",
             feat_sel_label_1_and_2="IFC to DXF to CityGML")

        st.session_state.dxf_rotational_symmetry_angles = check_rotational_symmetry(st.session_state.dxf_footprint)
        if st.session_state.dxf_rotational_symmetry_angles != []:
            st.warning(f"DXF footprint is rotationally symmetric by {st.session_state.dxf_rotational_symmetry_angles} radians. Select at least 1 common feature manually for registration.")
        else:
            st.info(f"No rotational symmetry detected in DXF footprint.")

        dxf_all_indices = list([i for i in range(len(st.session_state.dxf_features_filtered))])
        dxf_matching_features_citygml = st.multiselect(
            "Select DXF feature(s) for DXF to CityGML registration.",
            options=dxf_all_indices,
            default=st.session_state.dxf_matching_features_citygml,
            max_selections=2
        )

        dxf_matching_features_ifc = st.multiselect(
            "Select DXF feature(s) for IFC to DXF registration.",
            options=dxf_all_indices,
            default=st.session_state.dxf_matching_features_ifc,
            max_selections=2
        )

        if st.button("Apply DXF Feature Selection"):
            st.session_state.dxf_matching_features_citygml = [match for match in dxf_matching_features_citygml if match != []]
            st.session_state.dxf_matching_features_ifc = [match for match in dxf_matching_features_ifc if match != []]
            st.rerun()





# Horizontal Registration
st.subheader("Horizontal Registration Estimation")

if st.session_state.citygml_model is None or st.session_state.ifc_model is None:
    st.warning("No models available for CityGML or IFC model.")
else:
    horizontal_registration_options = ["IFC to CityGML"]
    if st.session_state.dxf_features_filtered is not None:
        horizontal_registration_options.append("DXF to CityGML, then IFC to DXF")

    st.session_state.current_horizontal_registration = st.selectbox(
        "Select a registration task.",
        options=horizontal_registration_options,
        placeholder="Select registration task"
    )

    if st.session_state.current_horizontal_registration == "IFC to CityGML":

        col_ifc_to_citygml, col_null = st.columns(2)
        
        with col_ifc_to_citygml:

            plot(
                footprints=[st.session_state.citygml_footprint, st.session_state.ifc_footprint_transformed_to_citygml],
                key="ifc_to_citygml_plot"
            )

            if st.button("Run Registration Estimation IFC to CityGML"):

                ifc_transformation_citygml_rough = estimate_rough_horizontal_registration(
                    source_features=st.session_state.ifc_features_filtered,
                    target_features=st.session_state.citygml_features_filtered,
                    fixed_features=[st.session_state.ifc_matching_features_citygml, st.session_state.citygml_matching_features_ifc]
                )
                ifc_transformation_citygml_refined = refine_horizontal_registration(
                    source_features=st.session_state.ifc_features_filtered,
                    target_features=st.session_state.citygml_features_filtered,
                    rough_transformation=ifc_transformation_citygml_rough
                )
                st.session_state.ifc_transformation_citygml = ifc_transformation_citygml_refined
                st.session_state.ifc_footprint_transformed_to_citygml = translate_multipolygon(
                    rotate_multipolygon(st.session_state.ifc_footprint,
                                        st.session_state.ifc_transformation_citygml["rotation_center"],
                                        st.session_state.ifc_transformation_citygml["rotation_angle"]),
                                        st.session_state.ifc_transformation_citygml["translation"]
                )
                st.session_state.horizontal_transformation = st.session_state.ifc_transformation_citygml
                st.rerun()


    elif st.session_state.current_horizontal_registration == "DXF to CityGML, then IFC to DXF":
            
        col_dxf_to_citygml, col_ifc_to_dxf = st.columns(2)

        with col_dxf_to_citygml:

            plot(
                footprints=[st.session_state.citygml_footprint, st.session_state.dxf_footprint_transformed],
                key="ifc_to_dxf_plot"
            )

            if st.button("Run Registration Estimation DXF to CityGML"):

                dxf_transformation_citygml_rough = estimate_rough_horizontal_registration(
                    source_features=st.session_state.dxf_features_filtered,
                    target_features=st.session_state.citygml_features_filtered,
                    fixed_features=[st.session_state.dxf_matching_features_citygml, st.session_state.citygml_matching_features_dxf]
                )
                dxf_transformation_citygml_refined = refine_horizontal_registration(
                    source_features=st.session_state.dxf_features_filtered,
                    target_features=st.session_state.citygml_features_filtered,
                    rough_transformation=dxf_transformation_citygml_rough
                )
                st.session_state.dxf_transformation_citygml = dxf_transformation_citygml_refined
                st.session_state.dxf_footprint_transformed = translate_multipolygon(
                    rotate_multipolygon(st.session_state.dxf_footprint,
                                        st.session_state.dxf_transformation_citygml["rotation_center"],
                                        st.session_state.dxf_transformation_citygml["rotation_angle"]),
                                        st.session_state.dxf_transformation_citygml["translation"]
                )
                st.rerun()


        with col_ifc_to_dxf:
            
            if st.session_state.dxf_transformation_citygml:

                st.session_state.dxf_features_filtered_transformed = translate_points(
                    rotate_points(
                        input_points=st.session_state.dxf_features_filtered,
                        center=st.session_state.dxf_transformation_citygml["rotation_center"],
                        angle_rad=st.session_state.dxf_transformation_citygml["rotation_angle"]),
                        translation=st.session_state.dxf_transformation_citygml["translation"]
                )

                if len(st.session_state.dxf_footprint_transformed.geoms) > 0:
                    plot(
                        footprints=[st.session_state.citygml_footprint, st.session_state.dxf_footprint_transformed, st.session_state.ifc_footprint_transformed_to_dxf],
                        key="ifc_to_dxf_to_citygml_plot"
                    )

                    if st.button("Run Registration Estimation IFC to DXF"):

                        ifc_transformation_dxf_rough = estimate_rough_horizontal_registration(
                            source_features=st.session_state.ifc_features_filtered,
                            target_features=st.session_state.dxf_features_filtered_transformed,
                            fixed_features=[st.session_state.ifc_matching_features_dxf, st.session_state.dxf_matching_features_ifc]
                        )
                        ifc_transformation_dxf_refined = refine_horizontal_registration(
                            source_features=st.session_state.ifc_features_filtered,
                            target_features=st.session_state.dxf_features_filtered_transformed,
                            rough_transformation=ifc_transformation_dxf_rough
                        )
                        st.session_state.ifc_transformation_dxf = ifc_transformation_dxf_refined
                        st.session_state.ifc_footprint_transformed_to_dxf = translate_multipolygon(
                            rotate_multipolygon(st.session_state.ifc_footprint,
                                                st.session_state.ifc_transformation_dxf["rotation_center"],
                                                st.session_state.ifc_transformation_dxf["rotation_angle"]),
                                                st.session_state.ifc_transformation_dxf["translation"]
                        )
                        st.session_state.horizontal_transformation = st.session_state.ifc_transformation_dxf
                        st.rerun()

if st.session_state.horizontal_transformation:
    st.info(f"Current horizontal transformation: {st.session_state.horizontal_transformation}")
    st.session_state.ifc_footprint_horizontally_transformed = translate_multipolygon(
        rotate_multipolygon(st.session_state.ifc_footprint,
                            st.session_state.horizontal_transformation["rotation_center"],
                            st.session_state.horizontal_transformation["rotation_angle"]),
                            st.session_state.horizontal_transformation["translation"]
        )