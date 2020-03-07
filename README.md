# Image-Compression-and-Decompression

图像的压缩与解压缩—Python实现

此项目为《多媒体基础》课程的期末大作业, 主要实现了JPEG标准的图像压缩与解压缩过程.

## 项目所含文件说明：

decode.py: 读取图像文件"lena.jpg"，将其进行JPEG压缩，然后将得到的二进制位流存储到文件"encode.txt".

decode.py : 从文件"encode.txt"读取压缩的图像位流，将其恢复成图像并存储为图像"lena_re.jpg".

parameters.py : 保存亮度、色度量化表和霍夫曼编码表.

lena.jpg : 用于压缩的图像样例

encode.txt : 用于存储图像压缩后返回的二进制位流

lena_re.jpg : 压缩后的二进制位流恢复成的重构图像

## JPEG标准的图像压缩步骤：

读取图像文件 -> RGB颜色空间转化为YUV -> 图像分块 -> 前向DCT变换 -> 量化 -> 编码 -> 二进制流存储到文件.

## JPEG标准的图像解压缩步骤：

读取二进制流文件 -> 解码 -> 反量化 -> 逆向DCT变换 -> 合并图像块 -> YUV颜色空间转换为RGB -> 存储为图像文件.

## 主要函数说明：

### encode.py文件中的函数说明：

### decode.py文件中的函数说明：
