# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: batch_EVI
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2023/6/21 
"""

from osgeo import gdal, gdalconst
import os
import numpy as np
from tqdm import tqdm


def EVI_calculte(S2_file, EVI_output_file):
	"""
	:param S2_file: 哨兵影像文件
	:param EVI_output_file: 输出EVI影像
	:return:
	"""
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
	s2path = 'D:/2023遥感综合实习/S2Data'
	evipath = 'D:/2023遥感综合实习/S2EVI'
	filelist = os.listdir(s2path)
	for file in tqdm(filelist):
		(filename, extension) = os.path.splitext(file)
		if extension == '.tif':
			outname = filename + '_evi' + extension
			s2_file = s2path + '/' + file
			EVI_output_file = evipath + '/' + outname
			EVI_calculte(s2_file, EVI_output_file)
