# -*- coding: utf-8 -*-
"""
PROJECT_NAME: RS_Toolbox 
FILE_NAME: RF 
AUTHOR: welt 
E_MAIL: tjlwelt@foxmail.com
DATE: 2023/7/1 
"""

# -*- coding: utf-8 -*-
import os
import sys

import numpy as np
from osgeo import gdal
from osgeo import ogr
from osgeo.gdal.gdalconst import *
from sklearn.ensemble import RandomForestClassifier


def read_img(filename):
    dataset = gdal.Open(filename)

    im_width = dataset.RasterXSize
    im_height = dataset.RasterYSize

    im_geotrans = dataset.GetGeoTransform()
    im_proj = dataset.GetProjection()
    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)

    del dataset
    return im_proj, im_geotrans, im_width, im_height, im_data


def write_img(filename, im_proj, im_geotrans, im_data):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape

    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

    dataset.SetGeoTransform(im_geotrans)
    dataset.SetProjection(im_proj)

    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i + 1).WriteArray(im_data[i])

    del dataset


def getPixels(shp, img):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(shp, 0)
    if ds is None:
        print('Could not open ' + shp)
        sys.exit(1)

    layer = ds.GetLayer()

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

    gdal.AllRegister()

    ds = gdal.Open(img, GA_ReadOnly)
    if ds is None:
        print('Could not open image')
        sys.exit(1)

    rows = ds.RasterYSize
    cols = ds.RasterXSize
    bands = ds.RasterCount

    transform = ds.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    values = []
    for i in range(len(xValues)):
        x = xValues[i]
        y = yValues[i]

        xOffset = int((x - xOrigin) / pixelWidth)
        yOffset = int((y - yOrigin) / pixelHeight)

        s = str(int(x)) + ' ' + str(int(y)) + ' ' + str(xOffset) + ' ' + str(yOffset) + ' '

        dt = ds.ReadAsArray(xOffset, yOffset, 1, 1)
        values.append(dt.flatten())
    return values


def array_change(inlist, outlist):
    for i in range(len(inlist[0])):
        outlist.append([j[i] for j in inlist])
    return outlist


def array_change2(inlist, outlist):
    for ele in inlist:
        for ele2 in ele:
            outlist.append(ele2)
    return outlist


def random_test(img_path, point_path, save_path):
    class_list = []
    label_list = []
    count = 0
    for shp in os.listdir(point_path):
        if shp[-4:] == '.shp':
            shp_full_path = os.path.join(point_path, shp)
            class_type = getPixels(shp_full_path, img_path)
            class_list += class_type
            label_list += [count] * len(class_type)
            count += 1

    arr = np.array(class_list)
    label = np.array(label_list)
    im_proj, im_geotrans, im_width, im_height, im_data = read_img(img_path)
    im_data = im_data.transpose((2, 1, 0))
    clf = RandomForestClassifier(n_estimators=100, max_depth=2, random_state=0)
    clf.fit(arr, label)
    img_arr_temp = im_data
    img_reshape = img_arr_temp.reshape([img_arr_temp.shape[0] * img_arr_temp.shape[1], img_arr_temp.shape[2]])
    seg = clf.predict(img_reshape)
    re = seg.reshape((img_arr_temp.shape[0], img_arr_temp.shape[1]))
    re = re.transpose((1, 0))
    write_img(save_path, im_proj, im_geotrans, re)


if __name__ == "__main__":
    img_path = "image.tif"
    point_path = "./point/"
    save_path = "result.tif"
    random_test(img_path, point_path, save_path)
