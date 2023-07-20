# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: batch_ndvi 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2023/6/21 
"""

from osgeo import gdal, gdalconst
import os
import numpy as np
from tqdm import tqdm


def NDVI_calculte(S2_file, NDVI_output_file):
	"""
	红光与近红外波段分别存储为tif文件的NDVI指数计算
	:param Red_band_file: 红光波段文件
	:param NIR_band_file: 近红外波段文件
	:param NDVI_output_file: 输出NDVI影像
	:return:
	"""
	ds: gdal.Dataset = gdal.Open(S2_file)
	# 红波段
	red = ds.GetRasterBand(3).ReadAsArray()
	# 近红外波段
	nir = ds.GetRasterBand(4).ReadAsArray()

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


if __name__ == "__main__":
	s2path = 'D:/2023遥感综合实习/S2Data'
	ndvipath = 'D:/2023遥感综合实习/S2NDVI'
	filelist = os.listdir(s2path)
	for file in tqdm(filelist):
		(filename, extension) = os.path.splitext(file)
		if extension == '.tif':
			outname = filename + '_ndvi' + extension
			s2_file = s2path + '/' + file
			NDVI_output_file = ndvipath + '/' + outname
			NDVI_calculte(s2_file, NDVI_output_file)
