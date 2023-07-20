# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: Band_merge 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2022/10/20
功能: 批量合成同日期同区域多波段影像的指定波段，且各两幅影像波段数目不同
要求: 两批文件夹下影像日期需要对应，空间分辨率、影像大小需要一致
"""
import glob
# 载入相关库
import os

from osgeo import gdal, gdalconst


def SynthesisBands(dstlist1, dstlist2, dstlist3, outfile_dir):
	"""
	将多光谱波段合成一个tif
	:param dstlist1: 需要合并的第一幅影像
	:param dstlist2: 需要合并的第二幅影像
	:param dstlist3: 需要合并的第二幅影像
	:param outfile_dir: 影像的输出文件地址
	"""
	# 检测数据并读取波段信息
	# 第一幅影像
	dataset1 = gdal.Open(dstlist1, gdalconst.GA_ReadOnly)
	# print(dataset)
	file1_band_count = dataset1.RasterCount  # 波段数
	print(file1_band_count)
	if file1_band_count == 0:
		print("参数异常")
		return
	# 第二幅影像
	dataset2 = gdal.Open(dstlist2, gdalconst.GA_ReadOnly)
	# print(dataset)
	file2_band_count = dataset2.RasterCount  # 波段数
	print(file2_band_count)
	if file2_band_count == 0:
		print("参数异常")
		return
	# 因为实验需要只提取第二幅影像前6个波段，故在这里重新设置
	file2_band_count = 6

	# 获取栅格信息，并判断是否可以合成栅格数据
	# 获取第一幅栅格行列数
	file1_cols = dataset1.RasterXSize  # 列数
	file1_rows = dataset1.RasterYSize  # 行数
	# 获取第二幅栅格行列数
	file2_cols = dataset2.RasterXSize  # 列数
	file2_rows = dataset2.RasterYSize  # 行数
	# 判断是否可以合成
	if (file1_cols != file2_cols) or (file1_rows != file2_rows):
		print("影像不匹配")
		# 测试代码
		# print(file1_cols != file2_cols)
		# print(file1_cols)
		# print(file2_cols)
		return

	# 创建输出栅格
	First_Layer_1 = dataset1.GetRasterBand(1)
	data_type = First_Layer_1.DataType
	# 输出栅格总波段
	total_bands = file1_band_count + file2_band_count
	print("输出栅格总波段数为：" + str(total_bands))
	target = dataset1.GetDriver().Create(outfile_dir,
	                                     xsize=file1_cols,
	                                     ysize=file1_rows,
	                                     bands=total_bands,
	                                     eType=data_type)
	target.SetProjection(dataset1.GetProjection())  # 设置投影坐标
	geotrans = list(dataset1.GetGeoTransform())
	target.SetGeoTransform(geotrans)  # 设置地理变换参数

	for index in range(1, total_bands + 1):
		# 读取波段数据
		print("正在写入" + str(index) + "波段")
		# 判断输入哪一幅栅格的数据
		if index > file1_band_count:
			real_index = index - file1_band_count
			data = dataset2.GetRasterBand(real_index).ReadAsArray(buf_xsize=file2_cols,
			                                                      buf_ysize=file2_cols)
			if dataset2.GetRasterBand(real_index).GetNoDataValue() != None:
				out_band.SetNoDataValue(
					dataset2.GetRasterBand(real_index).GetNoDataValue())
		else:
			real_index = index
			data = dataset1.GetRasterBand(real_index).ReadAsArray(buf_xsize=file1_cols,
			                                                      buf_ysize=file1_cols)
		# 设置输出的栅格数据
		out_band = target.GetRasterBand(index)

		out_band.WriteArray(data)  # 写入数据到新影像中
		out_band.FlushCache()
		out_band.ComputeBandStats(False)  # 计算统计信息
	print("正在写入完成")
	del dataset1
	del dataset2
	del target


if __name__ == "__main__":
	"""
	变量说明：
	Input1_Path: 存放第一批影像 这里是2021年含有B2、3、4、8的sentinel-2影像文件夹
	Input2_Path: 存放第二批影像 这里是2021年含有B5、6、7、8A、11、12、AOT等波段的sentinel-2影像文件夹
	"""
	Input1_Path = r'F:\graduate\Data\T49RGP\10m_20m'
	Input2_Path = r'F:\graduate\Data\T49RGP\20m'
	# 获取文件夹下的所有栅格影像
	data1_list = glob.glob(Input1_Path + "\\*.tif")
	data2_list = glob.glob(Input2_Path + "\\*.tif")
	# 输出文件夹
	out_path = r'F:\graduate\Data\T49RGP\outlist'

	for i in range(len(data1_list)):
		# 获取第一幅影像的目录
		data1_path = data1_list[i]
		# 获取第二幅影像的目录
		data2_path = data2_list[i]
		# 获取影像名称
		filename = os.path.basename(data1_path)
		# 将输出文件夹和影像名称组合，得到输出目录
		outfile_path = out_path + "\\" + filename
		# 调用合成波段函数
		SynthesisBands(data1_path, data2_path, data2_path, outfile_path)
		# 打印合成进度
		print(outfile_path + "-----不同栅格波段合成成功")
	print("Congratulations! ----合成结束----")
