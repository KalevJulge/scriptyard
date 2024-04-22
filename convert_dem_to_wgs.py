# Converts Land Board DEM from EPSG:3301 to WGS84.
# Run using OSGeo4WShell.
# Does not convert EH2000 heights to ellipsoid heights!!!


import os
from osgeo import gdal, osr
import glob

input_directory = 'dem_original'
output_directory = 'dem_wgs84'

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

dem_files = glob.glob(os.path.join(input_directory, '*.tif'))
src_epsg_code = 3301

for dem_file in dem_files:
    src_ds = gdal.Open(dem_file, gdal.GA_ReadOnly)
    if src_ds is None:
        print(f"Unable to open {dem_file}")
        continue
    
    src_proj = osr.SpatialReference()
    src_proj.ImportFromEPSG(src_epsg_code)
    
    tgt_proj = osr.SpatialReference()
    tgt_proj.ImportFromEPSG(4326)
    
    transform = osr.CoordinateTransformation(src_proj, tgt_proj)
    
    gt = src_ds.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + gt[5] * src_ds.RasterYSize
    maxx = gt[0] + gt[1] * src_ds.RasterXSize
    maxy = gt[3]
    
    minx, miny, _ = transform.TransformPoint(minx, miny)[:3]
    maxx, maxy, _ = transform.TransformPoint(maxx, maxy)[:3]
    
    output_file = os.path.join(output_directory, os.path.basename(dem_file))
    
    # Create WarpOptions object
    warp_options = gdal.WarpOptions(
        format='GTiff',
        outputBounds=[minx, miny, maxx, maxy],
        dstSRS=tgt_proj.ExportToWkt(),
        resampleAlg=gdal.GRA_Bilinear,
        srcNodata=-9999,  
        dstNodata=-9999,  
        creationOptions=['COMPRESS=LZW', 'PREDICTOR=2'],  
        outputType=gdal.GDT_Float32
        )
    
    result = gdal.Warp(output_file, src_ds, warpOptions=warp_options)
    
    if result is None:
        print(f"Reprojection failed for {dem_file}")
    else:
        print(f"Reprojection succeeded for {dem_file}")

    src_ds = None
    result = None

print("Processing complete.")
