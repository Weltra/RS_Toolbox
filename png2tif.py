"""
time: 2022-09-05
coder: welt
reference:
无空间参考的PNG格式文件转有空间参考的TIF文件
"""

from osgeo import gdal
import os
import numpy as np
import cv2

'''
input:原图的tif文件和预测的单通道png图像
out:合成新的tif,带有坐标信息
'''


class GRID:

	# 读图像文件
	def read_img(self, filename):
		dataset = gdal.Open(filename)  # 打开文件

		im_width = dataset.RasterXSize  # 栅格矩阵的列数
		im_height = dataset.RasterYSize  # 栅格矩阵的行数

		im_geotrans = dataset.GetGeoTransform()  # 仿射矩阵
		im_proj = dataset.GetProjection()  # 地图投影信息
		im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 将数据写成数组，对应栅格矩阵

		del dataset  # 关闭对象，文件dataset
		return im_proj, im_geotrans, im_data, im_width, im_height

	# 写文件，以写成tif为例
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


if __name__ == "__main__":
	os.chdir(r'./data')  # 切换路径到待处理图像所在文件夹
	run = GRID()
	# 第一步
	proj, geotrans, data1, row1, column1 = run.read_img('pic_2.tif')  # 读数据,获取tif图像的信息

	img_path = 'pic_2.png'  # 读取png图像数据
	data2 = cv2.imread(img_path, -1)

	data = np.array((data2), dtype=data1.dtype)  # 数据格式

	run.write_img('pic_2_tif.tif', proj, geotrans, data)  # 生成tif
