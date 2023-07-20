# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: NDVI 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2023/6/23 
"""
from osgeo import gdal
import os
import numpy as np


def NDVI_calculte(Image_file, NDVI_output_file):
	ds: gdal.Dataset = gdal.Open(Image_file)
	# 红波段
	red = ds.GetRasterBand(4).ReadAsArray()
	# 近红外波段
	nir = ds.GetRasterBand(5).ReadAsArray()

	np.seterr(all="ignore")

	ndvi = (nir - red) / (nir + red)
	# NAN——>0
	nan_index = np.isnan(ndvi)
	ndvi[nan_index] = 0
	ndvi = ndvi.astype(np.float32)
	# 创建tif
	tif_driver = gdal.GetDriverByName('GTiff')

	if os.path.exists(NDVI_output_file) and os.path.isfile(NDVI_output_file):  # 如果已存在同名影像则删除之
		os.remove(NDVI_output_file)
	out_ds = tif_driver.Create(NDVI_output_file, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32)
	# 设置投影坐标
	out_ds.SetProjection(ds.GetProjection())
	out_ds.SetGeoTransform(ds.GetGeoTransform())
	# 写入数据
	out_band = out_ds.GetRasterBand(1)
	out_band.WriteArray(ndvi)


def SAVI_calculte(S2_file, SAVI_output_file):
	ds: gdal.Dataset = gdal.Open(S2_file)
	# 红波段
	red = ds.GetRasterBand(4).ReadAsArray()
	# 近红外波段
	nir = ds.GetRasterBand(5).ReadAsArray()

	np.seterr(all="ignore")

	savi = 1.5 * (nir - red) / (nir + red + 0.5)
	# NAN——>0
	nan_index = np.isnan(savi)
	savi[nan_index] = 0
	savi = savi.astype(np.float32)
	savi[savi > 1] = 1
	savi[savi < -1] = -1
	# 创建tif
	tif_driver = gdal.GetDriverByName('GTiff')

	if os.path.exists(SAVI_output_file) and os.path.isfile(SAVI_output_file):  # 如果已存在同名影像则删除之
		os.remove(SAVI_output_file)
	out_ds = tif_driver.Create(SAVI_output_file, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32)
	# 设置投影坐标
	out_ds.SetProjection(ds.GetProjection())
	out_ds.SetGeoTransform(ds.GetGeoTransform())
	# 写入数据
	out_band = out_ds.GetRasterBand(1)
	out_band.WriteArray(savi)


def EVI_calculte(S2_file, EVI_output_file):
	ds: gdal.Dataset = gdal.Open(S2_file)
	# 红波段
	blue = ds.GetRasterBand(1).ReadAsArray()
	red = ds.GetRasterBand(3).ReadAsArray()
	# 近红外波段
	nir = ds.GetRasterBand(4).ReadAsArray()

	np.seterr(all="ignore")

	evi = (nir - red) / (nir + 6 * red - 7.5 * blue + 1) * 2.5
	# NAN——>0
	nan_index = np.isnan(evi)
	evi[nan_index] = 0
	evi = evi.astype(np.float32)
	evi[evi > 1] = 1
	evi[evi < -1] = -1
	# 创建tif
	tif_driver = gdal.GetDriverByName('GTiff')

	if os.path.exists(EVI_output_file) and os.path.isfile(EVI_output_file):  # 如果已存在同名影像则删除之
		os.remove(EVI_output_file)
	out_ds = tif_driver.Create(EVI_output_file, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32)
	# 设置投影坐标
	out_ds.SetProjection(ds.GetProjection())
	out_ds.SetGeoTransform(ds.GetGeoTransform())
	# 写入数据
	out_band = out_ds.GetRasterBand(1)
	out_band.WriteArray(evi)


if __name__ == "__main__":
	Image_path = 'D:/RS_3/数据/LC08_123039_20211110.tif'
	NDVI_path = "D:/RS_3/数据/NDVI.tif"
	EVI_path = 'D:/RS_3/数据/EVI.tif'
	SAVI_path = 'D:/RS_3/数据/SAVI.tif'
	NDVI_calculte(Image_path, NDVI_path)
	EVI_calculte(Image_path, EVI_path)
	SAVI_calculte(Image_path, SAVI_path)
