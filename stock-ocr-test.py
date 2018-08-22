from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import pytesseract
# import PIL.ImageOps

img1 = Image.open('/home/liugdft/Pictures/1.ppm')
#img1.show()
#img1.size
#img1.format
#img1.mode

# 灰度处理
img2 = img1.convert('L')
#img2.show()

#img_enhance = img2.filter(ImageFilter.EDGE_ENHANCE_MORE) 
img_enhance = img2.filter(ImageFilter.EDGE_ENHANCE) 
img_enhance.show()



chi_data_position = {"STOCK_NAME":(1571,54,1707,84), "AMOUNT":(1695,189,1713,207), "ALL_MONNEY":(1598,189,1615,207)}
data_position = {"DIF":(151,529,191,545), "DEA":(233,529,270,545), "MACD":(319,529,366,545), "STOCK_ID":(1518,56,1568,83),
                 "STOCK_PRICE":(1545,121,1616,140), "RISE_RATIO":(1647,173,1713,190), "SELL01_PRICE":(1749,281,1832,298), "SELL01_AMOUNT":(1832,281,1900,298),
                 "RISE_PIONTS":(1545,173,1616,191), "WEIBI":(1647,241,1714,260) }

data_position = {"MACD":(151,529,390,545), "STOCK_ID":(1518,56,1568,83),
                 "STOCK_PRICE":(1545,121,1616,140), "RISE_RATIO":(1647,173,1713,190), "SELL01_PRICE":(1749,281,1832,298), "SELL01_AMOUNT":(1832,281,1900,298),
                 "RISE_PIONTS":(1545,173,1616,191), "WEIBI":(1647,241,1714,260) }

chi_pics = {}
for key in chi_data_position:
    chi_pics[key] = Image.new('L', (200, 50), 255)
    chi_pics[key].paste(img2.crop(chi_data_position[key]), (10, 10))
    chi_pics[key].point(table, '1').save("/home/liugdft/Pictures/" + key + ".tiff", "TIFF")
    #chi_pics[key].show()
    #chi_pics[key].save("/home/liugdft/Pictures/" + key + ".tiff", "TIFF")
    #print(pytesseract.image_to_string(chi_pics[key], lang='chi_sim'))

pics = {}
for key in data_position:
    pics[key] = Image.new('L', (300, 50), 255)
    pics[key].paste(img2.crop(data_position[key]), (10, 10))
    pics[key].point(table, '1').save("/home/liugdft/Pictures/" + key + ".tiff", "TIFF")
    #pics[key].save("/home/liugdft/Pictures/" + key + ".tiff", "TIFF")
    #pics[key].show()
    #print(pytesseract.image_to_string(pics[key], lang='eng'))

# 反色处理，用来处理黑底的图片
#img3 = ImageOps.invert(img2)
#img3.show()

# 扩大图片，放到一块100x100的白底上
base_img = Image.new('L', (100, 100), 255)
base_img.paste(img3, (10, 10))

#img_enhance1 = base_img.filter(ImageFilter.DETAIL) 
#img_enhance1.show()

#img_enhance3 = ImageEnhance.Sharpness(img1).enhance(100)
#img_enhance3.show()


#二值化，采用阈值分割法，threshold为分割点
threshold = 190
table = []
for j in range(256):
    if j < threshold:
        table.append(0)
    else:
        table.append(1)

img3 = img2.point(table, '1')


# 对 MACD 这种不清晰的截图最好的处理是 filter.ENHANCE + point-160
# 对于其他数字比较清晰的，直接用 point-190 就非常清晰了

print(pytesseract.image_to_string(img1, lang='eng'))