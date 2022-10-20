# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: Extract_By_Mask 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2022/10/20
"""
from osgeo import gdal


def extract_by_mask(input_path, input_shape_path, output_path):
	"""
	:param input_path:
	:param input_shape_path:
	:param output_path:
	:return:
	"""
	# 实例化一个Warp对象
	ds = gdal.Warp(output_path,
	               input_path,
	               format='GTiff',
	               cutlineDSName=input_shape_path,  # or any other file format
	               cutlineWhere="FIELD = 'whatever'",
	               # optionally you can filter your cutline (shapefile) based on attribute values
	               dstNodata=-9999)  # select the no data value you like
	ds = None  # do other stuff with ds object, it is your cropped dataset. in this case we only close the dataset.


if __name__ == "__main__":
	input_raster = r"F:\JUNK\dem90.tif"
	# or as an alternative if the input is already a gdal raster object you can use that gdal object
	input_raster = gdal.Open(input_raster)
	input_shape = r"F:\JUNK\gla-shp.shp"  # or any other format
	output_raster = r'F:\JUNK\test2.tif'  # your output raster file
	extract_by_mask(input_raster, input_shape, output_raster)
