from osgeo import gdal

input_raster = r"F:\JUNK\dem90.tif"
# or as an alternative if the input is already a gdal raster object you can use that gdal object
input_raster = gdal.Open(input_raster)
input_shape = r"F:\JUNK\gla-shp.shp"  # or any other format
output_raster = r'F:\JUNK\test2.tif'  # your output raster file

ds = gdal.Warp(output_raster,
               input_raster,
               format='GTiff',
               cutlineDSName=input_shape,  # or any other file format
               cutlineWhere="FIELD = 'whatever'",
               # optionally you can filter your cutline (shapefile) based on attribute values
               dstNodata=-9999)  # select the no data value you like
ds = None  # do other stuff with ds object, it is your cropped dataset. in this case we only close the dataset.
