from osgeo import gdal


def resample_images(referencefilePath, inputfilePath, outputfilePath):  # 影像重采样
	"""
	:param referencefilePath: 重采样参考文件路径
	:param inputfilePath: 输入路径
	:param outputfilePath: 输出路径
	"""
	# 获取参考影像信息, 其实可以自定义这些信息，有参考的话就不用查这些参数了
	referencefile = gdal.Open(referencefilePath, gdal.GA_ReadOnly)
	referencefileProj = referencefile.GetProjection()
	referencefiletrans = referencefile.GetGeoTransform()
	bandreferencefile = referencefile.GetRasterBand(1)
	width = referencefile.RasterXSize
	height = referencefile.RasterYSize
	# 获取输入影像信息
	inputrasfile = gdal.Open(inputfilePath, gdal.GA_ReadOnly)  # 打开输入影像
	inputProj = inputrasfile.GetProjection()  # 获取输入影像的坐标系
	bands = inputrasfile.RasterCount
	# 创建重采样输出文件（设置投影及六参数）
	driver = gdal.GetDriverByName('GTiff')  # 这里需要定义，如果不定义自己运算会大大增加运算时间
	output = driver.Create(outputfilePath, width, height, bands, bandreferencefile.DataType)  # 创建重采样影像
	output.SetGeoTransform(referencefiletrans)  # 设置重采样影像的仿射矩阵为参考面的仿射矩阵
	output.SetProjection(referencefileProj)  # 设置重采样影像的坐标系为参考面的坐标系
	# 参数说明 输入数据集、输出文件、输入投影、参考投影、重采样方法(最邻近内插\双线性内插\三次卷积等)、回调函数
	gdal.ReprojectImage(inputrasfile, output, inputProj, referencefileProj, gdal.GRA_Bilinear, 0.0, 0.0, )


if __name__ == "__main__":
	inputfilePath = 'D:\RS_Toolbox\DJKS_dem_12.5m.tif'  # 输入文件
	outputfilePath = 'D:\RS_Toolbox\DJKS_dem_2m.tif'  # 输出文件
	referencePath = 'D:\RS_Toolbox\image.tif'  # 重采样参考文件
	resample_images(referencePath, inputfilePath, outputfilePath)
