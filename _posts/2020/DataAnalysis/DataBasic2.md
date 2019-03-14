---
layout: post
title: 数据基础知识（二）
date: 2019-02-12
author: lyton
tags: 数据转换
---
### 数据转换
>了解数据数据变换的基础知识，参看以下两篇blog

* [概率论：均值，方差，协方差](https://blog.csdn.net/pipisorry/article/details/48788671)
* [矩阵论：向量范数和矩阵范数](https://blog.csdn.net/pipisorry/article/details/51030563)

数据科学以数据为主，那么数据间的量纲会影响数据彼此之间的比较和加权，所以进行数据标准化，至关重要。

#### 数据标准化和归一化
数据标准化（normalization）是将数据按比例缩放，使之落入一个小的特定空间。在某些比较和评价的指标处理中会经常用到，去除单位限制，将其转化为无量纲的纯数值，便于不同单位或量级指标能够进行比较和加权。其中比较典型的方法就是数据归一化处理，将数据映射到[0，1]空间上。

!["data_All"](/assets/img/2020/DataAnalysis/ data-standardization.png)

具体代码可以参考sklearn中的示例代码。
