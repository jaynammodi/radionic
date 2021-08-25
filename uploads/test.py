from PIL import Image, ImageFont, ImageDraw
import os

old_im = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.jpg"))
old_size = old_im.size
aspect_ratio = old_size[1]/old_size[0]
old_im = old_im.resize((1080, int(1080*aspect_ratio)), Image.NEAREST)
old_size = old_im.size

new_size = (1080, 1920)
new_im = Image.new("RGB", new_size)   ## luckily, this is already black!
new_im.paste(old_im, ((new_size[0]-old_size[0])//2, (new_size[1]-old_size[1])//2))

msgs = ["My Name Here", "My Wish Here", "RR - RR Code Here", " - Radionic Tone Healing"]

textfont = ImageFont.truetype('Calibri.ttf', 50)
W = 1080
H = 1920
draw = ImageDraw.Draw(new_im)

msg = ""
for x in msgs:
    msg += x + "\n\n"

draw.text((W/2, H), msg, align="center", font=textfont, anchor="md")
new_im.save('someimage.jpg')