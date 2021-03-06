from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import pytesseract
# import PIL.ImageOps

# 默认的分辨率 1920*1080，东方财富软件使用默认的设置，皮肤颜色设置为典雅白，K 线图默认为 15 分钟
# 数据格式说明：<> 表示替换为实际内容，[] 表示多选一，_ 表示一个空格
# 数字有模糊边的，目前测试下来，使用 filter.ENHANCE + point-160 处理效果最好
weak_data_position = {
    # 稳赢线数据位置，由于最前面有股票名称，长短不一，导致稳赢线数据位置不确定，只能连名称一起全部截图，然后再 OCR
    # 股票名称最长为 8 个字，最短为 2 个字
    # WYX_ALL 数据格式：<股票名称>_（x分钟线,前复权）_稳赢线_短线:_[368.735/3.610]_[↑/↓/-]_中线:_[366.952/3.609]_[↑/↓/-]
    "WYX_ALL" : (21, 80, 515, 98),

    # KD 数据在 K: 之前（包括）都是固定长度的，所以从 K: 之后的位置开始
    # KD_ALL 数据格式：[78.530/0.0152]_[↑/↓/]_D:_[66.451/0.964]_[↑/↓/]
    "KD_ALL" : (109, 523, 257, 541),

    # VOLUME 数据在 VOLUME: 之前（包括）都是固定长度的，所以从 VOLUME: 之后的位置开始
    # VOLUME_ALL 数据格式：[0.000/2279360.000]_[↑/↓/-]_MAVOL1:_[0.000/1197201.600]_[↑/↓/-]_MAVOL2:_[0.000/888559.100]_[↑/↓/-]
    "VOLUME_ALL" : (153, 623, 560, 641),

    # MACD 数据在 DIF: 之前（包括）都是固定长度的，所以从 DIF: 之后的位置开始,
    # DIF 数据可以单独获取，DIF 为正时，结束在 197-203 之间，为负时，结束在 201-207 之间，取交集的中点 202。 -- 最后验证不行，因为 DIF 值会有 -184.777 到 210.100 这么大
    # "MACD_DIF" : (151, 719, )
    # MACD_ALL 数据格式：[-0.000/0.000/-184.777]_[↑/↓/]_DEA:_[-0.000/0.000/-184.777]_[↑/↓/]_MACD:_[-0.000/0.000/-7.750]_[↑/↓/]
    "MACD_ALL" : (151, 719, 445, 737),

    # 股票代码，8 个字股票名以下的，1568 就够了，但是 8 个字股票名字的，股票代码字号会缩小，1571 刚好可以把第一个字截进去，需要单独处理
    "STOCK_CODE" : (1514, 54, 1571, 80)
}

