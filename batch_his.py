# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: batch_his 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2022/11/1 
"""
import os
import re
import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal

# 通过GDAL读取栅格影像
filepath = 'D:/RS_Toolbox/slope'
filelist = os.listdir(filepath)
for file in filelist:
	(name, extension) = os.path.splitext(file)
	filename = filepath + '/' + file
	dataset = gdal.Open(filename)
	im_width = dataset.RasterXSize
	im_height = dataset.RasterYSize
	im_data = dataset.ReadAsArray(0, 0, im_width, im_height)
	print(im_data.shape)

	# 显示灰度直方图
	# 遍历影像中的每一个像元的像元值
	data = []
	for i in range(im_data.shape[0]):
		for j in range(im_data.shape[1]):
			if im_data[i][j] > 0:
				data.append(im_data[i][j])
	data.sort()

	# 统计最大最小值
	data = np.array(data)
	mean_value = np.mean(data)
	variance = np.std(data)
	print(name)
	print("平均值: ", mean_value)
	print("方差: ", variance)
	print("最小值: ", data.min())
	print("最大值: ", data.max())

	# 根据影像中最大最小值设定坐标轴
	bins = np.linspace(data.min(), data.max(), 100)
	resolution = re.findall(r"\d+\.?\d*", name)
	# 绘制直方图，设定直方图颜色
	plt.hist(data, bins, facecolor="blue")
	# 横坐标轴名称
	plt.xlabel('像元值')
	# 纵坐标轴名称
	plt.ylabel('频数')
	# 图表头名称
	plt.title(resolution[0] + 'm分辨率坡度数据的' + '灰度分布直方图')
	# 显示中文字体
	plt.rcParams["font.sans-serif"] = ["SimHei"]
	plt.rcParams['axes.unicode_minus'] = False
	# 导出绘制得到的图片
	plt.tight_layout()
	plt.savefig(name + '.jpg')
	plt.show()
