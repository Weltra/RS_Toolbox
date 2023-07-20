# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: get_value_by_location
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2023/3/28 
"""

from osgeo import gdal
import pandas as pd
from osgeo import osr
import numpy as np
import os
import re


def get_file_info(file_path):
	"""
	获取文件的信息
	:param file_path: 文件路径
	:return: 数据集，地理坐标系，投影坐标系，范围，shape
	"""
	dataset = gdal.Open(file_path)
	pcs = osr.SpatialReference()
	pcs.ImportFromWkt(dataset.GetProjection())
	gcs = pcs.CloneGeogCS()
	extend = dataset.GetGeoTransform()
	shape = (dataset.RasterXSize, dataset.RasterYSize)
	return dataset, gcs, pcs, extend, shape


def lonlat_to_xy(gcs, pcs, lon, lat):
	"""
	地理坐标系转投影坐标系
	:param gcs: 地理坐标系
	:param pcs: 投影坐标系
	:param lon: 经度
	:param lat: 纬度
	:return: 投影坐标系坐标
	"""
	ct = osr.CoordinateTransformation(gcs, pcs)
	coordinate = ct.TransformPoint(lon, lat)
	return coordinate[0], coordinate[1], coordinate[2]


def xy_to_rowcol(extend, x, y):
	"""
	投影坐标系转图上坐标系
	:param extend: 范围
	:param x: 投影坐标系x
	:param y: 投影坐标系y
	:return: 行号与列号
	"""
	a = np.array([[extend[1], extend[2]], [extend[4], extend[5]]])
	b = np.array([x - extend[0], y - extend[3]])
	row_col = np.linalg.solve(a, b)
	row = int(np.float(row_col[1]))
	col = int(np.float(row_col[0]))
	return row, col


def get_location_data(location, file_name):
	"""
	根据经纬度来取得相应位置的值
	:param location: 经纬度坐标
	:param file_name: 文件名
	:return: 取得的值
	"""
	dataset, gcs, pcs, extend, shape = get_file_info(file_name)
	img = dataset.ReadAsArray()
	x, y, _i = lonlat_to_xy(gcs, pcs, location[0], location[1])
	row, col = xy_to_rowcol(extend, x, y)
	img_value = img[row, col]
	return img_value


if __name__ == '__main__':
	loc = [-96.476639, 41.165056]
	img_path = 'D:\Download\实验一\数据\MODIS'
	resultPath = 'D:/result.xlsx'
	filelist = os.listdir(img_path)
	# 解析日期
	pattern = re.compile(r'\d{4}\d{3}')
	df = pd.DataFrame(columns=['date', 'value'])
	for file in filelist:
		(filename, extension) = os.path.splitext(file)
		if extension == '.img':
			date = pattern.findall(filename)
			img_file = img_path + '/' + file
			value = get_location_data(loc, img_file)
			result = [date[0][-3:]+'/' + date[0][:-3], value]
			df.loc[len(df.index)] = result
	# 导出文件
	df.to_excel(resultPath)