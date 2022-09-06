"""
time: 2022-7-23
coder: welt
reference:
将多波段遥感影像拆分为多张单波段图像
"""
import numpy as np
import os
from osgeo import gdal
import tqdm


def readTiff(filename):
	"""
	:param filename:fileName
	:return: 读取的图像像素矩阵，投影信息，地理坐标信息
	"""
	dataset = gdal.Open(filename)
	width = dataset.RasterXSize
	height = dataset.RasterYSize
	proj = dataset.GetProjection()
	geotrans = dataset.GetGeoTransform()
	gdal_img_data = dataset.ReadAsArray(0, 0, width, height)
	return gdal_img_data, proj, geotrans


# 保存tif文件函数
def writeTiff(im_data, im_geotrans, im_proj, savepath):
	"""
	:param im_data: 需要保存的图像像素矩阵
	:param im_geotrans: 地理坐标信息
	:param im_proj: 投影信息
	:param savepath: 文件保存路径
	"""
	if 'int8' in im_data.dtype.name:
		datatype = gdal.GDT_Byte
	elif 'int16' in im_data.dtype.name:
		datatype = gdal.GDT_UInt16
	else:
		datatype = gdal.GDT_Float32
	if len(im_data.shape) == 3:
		im_bands, im_height, im_width = im_data.shape
	elif len(im_data.shape) == 2:
		im_data = np.array([im_data])
		im_bands, im_height, im_width = im_data.shape
	# 创建文件
	driver = gdal.GetDriverByName("GTiff")
	dataset = driver.Create(savepath, int(im_width), int(im_height), int(im_bands), datatype)
	if dataset is not None:
		dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
		dataset.SetProjection(im_proj)  # 写入投影
	for i in range(im_bands):
		dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
	del dataset


def band_separate(path_in, path_out):
	"""
	:param path_in: 要分离波段的原始图像数据名称
	:param path_out: 分离的各波段结果图像部分名称
	"""
	img, proj, geotrans = readTiff(path_in)
	# 依次将各波段输出
	for i in tqdm.trange(img.shape[0]):
		img_out = np.array(img[i, ::])
		# 保存tiff格式文件数据
		writeTiff(img_out, geotrans, proj, path_out + str(i) + '.tif')  # 输出波段的名称命名格式可以修改，结合传递的path2参数


if __name__ == '__main__':
	os.chdir(r'D:\RS_Toolbox')  # 改变当前工作目录
	tifName = r'out.tif'  # 要分离波段的原始图像数据名称
	outName = os.path.splitext(tifName)[0]
	band_separate(tifName, outName)
	print('Band separate END!')
