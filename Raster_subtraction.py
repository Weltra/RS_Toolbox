# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: Raster_subtraction 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2022/10/17 
"""

from osgeo import gdal
import numpy as np
from tqdm import tqdm


def subtract_raster(DEM_standard_path, DEM_path, out_path):
	dataset = gdal.Open(DEM_standard_path)
	projinfo = dataset.GetProjection()
	geotransform = dataset.GetGeoTransform()

	format = "GTiff"
	driver = gdal.GetDriverByName(format)
	depth = dataset.RasterCount
	rows = int(dataset.RasterYSize)
	colmns = int(dataset.RasterXSize)

	DEM_standard = dataset.ReadAsArray()
	src2 = gdal.Open(DEM_path)
	DEM = src2.ReadAsArray()
	Result = np.zeros((rows, colmns))
	Result_DEM = driver.Create(out_path, colmns, rows, depth, gdal.GDT_Float32)
	Result_DEM.SetGeoTransform(geotransform)
	Result_DEM.SetProjection(projinfo)

	for row in tqdm(range(rows)):
		for col in range(colmns):
			if DEM[row, col] > 0:
				Result[row, col] = DEM_standard[row, col] - DEM[row, col]


	Result_DEM.GetRasterBand(1).WriteArray(Result)


if __name__ == '__main__':
	# 修改路径
	Standard_DEM_Path = r"dem_standard.tif"  # 标准的DEM
	MY_DEM_Path = r"Extract_terl.tif"  # 由点，线，TIN得到的DEM
	OutTif = r"out_TIN.tif"
	subtract_raster(Standard_DEM_Path, MY_DEM_Path, OutTif)