# 数字比较清晰、没有模糊像素的，直接用 point-190 就非常清晰了
strong_data_position = {
    # 软件时间
    "EASTMONEY_TIME" : (1842, 1019, 1915, 1038),

    # 最新价格
    "CURRENT" : (1538, 120, 1615, 141),

    # 平均价格
    "AVERAGE" : (1642, 120, 1710, 141),

    # 最高价格
    "HIGH" : (1538, 138, 1615, 158),

    # 最低价格
    "LOW" : (1642, 138, 1710, 158),

    # 今日开盘价
    "OPEN" : (1538, 155, 1615, 175),

    # 昨天收盘价
    "PRE_CLOSE" : (1642, 155, 1710, 175),

    # 涨跌，数值前面有 ▲/▼ 需要处理
    "CHANGE" : (1538, 172, 1615, 192),

    # 涨跌幅度，数值前面有 -/+、后面有 % 需要处理
    "PCT_CHANGE" : (1642, 172, 1710, 192),

    # 成交金额，数值后面有 万/亿 需要处理
    "AMOUNT" : (1538, 189, 1615, 209),

    # 成交量，数值后面有 万/亿 需要处理
    "VOLUME" : (1642, 189, 1710, 209),
    
    # 外盘，数值后面有 万/亿 需要处理
    "OUT" : (1538, 206, 1615, 226),

    # 内盘，数值后面有 万/亿 需要处理
    "IN" : (1642, 206, 1710, 226),

    # 换手率，数值后面有 % 需要处理
    "PCT_TURN" : (1538, 223, 1615, 243),

    # 量比
    "PCT_VOLUME" : (1642, 223, 1710, 243),

    # 笔数
    "TRADE_NUM" : (1538, 240, 1615, 261),

    # 委比，数值前面有 +/- 需要处理
    "ORDER_RATIO" : (1642, 240, 1710, 261),

    # 每手股，数值后面有个 股 字需要处理
    "PER_LOT" : (1552, 359, 1615, 379),

    # 主力流入，数值后面有 万元/亿元 需要处理
    "MAIN_IN" : (1582, 411, 1710, 435),

    # 主力流出，数值后面有 万元/亿元 需要处理
    "MAIN_OUT" : (1582, 440, 1710, 464),

    # 主力净流向，数值前面有 +/-，后面有 万元/亿元 需要处理
    "MAIN_PURE_IN" : (1582, 472, 1710, 496),

    # 超大单流入
    "SUPER_IN" : (1540, 531, 1631, 555),

    # 超大单流出
    "SUPER_OUT" : (1631, 531, 1710, 555),

    # 大单流入
    "LARGE_IN" : (1540, 560, 1631, 584),

    # 大单流出
    "LARGE_OUT" : (1631, 560, 1710, 584),

    # 中单流入
    "MEDIUM_IN" : (1540, 589, 1631, 613),

    # 中单流出
    "MEDIUM_OUT" : (1631, 589, 1710, 613),

    # 小单流入
    "SMALL_IN" : (1540, 618, 1631, 642),

    # 小单流出
    "SMALL_OUT" : (1642, 618, 1710, 642),

    # 卖一价格
    "SELL01_PRICE" : (1743, 282, 1814, 299),

    # 卖一数量，数值后面有 K/M 需要处理
    "SELL01_AMOUNT" : (1821, 282, 1874, 299),

    # 卖二价格
    "SELL02_PRICE" : (1743, 264, 1814, 282),

    # 卖二数量
    "SELL02_AMOUNT" : (1821, 264, 1874, 282),

    # 卖三价格
    "SELL03_PRICE" : (1743, 246, 1814, 264),

    # 卖三数量
    "SELL03_AMOUNT" : (1821, 246, 1874, 264),

    # 卖四价格
    "SELL04_PRICE" : (1743, 228, 1814, 246),

    # 卖四数量
    "SELL04_AMOUNT" : (1821, 228, 1874, 246),

    # 卖五价格
    "SELL05_PRICE" : (1743, 210, 1814, 228),

    # 卖五数量
    "SELL05_AMOUNT" : (1821, 210, 1874, 228),

    # 卖六价格
    "SELL06_PRICE" : (1743, 192, 1814, 210),

    # 卖六数量
    "SELL06_AMOUNT" : (1821, 192, 1874, 210),

    # 卖七价格
    "SELL07_PRICE" : (1743, 174, 1814, 192),

    # 卖七数量
    "SELL07_AMOUNT" : (1821, 174, 1874, 192),

    # 卖八价格
    "SELL08_PRICE" : (1743, 156, 1814, 174),

    # 卖八数量
    "SELL08_AMOUNT" : (1821, 156, 1874, 174),

    # 卖九价格
    "SELL09_PRICE" : (1743, 138, 1814, 156),

    # 卖九数量
    "SELL09_AMOUNT" : (1821, 138, 1874, 156),

    # 卖十价格
    "SELL10_PRICE" : (1743, 120, 1814, 138),

    # 卖十数量
    "SELL10_AMOUNT" : (1821, 120, 1874, 138),

    # 买一价格
    "BUY01_PRICE" : (1743, 300, 1814, 318),

    # 买一数量
    "BUY01_AMOUNT" : (1821, 300, 1874, 318),

    # 买二价格
    "BUY02_PRICE" : (1743, 318, 1814, 336),

    # 买二数量
    "BUY02_AMOUNT" : (1821, 318, 1874, 336),

    # 买三价格
    "BUY03_PRICE" : (1743, 336, 1814, 354),

    # 买三数量
    "BUY03_AMOUNT" : (1821, 336, 1874, 354),

    # 买四价格
    "BUY04_PRICE" : (1743, 354, 1814, 372),

    # 买四数量
    "BUY04_AMOUNT" : (1821, 354, 1874, 372),

    # 买五价格
    "BUY05_PRICE" : (1743, 372, 1814, 390),

    # 买五数量
    "BUY05_AMOUNT" : (1821, 372, 1874, 390),

    # 买六价格
    "BUY06_PRICE" : (1743, 390, 1814, 408),

    # 买六数量
    "BUY06_AMOUNT" : (1821, 390, 1874, 408),

    # 买七价格
    "BUY07_PRICE" : (1743, 408, 1814, 426),

    # 买七数量
    "BUY07_AMOUNT" : (1821, 408, 1874, 426),

    # 买八价格
    "BUY08_PRICE" : (1743, 426, 1814, 444),

    # 买八数量
    "BUY08_AMOUNT" : (1821, 426, 1874, 444),

    # 买九价格
    "BUY09_PRICE" : (1743, 444, 1814, 462),

    # 买九数量
    "BUY09_AMOUNT" : (1821, 444, 1874, 462),

    # 买十价格
    "BUY10_PRICE" : (1743, 462, 1814, 480),

    # 买十数量
    "BUY10_AMOUNT" : (1821, 462, 1874, 480)
}

