import cv2
import math
from parameters import luma, chroma, Y_DC, UV_DC, Y_AC, UV_AC


def split(img):
    """函数功能：将图片划分成8x8的小块，对于408x408的lena图来说就是51x51=2601个小块"""
    hei = len(img)
    wid = len(img[0])
    block = []  # 用于各分量的存储分块
    for i in range(hei // 8):
        for j in range(wid // 8):
            tmp = [[0 for i in range(8)] for i in range(8)]  # 用于暂时存储每个8x8的分块
            for m in range(8):
                for n in range(8):
                    tmp[m][n] = img[i * 8 + m][j * 8 + n]
            block.append(tmp)  # 将分割的块添加到存储块的列表
    return block


def C(n):
    """函数功能：对应公式中的C函数，当n为0时，返回值为根号2的倒数，否则返回1"""
    return pow(2, 1 / 2) / 2 if n == 0 else 1


def dct(block):
    """函数功能：对一个8x8的小块采用DCT变换"""
    tmp = [[0 for i in range(8)] for i in range(8)]  # 用于暂时存储变换后的结果
    for u in range(8):
        for v in range(8):
            point = 0  # 对每一个像素点进行处理
            for x in range(8):
                for y in range(8):
                    point += math.cos((2 * x + 1) * u * math.pi / 16) * math.cos((2 * y + 1) * v * math.pi / 16) * \
                             block[x][y]
            tmp[u][v] = round(C(u) * C(v) / 4 * point)
    return tmp


def quantize_y(img):
    """函数功能：对Y亮度分量进行量化"""
    tmp = [[0 for i in range(8)] for i in range(8)]
    for i in range(8):
        for j in range(8):
            tmp[i][j] = round(img[i][j] / luma[i][j])
    return tmp


def quantize_uv(img):
    """函数功能：对UV色度分量进行量化"""
    tmp = [[0 for i in range(8)] for i in range(8)]
    for i in range(8):
        for j in range(8):
            tmp[i][j] = round(img[i][j] / chroma[i][j])
    return tmp


def Z(img):
    """函数功能：对量化后的块进行Z字扫描，将扫描的结果存储在Z列表中"""
    Z_list = []
    m = n = 0  # 分别代表行和列
    while m < 8 and n < 8:  # 当尚未遍历到最后一个点循环
        if n < 7:
            n = n + 1
        else:
            m = m + 1
        while n >= 0 and m < 8:
            Z_list.append(img[m][n])
            m = m + 1
            n = n - 1
        m = m - 1
        n = n + 1
        if m < 7:
            m = m + 1
        else:
            n = n + 1
        while n < 8 and m >= 0:
            Z_list.append(img[m][n])
            m = m - 1
            n = n + 1
        m = m + 1
        n = n - 1
    return Z_list


def Run_Length_Coding(z_list):
    """函数功能：产生游长编码"""
    tmp = []  # 用于存储游长编码
    zeros = 0  # 对连续的0进行计数
    for t in z_list:
        if t == 0:
            zeros += 1
        else:
            tmp.append([zeros, t])
            zeros = 0
    if zeros != 0:
        tmp.append([0, 0])
    return tmp


def DPCM(block):
    """函数功能：提取DC系数并产生它们的DPCM编码数组"""
    tmp = [block[0][0][0]]  # 初始化DPCM的存储表
    leng = len(block)
    for i in range(1, leng):
        tmp.append(block[i][0][0] - block[i - 1][0][0])
    return tmp


def to_binary(num):
    """函数功能：把一个数num转换成二进制字符串"""
    s = bin(abs(int(num)))[2:]  # 返回整数num的二进制表示
    if num < 0:  # 按照算法描述，用一个编码的取反来表示负数
        tmp = ''  # 存储按照算法规定的负数二进制编码
        for char in s:
            tmp += '0' if char == '1' else '1'
        return tmp
    else:
        return s


def VIL(x):
    """函数功能：获取变长整数编码(Variable-length integer encoding)"""
    return [0, ''] if x == 0 else [len(to_binary(x)), to_binary(x)]


def YUV_Block_Encode(DC, comp, flag):
    """函数功能：对每一个图像块的亮度/色度进行编码，flag=1时编码亮度，flag!=1时编码色度"""
    tmp = ''  # 暂时存储编码后的分量
    if flag == 1:
        tmp += Y_DC[VIL(DC)[0]] + VIL(DC)[1]  # 存储DC系数到字符串s中
    else:
        tmp += UV_DC[VIL(DC)[0]] + VIL(DC)[1]
    for t in comp:
        run_length = t[0]
        m = VIL(t[1])
        while run_length > 15:
            run_length -= 15
            tmp += Y_AC[(15, 0)] if flag == 1 else UV_AC[(15, 0)]
        tmp += Y_AC[(run_length, m[0])] if flag == 1 else UV_AC[(run_length, m[0])]
        tmp += m[1]
    return tmp


def save_to_file(filename, s):
    """函数功能：将字符串s以‘utf-8’的编码格式写入文件filename中去"""
    file = open(filename, 'w', encoding='utf-8')
    file.write(s)
    file.close()


def component_en(comp, flag):
    """函数功能：对YUV分量进行编码，返回各自的编码二进制串"""
    DCT = []
    Quantize = []
    Zlist = []
    AC_coff = []
    block = split(comp)
    for blk in block:
        DCT.append(dct(blk))
        Quantize.append(quantize_y(DCT[-1]) if flag == 1 else quantize_uv(DCT[-1]))
        Zlist.append(Z(Quantize[-1]))
        AC_coff.append(Run_Length_Coding(Zlist[-1]))
    DC_coff = DPCM(Quantize)
    str_after_encode = ''
    for i in range(len(AC_coff)):
        str_after_encode += YUV_Block_Encode(DC_coff[i], AC_coff[i], flag)
    return str_after_encode


def encoder(img, filename):
    """函数功能：调用前面定义的函数对图像ima完成数据的编码"""
    lena_bgr = cv2.imread(img)  # img是一个408*408*3的三维数组，用于表示[height, width, channel]，其中channel表示图片的颜色通道
    lena_yuv = cv2.cvtColor(lena_bgr, cv2.COLOR_BGR2YUV)  # 将RGB颜色模式转化成YUV颜色模式
    Y, U, V = cv2.split(lena_yuv)  # 划分YUV三个颜色通道
    s = component_en(Y, 1)
    s += component_en(U, 0)
    s += component_en(V, 0)
    print("the length of bit stream s : ", end="")  # 打印压缩后的位流长度
    print(len(s))
    save_to_file(filename, s)  # 将结果存储到文件中


encoder('lena.jpg', 'encode.txt')
