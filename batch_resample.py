# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: batch_resample
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2022/10/31 
"""

from osgeo import gdal
import os
import numpy as np

path = r"D:\RS_Toolbox"
os.chdir(path)
image_name = '1269.tif'

times = [2, 4, 8]
for time in times:
    in_ds = gdal.Open(image_name)
    geotrans = list(in_ds.GetGeoTransform())
    geotrans[1] *= time  # 像元宽度变为原来的两倍
    geotrans[5] *= time  # 像元高度也变为原来的两倍
    in_band = in_ds.GetRasterBand(1)
    xsize = in_band.XSize
    ysize = in_band.YSize
    x_resolution = int(xsize / time)  # 影像的行列都变为原来的一半
    y_resolution = int(ysize / time)
    (filename, extension) = os.path.splitext(image_name)
    outname = filename + '_' + str(5 * time) + 'm' + extension
    if os.path.exists(outname):
        # 如果存在重采样后的影像，则删除之
        os.remove(outname)
    out_ds = in_ds.GetDriver().Create(outname, x_resolution, y_resolution, 1,
                                      in_band.DataType)
    out_ds.SetProjection(in_ds.GetProjection())  # 设置投影信息
    out_ds.SetGeoTransform(geotrans)  # 设置地理变换信息
    data = np.empty((y_resolution, x_resolution), np.int)  # 设置一个与重采样影像行列号相等的矩阵去接受读取所得的像元值
    in_band.ReadAsArray(buf_obj=data)
    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(data)
    out_band.FlushCache()
    out_band.ComputeStatistics(False)  # 计算统计信息
    out_ds.BuildOverviews('average', [1, 2, 4, 8, 16, 32])  # 构建金字塔
    del in_ds
    del out_ds
    print("This process has succeeded!")