some_data_position = {
    # 软件时间
    "EASTMONEY_TIME" : (1842, 1019, 1915, 1038),

    # 最新价格
    #"CURRENT" : (1538, 120, 1615, 141),

    # 平均价格
    #"AVERAGE" : (1642, 120, 1710, 141),

    # 最高价格
    #"HIGH" : (1538, 138, 1615, 158),

    # 最低价格
    #"LOW" : (1642, 138, 1710, 158),

    # 今日开盘价
    #"OPEN" : (1538, 155, 1615, 175),

    # 昨天收盘价
    #"PRE_CLOSE" : (1642, 155, 1710, 175),

    # 涨跌，数值前面有 ▲/▼ 需要处理
    "CHANGE" : (1538, 172, 1615, 192),

    # 涨跌幅度，数值前面有 -/+、后面有 % 需要处理
    "PCT_CHANGE" : (1642, 172, 1710, 192),

    # 成交金额，数值后面有 万/亿 需要处理
    "AMOUNT" : (1538, 189, 1615, 209),

    # 成交量，数值后面有 万/亿 需要处理
    "VOLUME" : (1642, 189, 1710, 209),
    
    # 外盘，数值后面有 万/亿 需要处理
    "OUT" : (1538, 206, 1615, 226),

    # 内盘，数值后面有 万/亿 需要处理
    "IN" : (1642, 206, 1710, 226),

    # 换手率，数值后面有 % 需要处理
    "PCT_TURN" : (1538, 223, 1615, 243),

    # 量比
    "PCT_VOLUME" : (1642, 223, 1710, 243),

    # 笔数
    #"TRADE_NUM" : (1538, 240, 1615, 261),

    # 委比，数值前面有 +/- 需要处理
    #"ORDER_RATIO" : (1642, 240, 1710, 261),

    # 每手股，数值后面有个 股 字需要处理
    "PER_LOT" : (1552, 359, 1615, 379),
}

for i in range(1, 21):
    img1 = Image.open('/home/liugdft/stock/stock-ocr/pics/' + str(i) + '.ppm')
    #img1 = Image.open('/home/liugdft/stock/stock-ocr/pics/pics-live/1.ppm')
    #img1.show()
    #img1.size
    #img1.format
    #img1.mode

    # 灰度处理
    img2 = img1.convert('L')
    #img2.show()

    #chi_data_position = {"STOCK_NAME":(1571,54,1707,84), "AMOUNT":(1695,189,1713,207), "ALL_MONNEY":(1598,189,1615,207)}

    #data_position = {"MACD_ALL" : (151, 719, 445, 737),}
    #data_position = {
    #"BUY08_AMOUNT" : (1821, 426, 1874, 444),
    #}

    pics = {}
    #二值化，采用阈值分割法，threshold为分割点
    threshold = 190
    table = []
    for j in range(256):
        if j < threshold:
            table.append(0)
        else:
            table.append(1)
    
    for key in strong_data_position:
        #pics[key] = Image.new('L', (300, 50), 255)
        #pics[key].paste(img2.crop(data_position[key]), (10, 10))
        #pics[key].point(table, '1').save("/home/liugdft/Pictures/" + key + ".tiff", "TIFF")
        #pics[key].save("/home/liugdft/Pictures/" + key + ".tiff", "TIFF")
        img3 = img2.crop(strong_data_position[key])
        img3 = img3.point(table, '1')
        #img3 = img3.point(lambda x: 0 if x < 160 else 255)
        #img3 = img3.point(table, '1')
        #img4 = img2.crop(weak_data_position[key])
        #img4 = img4.filter(ImageFilter.EDGE_ENHANCE_MORE).point(table, '1')
        size = img3.size
        img3.resize((size[0]*5, size[1]*5)).save("/home/liugdft/stock/stock-ocr/pics/trainning-pics/" + str(i) + "-" + key + ".tif", "TIFF")
        #img4.resize((size[0]*5, size[1]*5)).show()



    #img2.crop(data_position[key]).show()
    #print(pytesseract.image_to_string(pics[key], lang='eng'))

# 反色处理，用来处理黑底的图片
#img3 = ImageOps.invert(img2)
#img3.show()

# 扩大图片，放到一块100x100的白底上
#base_img = Image.new('L', (100, 100), 255)
#base_img.paste(img3, (10, 10))

#img_enhance1 = base_img.filter(ImageFilter.DETAIL) 
#img_enhance1.show()

#img_enhance3 = ImageEnhance.Sharpness(img1).enhance(100)
#img_enhance3.show()


#二值化，采用阈值分割法，threshold为分割点
#threshold = 190
#table = []
#for j in range(256):
#    if j < threshold:
#        table.append(0)
#    else:
#        table.append(1)
#
#img3 = img2.point(table, '1')


# 对 MACD 这种不清晰的截图最好的处理是 filter.ENHANCE + point-190
# 对于其他数字比较清晰的，这么用也可以

#print(pytesseract.image_to_string(img1, lang='eng'))