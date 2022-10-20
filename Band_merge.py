# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: Band_merge 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2022/10/20 
"""

import os
from osgeo import gdal


def get_dataset_band(bandfile):
	"""获取dataset并获取dataset的一个band"""
	input_dataset = gdal.Open(bandfile)
	input_band = input_dataset.GetRasterBand(1)

	return [input_dataset, input_band]


def main():
	# 1. 定义默认路径并导入文件
	os.chdir(r'D:\Random_Forest\data')
	bandfile_1 = '202004.TIF'
	bandfile_2 = '202005.TIF'
	bandfile_3 = '202006.TIF'
	bandfile = [bandfile_1, bandfile_2, bandfile_3]

	# 2. 读取dataset并获取band值
	inputdata = []
	for i in range(3):
		inputdata.append(get_dataset_band(bandfile[i]))
	inputdataset_1, inputband_1 = inputdata[0]

	# 3. 创建dataset（要输出的dataset）
	file_driver = gdal.GetDriverByName('Gtiff')
	output_dataset = file_driver.Create(
		'natural_color.tif', inputband_1.XSize, inputband_1.YSize, 3, inputband_1.DataType
	)
	output_dataset.SetProjection(inputdataset_1.GetProjection())
	output_dataset.SetGeoTransform(inputdataset_1.GetGeoTransform())

	# 4. 写入数据
	for i in range(3):
		inputband_data = inputdata[i][1].ReadAsArray()
		output_dataset.GetRasterBand(i + 1).WriteArray(inputband_data)

	# 5. 后续处理
	output_dataset.FlushCache()  # 刷新缓存，确保数据写入硬盘
	output_dataset.BuildOverviews('average', [2, 4, 8, 16, 32])  # 建立快速显示金字塔


if __name__ == '__main__':
	main()
