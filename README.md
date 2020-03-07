# Image-Compression-and-Decompression

图像的压缩与解压缩—Python实现

此项目为《多媒体基础》课程的期末大作业, 主要实现了JPEG标准的图像压缩与解压缩过程.

## 项目所含文件说明：

decode.py: 读取图像文件"lena.jpg"，将其进行JPEG压缩，然后将得到的二进制位流存储到文件"encode.txt".

decode.py : 从文件"encode.txt"读取压缩的图像位流，将其恢复成图像并存储为图像"lena_re.jpg".

parameters.py : 保存亮度、色度量化表和霍夫曼编码表.

lena.jpg : 用于压缩的图像样例.

encode.txt : 用于存储图像压缩后返回的二进制位流.

lena_re.jpg : 压缩后的二进制位流恢复成的重构图像.

## JPEG标准的图像压缩步骤：

读取图像文件 -> RGB颜色空间转化为YUV -> 图像分块 -> 前向DCT变换 -> 量化 -> 编码 -> 二进制流存储到文件.

## JPEG标准的图像解压缩步骤：

读取二进制流文件 -> 解码 -> 反量化 -> 逆向DCT变换 -> 合并图像块 -> YUV颜色空间转换为RGB -> 存储为图像文件.

## 主要函数说明：

### encode.py文件中的主要函数说明：

split(img): 将图片划分成8x8的小块，对于408x408的lena图来说就是51x51=2601个小块.

C(n): 对应公式中的C函数，当n为0时，返回值为根号2的倒数，否则返回1.

dct(block): 对一个8x8的小块采用DCT变换.

quantize_y(img): 对Y亮度分量进行量化.

quantize_uv(img): 对UV色度分量进行量化.

Run_Length_Coding(z_list): 产生游长编码.

DPCM(block): 提取DC系数并产生它们的DPCM编码数组.

to_binary(num): 把一个数num转换成二进制字符串.

VIL(x): 获取变长整数编码(Variable-length integer encoding).

YUV_Block_Encode(DC, comp, flag): 对每一个图像块的亮度/色度进行编码，flag=1时编码亮度，flag!=1时编码色度.

### decode.py文件中的主要函数说明：

parse_component(s, height, width, head, tail, AC_pair, DC_pair): 对YUV各分量进行解析，得到需要的AC和DC的矩阵.

bit_to_coff(s, height, width): 输入字符串s，将其解析成YUV各分量的AC/DC系数.

iVIL(b): DC系数的VIL逆过程.

iDPCM(t): 对输入的数组t完成DPCM数组的DC系数的逆编码.

i_Run_Length_Coding(lst): 逆游长编码.

YUV_recover(img, flag): 对量化后的DCT系数恢复成未量化的的DCT系数，flag=1对亮度进行处理，flag!=1对色度进行处理.

C(n): 对应公式中的C函数，当n为0时，返回值为根号2的倒数，否则返回1.

iDCT(block): 对块进行逆DCT编码.
