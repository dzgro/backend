from PIL import Image, ImageOps
names = [str(i) for i in range(221, 231)]
# for name in names:
#     image = Image.open(f"D://Downloads//rakhi masks//{name}.png")
#     coloredimage = Image.new('RGBA', [image.width, image.height], (170, 230, 241, 255))
#     coloredimage.paste(image, (0, 0), image)
#     isportrait = True if image.width < image.height else False
#     print (f'Design Name: {name}, Size: {image.width}x{image.height}')
#     baseImgSize = image.height if isportrait else image.width
#     baseImg = Image.new('RGBA', [baseImgSize, baseImgSize], (255, 255, 255, 0))
#     corrds = (int((baseImgSize-image.width)/2),0) if isportrait else (0, int((baseImgSize-image.height)/2))
#     baseImg.paste(coloredimage, corrds, coloredimage)
#     baseImg.format='PNG'
#     baseImg.save(f"D://Downloads//rakhi masks//masks//{name}_Mask.png")
# print('')
for name in names:
    image = Image.open(f"D://Downloads//rakhi masks//{name}.png")
    isportrait = True if image.width < image.height else False
    print (f'Design Name: {name}, Size: {image.width}x{image.height}')
    baseImgSize = image.height if isportrait else image.width
    baseImg = Image.new('RGBA', [baseImgSize, baseImgSize], (255, 255, 255, 0))
    corrds = (int((baseImgSize-image.width)/2),0) if isportrait else (0, int((baseImgSize-image.height)/2))
    baseImg.paste(image, corrds)
    baseImg.format='PNG'
    baseImg.save(f"D://Downloads//rakhi masks//original//{name}_Mask.png")
print('')

