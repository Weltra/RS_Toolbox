# 读取矢量
from osgeo import ogr
import os, sys

# 改变工作空间
os.chdir('D:\RS_Toolbox')

# 获取矢量点位的经纬度
# 设置driver
driver = ogr.GetDriverByName('ESRI Shapefile')
# 打开矢量
ds = driver.Open('sites.shp', 0)
if ds is None:
	print('Could not open ' + 'sites.shp')
sys.exit(1)
# 获取图层
layer = ds.GetLayer()

# 获取要素及要素地理位置
xValues = []
yValues = []
feature = layer.GetNextFeature()
while feature:
	geometry = feature.GetGeometryRef()
	x = geometry.GetX()
	y = geometry.GetY()
	xValues.append(x)
	yValues.append(y)
	feature = layer.GetNextFeature()

# 获取点位所在像元的栅格值
# 读取栅格
from osgeo import gdal
import os, sys

# 获取注册类
gdal.AllRegister()
# 打开栅格数据
ds = gdal.Open('aster.img', GA_ReadOnly)
if ds is None:
	print('Could not open image')
sys.exit(1)
# 获取行列、波段
rows = ds.RasterYSize
cols = ds.RasterXSize
bands = ds.RasterCount
# 获取放射变换信息
transform = ds.GetGeoTransform()
xOrigin = transform[0]
yOrigin = transform[3]
pixelWidth = transform[1]
pixelHeight = transform[5]
#
values = []
for i in range(len(xValues)):
	x = xValues[i]
y = yValues[i]
# 获取点位所在栅格的位置
xOffset = int((x - xOrigin) / pixelWidth)
yOffset = int((y - yOrigin) / pixelHeight)

s = str(int(x)) + ' ' + str(int(y)) + ' ' + str(xOffset) + ' ' + str(yOffset) + ' '
# 提取每个波段上对应的像元值
for j in range(bands):
	band = ds.GetRasterBand(j + 1)
data = band.ReadAsArray(xOffset, yOffset, 1, 1)
value = data[0, 0]
s = s + str(value) + ' '
print(s)
values.append(s)
