# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: get_value_by_lon_lat 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2023/3/28 
"""

from osgeo import gdal
import os
import pandas as pd


def get_location_data(location, img_files):
	f = img_files
	print(f)
	tif_name = os.path.basename(f).split('_')[0]
	raster: gdal.Dataset = gdal.Open(f)
	geotransform = raster.GetGeoTransform()
	# 获取栅格影像的左上角起始坐标，像元大小
	xOrigin = geotransform[0]
	yOrigin = geotransform[3]
	pixelWidth = geotransform[1]
	pixelHeight = geotransform[5]
	# 创建一个空的数组，把for循环里面得到的值放到这个数组里面
	data = []
	for index, row in location.iterrows():
		long_value = row["X"]
		lat_value = row["Y"]
		print(lat_value)
		print(yOrigin)
		coord_x = long_value
		coord_y = lat_value
		# 主要思路就是计算该坐标与该tif起始坐标差了多少行和列
		loc_x = int((float(coord_x) - xOrigin) / pixelWidth)
		loc_y = int((float(coord_y) - yOrigin) / pixelHeight)
		print(loc_y)
		# 知道了多少行和列，就直接读这个行列对应数像元的数值大小，并把读到的数值追加到data这个空数组里面
		data_value = raster.GetRasterBand(1).ReadAsArray(loc_x, loc_y, 1, 1)[0, 0]
		data.append(data_value)
	location['NDVI_' + tif_name] = data
	print(location)
	return location


if __name__ == '__main__':
	excel_data = pd.read_excel(r'G:\0test\test\xj.xlsx')
	test_tif = r'G:\0test\test\xj.tif'
	out_data = get_location_data(excel_data, test_tif)
	# 输出为另一个表格
	xls_name = r'G:\0test\test\location_value.xlsx'
	out_data.to_excel(xls_name)