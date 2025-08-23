# Imports

import ezdxf
import ezdxf.document as DOC
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.ops import unary_union, polygonize
import traceback


# Helper functions

def parse_dxf_file(dxf_path: str) -> DOC.Drawing:
    """
    Parses DXF file and returns the EZDXF Document.

    @params dxf_path: Path to the DXF file.
    @return: EZDXF Document.
    """
    try:
        doc = ezdxf.readfile(dxf_path)
        return doc
    
    except Exception as e:
        print(f"An error occurred parsing the DXF file: {e}")
        print(traceback.format_exc())
        return None
    


def extract_dxf_layers(dxf_doc: DOC.Drawing) -> list:
    """
    Extract all layers from a DXF file.

    @param dxf_path: Path to the DXF file.
    @return: List of layer names found in the file.
    """
    try:
        layers = [layer.dxf.name for layer in dxf_doc.layers]
        return layers

    except Exception as e:
        print(f"An error occurred getting the DXF layers: {e}")
        print(traceback.format_exc())
        return None
    


def is_likely_connection_line(segment: LineString) -> bool:
    """
    Checks if a line could be a connection line from the origin to a block geometry.

    @params segment: Linestring to check.
    @return: True if it is likely a conneciton line.
    """
    start, end = segment.coords
    origin_distance_start = (start[0]**2 + start[1]**2)**0.5
    origin_distance_end = (end[0]**2 + end[1]**2)**0.5
    length = segment.length
    # If one point is near origin and the segment is relatively long
    return (origin_distance_start < 0.1 or origin_distance_end < 0.1) and length > 10
    


# Main functions

def create_dxf_footprint(dxf_doc: DOC.Drawing, layer_names: list, detailed: bool=False) -> MultiPolygon:
    """
    Generates a multipolygon from geometries in one or more DXF layers.

    @param dxf_path: Path to the DXF file.
    @param layer_names: List of layer names to use for the multipolygon.
    @param detailed: Returns detailed entity geometries if needed for floor plan-like representation.
    @return: 2D multipolygon of the selected geometries.
    """
    try:
        # Get entities wit query
        msp = dxf_doc.modelspace()
        line_segments = []

        for layer_name in layer_names:
            entities = msp.query(f'*[layer=="{layer_name}"]')
            if entities is None:
                print(f"No entities found for layer {layer_name}.")
            for entity in entities:
                try:
                    for geometry in entity.virtual_entities():
                        # Process LINE entities directly
                        if geometry.dxftype() == "LINE":
                            start = (geometry.dxf.start[0], geometry.dxf.start[1])
                            end = (geometry.dxf.end[0], geometry.dxf.end[1])
                            segment = LineString([start, end])
                            if not is_likely_connection_line(segment):
                                line_segments.append(segment)
                        
                        # Process POLYLINE or LWPOLYLINE by splitting into individual segments
                        elif geometry.dxftype() in ["POLYLINE", "LWPOLYLINE"]:
                            try:
                                # Convert each point to 2D by taking only (x, y)
                                points = [(pt[0], pt[1]) for pt in geometry.points()]
                            except Exception as e:
                                print(f"Error extracting points from polyline: {e}")
                                continue
                            if len(points) < 2:
                                continue
                            # Create segments from consecutive pairs of 2D points
                            for i in range(len(points) - 1):
                                segment = LineString([points[i], points[i + 1]])
                                if not is_likely_connection_line(segment):
                                    line_segments.append(segment)
                        else:
                            # If additional virtual entities exist, try to process them as well.
                            for sub_geom in geometry.virtual_entities():
                                if sub_geom.dxftype() == "LINE":
                                    start = (sub_geom.dxf.start[0], sub_geom.dxf.start[1])
                                    end = (sub_geom.dxf.end[0], sub_geom.dxf.end[1])
                                    segment = LineString([start, end])
                                    if not is_likely_connection_line(segment):
                                        line_segments.append(segment)
                
                except Exception as e:
                    pass

        if not line_segments:
            print(f"No geometries found in model.")
            return MultiPolygon()

        # Merge all line segments and polygonize the network:
        union_lines = unary_union(line_segments)
        polygons = list(polygonize(union_lines))

        if not detailed:
            # Create a union of the polygons, and extract only the exteriors to form a footprint.
            union_poly = unary_union(polygons)
            if union_poly.geom_type == "Polygon":
                return MultiPolygon([union_poly])
            elif union_poly.geom_type == "MultiPolygon":
                return union_poly
            else:
                return MultiPolygon()
        else:
            # If detailed is set to true, return polygons directly.
            valid_polygons = []
            for polygon in polygons:
                if isinstance(polygon, Polygon) and polygon.is_valid:
                    valid_polygons.append(polygon)
            if valid_polygons:
                return(MultiPolygon(valid_polygons))
            else:
                print(f"No valid polygons found for detailed footprint. Returning None.")
                return MultiPolygon()

    except Exception as e:
        print(f"An error occurred creating the DXF footprint: {e}")
        print(traceback.format_exc())
        return MultiPolygon()