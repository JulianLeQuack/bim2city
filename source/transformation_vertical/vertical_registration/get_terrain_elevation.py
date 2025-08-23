# Imports

import rasterio
from rasterio.merge import merge
import requests
from io import BytesIO
import traceback


# Helper functions

def assemble_tiles(tile_paths):
    src_files_to_mosaic = []
    for path in tile_paths:
        src = rasterio.open(path)
        src_files_to_mosaic.append(src)
    mosaic, out_trans = merge(src_files_to_mosaic)
    out_meta = src_files_to_mosaic[0].meta.copy()
    out_meta.update({
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans
    })
    nodata = src_files_to_mosaic[0].nodata
    for src in src_files_to_mosaic:
        src.close()
    return mosaic, out_trans, out_meta, nodata

def get_elevation(mosaic, transform, x, y, nodata):
    col, row = ~transform * (x, y)
    col, row = int(col), int(row)
    if row < 0 or row >= mosaic.shape[1] or col < 0 or col >= mosaic.shape[2]:
        return None
    elevation = mosaic[0, row, col]
    if elevation == nodata:
        return None
    return round(float(elevation), 2)


# Main functions

def get_terrain_elevation(x: float, y: float) -> float:
    """
    Get the terrain elevation at a specific point using WCS service for 1m DTM of Bavaria.
    
    @param x: X coordinate in EPSG:25832.
    @param y: Y coordinate in EPSG:25832.
    @return: Elevation in meters, or None if no data is available.
    """
    try:
        tile_files = [
            "./data/690_5335.tif",
            "./data/690_5336.tif",
            "./data/691_5335.tif",
            "./data/691_5336.tif",
        ]
        mosaic, transform, meta, nodata = assemble_tiles(tile_files)
        elevation = get_elevation(mosaic, transform, x, y, nodata)
        return(elevation)
                
    except Exception as e:
        print(f"An error occurred getting the terrain elevation: {e}")
        print(f"Coordinates: x={x}, y={y}")
        print(traceback.format_exc())
        return None