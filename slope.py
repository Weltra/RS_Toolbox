from osgeo import gdal
import os
import sys
from osgeo import osr, gdalconst
import math
import numpy as np


# 给栅格最外圈加一圈
def assignBCs(elevGrid):
	ny, nx = elevGrid.shape
	Zbc = np.zeros((ny + 2, nx + 2))
	Zbc[1:-1, 1:-1] = elevGrid

	Zbc[0, 1:-1] = elevGrid[0, :]
	Zbc[-1, 1:-1] = elevGrid[-1, :]
	Zbc[1:-1, 0] = elevGrid[:, 0]
	Zbc[1:-1, -1] = elevGrid[:, -1]

	Zbc[0, 0] = elevGrid[0, 0]
	Zbc[0, -1] = elevGrid[0, -1]
	Zbc[-1, 0] = elevGrid[-1, 0]
	Zbc[-1, -1] = elevGrid[-1, 0]

	return Zbc


# 计算dx,dy
def calcFiniteSlopes(elevGrid, dx):
	Zbc = assignBCs(elevGrid)

	Sx = (Zbc[1:-1, :-2] - Zbc[1:-1, 2:]) / (2 * dx)  # WE方向
	Sy = (Zbc[2:, 1:-1] - Zbc[:-2, 1:-1]) / (2 * dx)  # NS方向

	return Sx, Sy


# 投影转换
def convertProjection(data, filename, dx):
	landsatData = gdal.Open(filename, gdal.GA_ReadOnly)

	oldRef = osr.SpatialReference()
	oldRef.ImportFromWkt(data.GetProjectionRef())

	newRef = osr.SpatialReference()
	newRef.ImportFromWkt(landsatData.GetProjectionRef())

	transform = osr.CoordinateTransformation(oldRef, newRef)

	tVect = data.GetGeoTransform()
	nx, ny = data.RasterXSize, data.RasterYSize
	(ulx, uly, ulz) = transform.TransformPoint(tVect[0], tVect[3])
	(lrx, lry, lrz) = transform.TransformPoint(tVect[0] + tVect[1] * nx, tVect[3] + tVect[5] * ny)

	memDrv = gdal.GetDriverByName('MEM')

	dataOut = memDrv.Create('name', int((lrx - ulx) / dx), int((uly - lry) / dx), 1, gdal.GDT_Float32)

	newtVect = (ulx, dx, tVect[2], uly, tVect[4], -dx)

	dataOut.SetGeoTransform(newtVect)
	dataOut.SetProjection(newRef.ExportToWkt())

	# Perform the projection/resampling
	res = gdal.ReprojectImage(data, dataOut, oldRef.ExportToWkt(), newRef.ExportToWkt(), gdal.GRA_Cubic)

	return dataOut


def Slope(DEMFilename, slopeFilename, aspectFilename):
	gdal.AllRegister()

	data = gdal.Open(DEMFilename, gdal.GA_ReadOnly)
	if data is None:
		print('Cannot open this file:' + DEMFilename)
		sys.exit(1)

	dx = 30  # 设置分辨率

	# 投影变换
	projData = convertProjection(data, DEMFilename, dx)
	projinfo = data.GetProjection()
	geotransform = data.GetGeoTransform()

	gridNew = projData.ReadAsArray().astype(np.float)

	Sx, Sy = calcFiniteSlopes(gridNew, dx)
	# 坡度计算
	slope = np.arctan(np.sqrt(Sx ** 2 + Sy ** 2)) * 57.29578

	# 坡向计算
	aspect = np.ones([Sx.shape[0], Sx.shape[1]]).astype(np.float32)
	for i in range(Sx.shape[0]):
		for j in range(Sy.shape[1]):
			sx = float(Sx[i, j])
			sy = float(Sy[i, j])
			if (sx == 0.0) & (sy == 0.0):
				aspect[i, j] = -1
			elif sx == 0.0:
				if sy > 0.0:
					aspect[i, j] = 0.0
				else:
					aspect[i, j] = 180.0
			elif sy == 0.0:
				if sx > 0.0:
					aspect[i, j] = 90.0
				else:
					aspect[i, j] = 270.0
			else:
				aspect[i, j] = float(math.atan2(sy, sx) * 57.29578)
				if aspect[i, j] < 0.0:
					aspect[i, j] = 90.0 - aspect[i, j]
				elif aspect[i, j] > 90.0:
					aspect[i, j] = 360.0 - aspect[i, j] + 90.0
				else:
					aspect[i, j] = 90.0 - aspect[i, j]

	# 输出坡度坡向文件
	driver = gdal.GetDriverByName('GTiff')
	if os.path.exists(slopeFilename):
		os.remove(slopeFilename)
	if os.path.exists(aspectFilename):
		os.remove(aspectFilename)

	ds1 = driver.Create(slopeFilename, slope.shape[1], slope.shape[0], 1, gdal.GDT_Float32)
	ds1.SetGeoTransform(geotransform)
	ds1.SetProjection(projinfo)
	band = ds1.GetRasterBand(1)
	band.WriteArray(slope, 0, 0)

	ds2 = driver.Create(aspectFilename, aspect.shape[1], aspect.shape[0], 1, gdal.GDT_Float32)
	ds2.SetGeoTransform(geotransform)
	ds2.SetProjection(projinfo)
	band = ds2.GetRasterBand(1)
	band.WriteArray(aspect, 0, 0)
	del ds1
	del ds2


if __name__ == '__main__':
	DEMFilename = "D:\RS_3\数据\XianAn_DEM.tif"
	slopeFilename = "D:\RS_3\数据\XianAn_DEM_Slope.tif"
	aspectFilename = "D:\RS_3\数据\XianAn_DEM_Aspect.tif"
	Slope(DEMFilename, slopeFilename, aspectFilename)
