# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox
FILE_NAME: get_value_by_location
AUTHOR: welt
E_MAIL: tjlwelt@foxmail.com
DATE: 2023/3/28
"""

import os
import os.path as path

import matplotlib.pyplot as plt
import numpy as np
import xlrd
from osgeo import gdal
from osgeo import osr
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression
from scipy.stats import stats
import seaborn as sns
import pandas as pd


def get_img_value(wdrvi_path, lon_lat):
	"""
	:param wdrvi_path: 图像地址
	:param lon_lat: 要获取位置的经纬度
	:return: 获取的值
	"""
	# 读入数据
	dataset = gdal.Open(wdrvi_path)
	img = dataset.ReadAsArray()
	pcs = osr.SpatialReference()
	pcs.ImportFromWkt(dataset.GetProjection())
	gcs = pcs.CloneGeogCS()
	extend = dataset.GetGeoTransform()

	ct = osr.CoordinateTransformation(gcs, pcs)
	coordinate = ct.TransformPoint(lon_lat[0], lon_lat[1])

	# 地理坐标系转投影坐标系
	p_x = np.array([[extend[1], extend[2]], [extend[4], extend[5]]])
	p_y = np.array([coordinate[0] - extend[0], coordinate[1] - extend[3]])
	# 投影坐标系转图像坐标系
	row_col = np.linalg.solve(p_x, p_y)
	row = int(float(row_col[1]))
	col = int(float(row_col[0]))
	img_value = img[row, col]
	return img_value


def get_data(_modis_path, xls_path, loc):
	"""
	:param _modis_path: 图像文件夹地址
	:param xls_path: LAI文件地址
	:param loc: 要获取的经纬度
	:return:
	"""
	# 获取img文件列表
	img_path = []
	for i in os.listdir(_modis_path):
		if path.splitext(i)[1] == '.img':
			img_path.append(path.join(_modis_path, i))
	# 获取LAI值和对应时间
	data_dict = {'LAI_Value': [],
	             'LAI_Date': [],
	             'WDRVI_Path': [],
	             'WDRVI_Value': []}
	wb = xlrd.open_workbook(xls_path)
	ws = wb.sheet_by_index(0)
	for i in range(0, ws.nrows, 2):
		tmp_list1 = ws.row_values(rowx=i, start_colx=3)
		tmp_list2 = ws.row_values(rowx=i + 1, start_colx=3)
		while '' in tmp_list1:
			tmp_list1.remove('')
		while '' in tmp_list2:
			tmp_list2.remove('')
		data_dict['LAI_Value'] += tmp_list1
		data_dict['LAI_Date'] += tmp_list2
		for m in tmp_list2:
			for n in img_path:
				x, y = int(m[0:3]), int(n[-17:-14])
				if 0 <= (x - y) < 8:
					data_dict['WDRVI_Path'].append(n)
					data_dict['WDRVI_Value'].append(get_img_value(n, loc))
					break
	return data_dict


if __name__ == "__main__":
	modis_path = r"D:\Download\实验一\数据\MODIS"
	xls_path = r"D:\Download\实验一\数据\LAI.xls"
	loc = [-96.476639, 41.165056]
	data = get_data(modis_path, xls_path, loc)
	# 利用SG滤波库savgol_filter
	x = range(len(data['LAI_Date']))
	y1 = data['WDRVI_Value']
	plt.plot(x, y1, color='#336699')
	plt.title('The original WDRVI time series')
	plt.ylabel('WDRVI')
	plt.show()
	y2 = savgol_filter(y1, window_length=7, polyorder=2)
	plt.plot(x, y1, color='y', label='pre_filter data')
	plt.plot(x, y2, "b--", label="sg result")
	plt.legend(loc='lower right')
	plt.title('Result of SG Filter')
	plt.show()

	# 皮尔逊相关系数检验
	r, p_value = stats.pearsonr(y1, y2)  # 计算CRIM和target之间的相关系数和对应的显著性
	print('相关系数为{:.3f},p值为{:.5f}'.format(r, p_value))  # 相关系数保留3位小数，p值保留5位小数

	# 绘制基本统计量的图表
	sg_WDRVI = np.array(y2).reshape(-1, 1)
	LAI_value = np.array(data['LAI_Value'])
	plt.plot(x, LAI_value, color="y")
	plt.title('LAI time series')
	plt.ylabel('LAI')
	plt.show()
	LAI_value_r = LAI_value.reshape(-1, 1)
	data_array = np.hstack([sg_WDRVI, LAI_value_r])
	data_frame = pd.DataFrame(data_array, index=None, columns=['WDRVI', 'LAI'])
	sns.set(style="ticks", color_codes=True)
	plt.figure(dpi=500)
	sns.pairplot(data=data_frame, vars=['WDRVI', 'LAI'])  # 绘制WDRVI和LAI的散点图与直方图
	plt.show()
	plt.savefig('fig.png')  # 绘图结果存到本地
	cmap = sns.diverging_palette(230, 20, as_cmap=True)
	sns.heatmap(data_frame.corr(method='pearson'), cmap=cmap, vmax=1, center=0.95,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
	plt.title('Pearson correlation coefficient Matrix')
	plt.show()
	plt.savefig('fig1.png')  # 绘图结果存到本地

	# 一元线性回归
	model = LinearRegression()
	model.fit(sg_WDRVI, LAI_value)
	print('coefficient of determination: {}\n'
	      'intercept: {}\n'
	      'slope: {}'.format(model.score(sg_WDRVI, LAI_value), model.intercept_, model.coef_[0]))
	y = model.coef_[0] * sg_WDRVI + model.intercept_
	plt.scatter(sg_WDRVI, LAI_value, label='raw data', color='r')
	plt.legend(loc='lower right')
	plt.plot(sg_WDRVI, y, label='fitting', color='b')
	plt.legend(loc='lower right')
	plt.title('Result of Linear Regression')
	plt.xlabel('WDRVI')
	plt.ylabel('LAI')
	plt.show()
