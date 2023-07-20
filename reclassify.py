# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: reclassify 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2022/10/31 
"""

from osgeo import gdal
from tqdm import tqdm
import numpy as np

def main():
	data_path = 'djk_dem25.tif'
	outtif = 'djk_dem25_reclass.tif'
	dataset = gdal.Open(data_path)
	projinfo = dataset.GetProjection()
	geotransform = dataset.GetGeoTransform()

	format = "GTiff"
	driver = gdal.GetDriverByName(format)
	rows = int(dataset.RasterYSize)
	colmns = int(dataset.RasterXSize)

	data = dataset.ReadAsArray()

	dst_ds1 = driver.Create(outtif, colmns, rows, 1,
	                        gdal.GDT_Float32)

	dst_ds1.SetGeoTransform(geotransform)
	dst_ds1.SetProjection(projinfo)
	reclassdata = data
	# 开始计算
	for row in tqdm(range(rows)):
		for col in range(colmns):
			if data[row][col] < 0:
				reclassdata[row][col] = -9999  # 设置NaN值
			if 0 <= data[row][col] < 300:
				reclassdata[row][col] = 1
			elif 500 > data[row][col] >= 300:
				reclassdata[row][col] = 2
			elif 800 > data[row][col] >= 500:
				reclassdata[row][col] = 3
			elif 1100 > data[row][col] >= 800:
				reclassdata[row][col] = 4
			elif 1100 <= data[row][col]:
				reclassdata[row][col] = 5

	dst_ds1.GetRasterBand(1).WriteArray(reclassdata)


if __name__ == '__main__':
	main()