# Imports

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import numpy as np

import traceback


# Helper functions



# Main functions

def extract_ifc_z_extent(ifc_model: ifcopenshell.file) -> list:
    """
    Returns the overall height of the model.

    @param ifc_model: A parsed ifcopenshell model.
    @return: Dictionary of the form: {'story_id': '2MPOlgJ$1VdW0A00i00czE', 'story_name': '100', 'min_z': np.float64(-1.09), 'max_z': np.float64(4.9)}.
    """
    try:
        settings = ifcopenshell.geom.settings()

        # Use only main elements to avoid furniture which might not be present in CityGML.
        main_elements = ["IfcWall", "IfcSlab", "IfcColumn", "IfcBeam", "IfcFooting"]

        story_extents = []

        # Get all storys in the model
        stories = ifc_model.by_type("IfcBuildingStorey")
        for story in stories:
            z_values =[]
            # Get all elements related to this story
            related_elements = []
            for rel in getattr(story, "ContainsElements", []):
                related_elements.extend(rel.RelatedElements)
            # Filter only main construction elements
            elements = [el for el in related_elements if el.is_a() in main_elements]
            for element in elements:
                try:
                    shape = ifcopenshell.geom.create_shape(settings, element)
                except Exception as e:
                    continue
                verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
                matrix = ifcopenshell.util.shape.get_shape_matrix(shape)
                for v in verts:
                    v_homog = np.array([v[0], v[1], v[2], 1.0])
                    v_transformed = matrix @ v_homog
                    z = v_transformed[2]
                    z_values.append(z)
            min_z, max_z = min(z_values), max(z_values)
            story_extents.append({
                "story_id": story.GlobalId,
                "story_name": getattr(story, "Name", ""),
                "min_z": round(min_z, 2),
                "max_z": round(max_z, 2)
            })
        return story_extents

    except Exception as e:
        print(f"An error occurred extracting the IFC Z extent: {e}")
        print(traceback.format_exc())