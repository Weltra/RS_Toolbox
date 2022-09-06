"""
time: 2022-08-02
coder: welt
"""
import numpy as np
import sklearn
from osgeo import gdal
from sklearn.linear_model import LinearRegression
from tqdm import tqdm
from scipy.stats import f
from sklearn.metrics import r2_score


def regression(x, y):
    """
    X为n行的numpy数组,即自变量
    Y为目标：n个元素的numpy数组，即因变量
    """
    regr = sklearn.linear_model.LinearRegression()
    regr.fit(x, y)
    a = regr.coef_
    c = regr.intercept_
    return a, c


def erhuigui(ndvipath, temppath, outtif):
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

    dst_ds1 = driver.Create(outtif, colmns, rows, 4,
                            gdal.GDT_Float32)
    # predict = np.zeros((depth, rows, colmns))
    y_pre = np.zeros(depth)
    p_value = np.zeros((rows, colmns))
    r2 = np.zeros((rows, colmns))
    dst_ds1.SetGeoTransform(geotransform)
    dst_ds1.SetProjection(projinfo)
    d0 = ndvi[0]
    out_a = d0 * 0 - 2222.0
    out_c = d0 * 0 - 2222.0

    # 开始计算
    for row in tqdm(range(rows)):
        for col in range(colmns):
            y = ndvi[:, row, col] * 1.0
            x1 = temp[:, row, col] * 1.0
            y = y.reshape(-1, 1)
            x = x1
            x = x.reshape(-1, 1)
            a, c = -2222, -2222
            if (np.array(x) > -9999).all() and (np.array(y) > -9999).all():
                try:
                    a, c = regression(x, y)
                except:
                    pass
                out_a[row, col], out_c[row, col] = a, c
                for d in range(depth):
                    # predict[d, row, col] = a * x1[d] + c
                    y_pre[d] = a * x1[d] + c

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
                r2[row, col] = r2_score(y, y_pre)

    '''
    将a,b,c,预测值,p值写入图像中
    波段顺序为a,c,p值,r2
    '''
    dst_ds1.GetRasterBand(1).WriteArray(out_a)
    dst_ds1.GetRasterBand(2).WriteArray(out_c)
    '''
    for i in range(depth):
        dst_ds1.GetRasterBand(2 + i).WriteArray(predict[i])
    '''
    '''
    for i in range(depth):
        dst_ds1.GetRasterBand(2 + i).WriteArray(predict[i])
    '''
    dst_ds1.GetRasterBand(3).WriteArray(p_value)
    dst_ds1.GetRasterBand(4).WriteArray(r2)
    dst_ds1.GetRasterBand(1).SetNoDataValue(-2222)
    dst_ds1.GetRasterBand(2).SetNoDataValue(-2222)
    '''
    for i in range(depth):
        dst_ds1.GetRasterBand(2 + i).SetNoDataValue(-2222)
    '''
    dst_ds1.GetRasterBand(3).SetNoDataValue(-2222)
    dst_ds1.GetRasterBand(4).SetNoDataValue(-2222)


if __name__ == "__main__":
    # 修改路径
    NDVIPath = r"GMMg2000_2005.tif"  # 植被覆盖度路径
    TempPath = r"MODIS2000_2005.tif"  # 气温路径
    # RainPath = r"E:\forest\NDVI_temp_rain\result\rain2000_2005.tif"  # 降水路径
    OutTif = r"out.tif"
    erhuigui(NDVIPath, TempPath, OutTif)
