"""
time: 2022-07-16
coder: welt
"""
import numpy as np
import sklearn
from osgeo import gdal
from sklearn.linear_model import LinearRegression
from tqdm import tqdm
from scipy.stats import f


def regression(x, y):
    """
    X为n行2列的numpy数组，n为年份数，第一列为气温，第二列为降水
    Y为目标：n个元素的numpy数组，为NDVI
    """
    regr = sklearn.linear_model.LinearRegression()
    regr.fit(x, y)
    a, b = regr.coef_
    c = regr.intercept_
    return a, b, c


def erhuigui(ndvipath, temppath, rainpath, outtif):
    """
    :param ndvipath:NDVI的文件路径
    :param temppath:温度的文件路径
    :param rainpath:降水量的文件路径
    :param outtif:输出结果的文件路径
    """
    dataset = gdal.Open(ndvipath)
    projinfo = dataset.GetProjection()
    geotransform = dataset.GetGeoTransform()

    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    depth = dataset.RasterCount
    rows = int(dataset.RasterYSize)
    colmns = int(dataset.RasterXSize)

    ndvi = dataset.ReadAsArray()
    src2 = gdal.Open(temppath)
    temp = src2.ReadAsArray()

    src3 = gdal.Open(rainpath)
    rain = src3.ReadAsArray()

    dst_ds1 = driver.Create(outtif, colmns, rows, 3 + depth + 1,
                            gdal.GDT_Float32)
    # predict = np.zeros((depth, rows, colmns))
    Residual = np.zeros((depth, rows, colmns))
    y_pre = np.zeros(depth)
    p_value = np.zeros((rows, colmns))
    dst_ds1.SetGeoTransform(geotransform)
    dst_ds1.SetProjection(projinfo)
    d0 = ndvi[0]
    out_a = d0 * 0 - 2222.0
    out_b = d0 * 0 - 2222.0
    out_c = d0 * 0 - 2222.0
    # 开始计算
    for row in tqdm(range(rows)):
        for col in range(colmns):
            y = ndvi[:, row, col] * 1.0
            x1 = temp[:, row, col] * 1.0
            x2 = rain[:, row, col] * 1.0
            x = np.vstack([x1, x2]).T
            a, b, c = -2222, -2222, -2222
            if (np.array(x) > -9999).all() and (np.array(y) > -9999).all():
                try:
                    a, b, c = regression(x, y)
                except:
                    pass
                out_a[row, col], out_b[row, col], out_c[row, col] = a, b, c
                for d in range(depth):
                    # predict[d, row, col] = a * x1[d] + b * x2[d] + c
                    Residual[d, row, col] = y[d] - (a * x1[d] + b * x2[d] + c)
                    y_pre[d] = a * x1[d] + b * x2[d] + c

                # 计算组内样本方差
                var1 = np.var(y, ddof=1)
                var2 = np.var(y_pre, ddof=1)
                # 计算统计量F
                F = var1 / var2
                # 计算自由度
                df1 = len(x) - 1
                df2 = len(y) - 1
                # 计算p值
                p_value[row, col] = 1 - 2 * abs(0.5 - f.cdf(F, df1, df2))

    '''
    将a,b,c,预测值,p值写入图像中
    波段顺序为a,b,c,残差,p值
    '''
    dst_ds1.GetRasterBand(1).WriteArray(out_a)
    dst_ds1.GetRasterBand(2).WriteArray(out_b)
    dst_ds1.GetRasterBand(3).WriteArray(out_c)
    '''
    求每个时期的预测值
    for i in range(depth):
        dst_ds1.GetRasterBand(3 + i).WriteArray(predict[i])
    '''
    for i in range(depth):
        dst_ds1.GetRasterBand(3 + i).WriteArray(Residual[i])
    dst_ds1.GetRasterBand(3 + depth + 1).WriteArray(p_value)
    dst_ds1.GetRasterBand(1).SetNoDataValue(-2222)
    dst_ds1.GetRasterBand(2).SetNoDataValue(-2222)
    dst_ds1.GetRasterBand(3).SetNoDataValue(-2222)
    for i in range(depth):
        dst_ds1.GetRasterBand(3 + i).SetNoDataValue(-2222)
    dst_ds1.GetRasterBand(3 + depth + 1).SetNoDataValue(-2222)


if __name__ == "__main__":
    # 修改路径
    NDVIPath = r"jiusan_NDVI.tif"  # 植被覆盖度路径
    TempPath = r"jiusan_temp.tif"  # 气温路径
    RainPath = r"jiusan_rain.tif"  # 降水路径
    OutTif = r"out.tif"
    erhuigui(NDVIPath, TempPath, RainPath, OutTif)
