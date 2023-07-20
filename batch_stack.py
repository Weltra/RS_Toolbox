# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: batch_stack 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2023/6/23
用于将所有的影像的NIR波段合成在在一个影像中（n,height,width）
"""

import os
import numpy as np
from osgeo import gdal


# os.environ['PROJ_LIB'] = r'e:\Anaconda3\envs\cloneTF21\Library\share\proj'


class GRID:

	# 读影像文件
	def read_img(self, filename):
		dataset = gdal.Open(filename)  # 打开文件
		im_width = dataset.RasterXSize  # 栅格矩阵的列数
		im_height = dataset.RasterYSize  # 栅格矩阵的行数
		im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
		im_proj = dataset.GetProjection()  # 地图投影信息
		# 近红外波段
		im_data = dataset.GetRasterBand(1).ReadAsArray(0, 0, im_width, im_height)

		del dataset
		return im_data, im_width, im_height, im_geotrans, im_proj

	# 写成tif影像
	def write_img(self, filename, im_proj, im_geotrans, im_data):
		# 判断栅格数据的数据类型
		if 'int8' in im_data.dtype.name:
			datatype = gdal.GDT_Byte
		elif 'int16' in im_data.dtype.name:
			datatype = gdal.GDT_UInt16
		else:
			datatype = gdal.GDT_Float32
		# 判读数组维数
		if len(im_data.shape) == 3:
			im_bands, im_height, im_width = im_data.shape
		else:
			im_bands, (im_height, im_width) = 1, im_data.shape

		# 创建文件
		driver = gdal.GetDriverByName("GTiff")  # 数据类型必须有，因为要计算需要多大内存空间
		dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)
		dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
		dataset.SetProjection(im_proj)  # 写入投影
		if im_bands == 1:
			dataset.GetRasterBand(1).WriteArray(im_data)  # 写入数组数据
		else:
			for i in range(im_bands):
				dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
		del dataset

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
	run = GRID()

	# 单波段影像文件夹
	filename = r"K:\Area4\新建文件夹"
	# 输出文件夹
	output_layerstack = r"K:\Area4"
	files = []
	datas = []
	# listdir() 方法用于返回指定的文件夹包含的文件或文件夹的名字的列表。
	for file in os.listdir(filename):
		if os.path.splitext(file)[1] == '.tif':
			sourcefile = os.path.join(filename, file)
			files.append(sourcefile)

	for file, k in zip(files, range(len(files))):
		# 读入矢量和栅格文件
		(filepath, tempfilename) = os.path.split(file)
		(filename, extension) = os.path.splitext(tempfilename)
		# out_file = outpath + '/' + filename + '.tif'
		print(filename)
		data, height, width, geotrans, proj = run.read_img(file)
		datas.append(data)

	datas = np.array(datas)
	print(datas.shape)
	run.write_img(output_layerstack + "/layerstack.tif", proj, geotrans, datas, )
