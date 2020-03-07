import cv2
import math
import numpy as np
from parameters import luma, chroma, Y_DC, UV_DC, Y_AC, UV_AC

Y_DC_pair = {value: key for key, value in Y_DC.items()}
UV_DC_pair = {value: key for key, value in UV_DC.items()}
Y_AC_pair = {value: key for key, value in Y_AC.items()}
UV_AC_pair = {value: key for key, value in UV_AC.items()}


def read_file(filename):
    """函数功能：按‘utf-8’编码格式读取文件‘filename’，将文件中的内容以字符串s返回"""
    file = open(filename, 'r', encoding='utf-8')
    s = file.read()
    return s


def parse_component(s, height, width, head, tail, AC_pair, DC_pair):
    """函数功能：对YUV各分量进行解析，得到需要的AC和DC的矩阵"""
    AC = []
    DC = []
    while len(AC) < height * width:
        while s[head:tail] not in DC_pair.keys():
            tail += 1
        size = DC_pair[s[head:tail]]
        head = tail
        tail += size
        ampl = 0 if size == 0 else iVIL(s[head:tail])
        DC.append(ampl)
        head = tail
        tail += 1
        ACblk = []
        length = 0
        while True:
            run_length = 0
            while True:
                while s[head:tail] not in AC_pair.keys():
                    tail += 1
                t = AC_pair[s[head:tail]]
                if t == (15, 0):
                    run_length += 15
                    head = tail
                    tail += 1
                else:
                    run_length += t[0]
                    size = t[1]
                    break
            head = tail
            tail += size
            ampl = 0 if size == 0 else iVIL(s[head:tail])
            ACblk.append([run_length, ampl])
            head = tail
            tail += 1
            length += run_length + 1
            if [run_length, ampl] == [0, 0] or length == 63:
                break
        AC.append(ACblk)
    return head, tail, AC, DC


def bit_to_coff(s, height, width):
    """函数功能：输入字符串s，将其解析成YUV各分量的AC/DC系数"""
    hei = height // 8
    wid = width // 8
    head = 0  # head和tail共同用于标记当前解析到哪里了
    tail = 1
    head, tail, ACY, DCY = parse_component(s, hei, wid, head, tail, Y_AC_pair, Y_DC_pair)
    head, tail, ACU, DCU = parse_component(s, hei, wid, head, tail, UV_AC_pair, UV_DC_pair)
    head, tail, ACV, DCV = parse_component(s, hei, wid, head, tail, UV_AC_pair, UV_DC_pair)
    return DCY, DCU, DCV, ACY, ACU, ACV


def iVIL(b):
    """函数功能：DC系数的VIL逆过程"""
    bi_str = ''
    if b[0] == '0':
        for c in b:
            bi_str += '0' if c == '1' else '1'
        return -int(bi_str, 2)  # 二进制转十进制并返回
    else:
        bi_str += b
        return int(bi_str, 2)


def iDPCM(t):
    """函数功能：对输入的数组t完成DPCM数组的DC系数的逆编码"""
    blk = []
    for i in range(len(t)):
        tmp = [[0 for i in range(8)] for i in range(8)]  # 暂时存储待添加的数组
        if i == 0:
            tmp[0][0] = t[0]
        else:
            tmp[0][0] = t[i] + blk[i - 1][0][0]
        blk.append(tmp)
    return blk


def i_Run_Length_Coding(lst):
    """函数功能：逆游长编码"""
    tmp = []
    for t in lst:
        zeros = t[0]
        number = t[1]
        if number == 0:
            for i in range(63 - len(tmp)):
                tmp.append(0)
            break
        for i in range(zeros):
            tmp.append(0)
        tmp.append(number)
    return tmp


def iZ(str, sheet):
    """函数功能：将之前按Z字读取形成的序列str恢复为表格sheet"""
    ary = i_Run_Length_Coding(str)
    cnt = 0
    m = n = 0  # 分别代表行和列
    while m < 8 and n < 8:
        if n < 7:
            n += 1
        else:
            m += 1
        while n >= 0 and m < 8:
            sheet[m][n] = ary[cnt]
            m += 1
            n -= 1
            cnt += 1
        m -= 1
        n += 1
        if m < 7:
            m += 1
        else:
            n += 1
        while n < 8 and m >= 0:
            sheet[m][n] = ary[cnt]
            m -= 1
            n += 1
            cnt += 1
        m += 1
        n -= 1
    return sheet


def YUV_recover(img, flag):
    """函数功能：对量化后的DCT系数恢复成未量化的的DCT系数，flag=1对亮度进行处理，flag!=1对色度进行处理"""
    tmp = [[0 for i in range(8)] for i in range(8)]
    if flag == 1:
        table = luma
    else:
        table = chroma
    for i in range(8):
        for j in range(8):
            tmp[i][j] = round(img[i][j] * table[i][j])
    return tmp


def C(n):
    """函数功能：对应公式中的C函数，当n为0时，返回值为根号2的倒数，否则返回1"""
    return pow(2, 1 / 2) / 2 if n == 0 else 1


def iDCT(block):
    """函数功能：对块进行逆DCT编码"""
    tmp = [[0 for i in range(8)] for i in range(8)]
    for x in range(8):
        for y in range(8):
            point = 0
            for u in range(8):
                for v in range(8):
                    point += math.cos((2 * x + 1) * u * math.pi / 16) * math.cos((2 * y + 1) * v * math.pi / 16) * \
                             block[u][v] * C(u) * C(v) / 4
            tmp[x][y] = round(point)
    return tmp


def merge(blocks):
    """函数功能：将各blocks(2601x8x8)重组为Y/U/V分量(408x408)"""
    T = blocks[0]
    for i in range(1, 51):
        T = np.hstack((T, blocks[i]))
    for i in range(51, 2601, 51):
        s = blocks[i]
        for j in range(1, 51):
            s = np.hstack((s, blocks[i + j]))
        T = np.vstack((T, s))
    return T


def component_decode(DC, AC, flag):
    """函数功能：对YUV分量进行解码，返回各自的分量块"""
    comp_blocks = iDPCM(DC)
    for i in range(len(comp_blocks)):
        comp_blocks[i] = iZ(AC[i], comp_blocks[i])
        comp_blocks[i] = YUV_recover(comp_blocks[i], flag)
        comp_blocks[i] = iDCT(comp_blocks[i])
    comp_blocks = np.array(comp_blocks)
    COMP = merge(comp_blocks)
    return COMP


def decoder(filename, img_name):
    """函数功能：调用前面定义的函数对图像img完成数据的解码和图像的显示"""
    DCY, DCU, DCV, ACY, ACU, ACV = bit_to_coff(read_file(filename), 408, 408)
    Y = component_decode(DCY, ACY, 1)
    U = component_decode(DCU, ACU, 0)
    V = component_decode(DCV, ACV, 0)
    im = cv2.merge([Y, U, V])  # 合并YUV颜色通道
    imge = im.astype(np.uint8)  # 恢复图像深度
    image = cv2.cvtColor(imge, cv2.COLOR_YUV2BGR)  # YUV颜色模式到RGB模式的转化
    cv2.imwrite(img_name, image)


decoder('encode.txt', 'lean_re.jpg')
