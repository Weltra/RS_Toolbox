# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: batch_LSWI 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2023/6/21 
"""

from osgeo import gdal, gdalconst
import os
import numpy as np
from tqdm import tqdm


def LSWI_calculte(S2_file, LSWI_output_file):
	"""
	:param S2_file: 哨兵影像文件
	:param LSWI_output_file: 输出EVI影像
	:return:
	"""
	ds: gdal.Dataset = gdal.Open(S2_file)
	# 红波段
	blue = ds.GetRasterBand(1).ReadAsArray()
	red = ds.GetRasterBand(3).ReadAsArray()
	# 近红外波段
	nir = ds.GetRasterBand(4).ReadAsArray()
	swirl = ds.GetRasterBand(5).ReadAsArray()

	np.seterr(all="ignore")

	lswi = (nir - swirl) / (nir + swirl)
	# NAN——>0
	nan_index = np.isnan(lswi)
	lswi[nan_index] = 0
	lswi = lswi.astype(np.float32)
	# 创建tif
	tif_driver = gdal.GetDriverByName('GTiff')

	if os.path.exists(LSWI_output_file) and os.path.isfile(LSWI_output_file):  # 如果已存在同名影像则删除之
		os.remove(LSWI_output_file)
	out_ds = tif_driver.Create(LSWI_output_file, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32)
	# 设置投影坐标
	out_ds.SetProjection(ds.GetProjection())
	out_ds.SetGeoTransform(ds.GetGeoTransform())
	# 写入数据
	out_band = out_ds.GetRasterBand(1)
	out_band.WriteArray(lswi)


if __name__ == "__main__":
	s2path = 'D:/2023遥感综合实习/S2Data'
	ndvipath = 'D:/2023遥感综合实习/S2LSWI'
	filelist = os.listdir(s2path)
	for file in tqdm(filelist):
		(filename, extension) = os.path.splitext(file)
		if extension == '.tif':
			outname = filename + '_lswi' + extension
			s2_file = s2path + '/' + file
			LSWI_output_file = ndvipath + '/' + outname
			LSWI_calculte(s2_file, LSWI_output_file)
