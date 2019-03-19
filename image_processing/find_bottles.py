import matplotlib.pyplot as plt
import numpy as np
from skimage.feature import match_template
from PIL import Image


# load image
input_im = '/home/pi/BeerBot/image_processing/ims/1552989614.png'
with Image.open(input_im, 'r') as src:
    image = np.asarray(src)

# define matching "templates"
templates = {"beer": {"x": (170, 220),
                      "y": (75, 130)},
             "spezi": {"x": (170, 220),
                       "y": (75, 130)},
             "non-alcoholic": {"x": (170, 220),
                               "y": (75, 130)}}
for namer, xy in templates.items():
    part = image[xy['x'][0]:xy['x'][1], xy['y'][0]:xy['y'][1]]
    result = match_template(image, part)
    plt.imshow(result)
    plt.set_title(namer)
    plt.savefig('{}.png'.format(namer))
#
# ij = np.unravel_index(np.argmax(result), result.shape)
# x, y = ij[::-1]
#
# fig = plt.figure(figsize=(8, 3))
# ax1 = plt.subplot(1, 3, 1)
# ax2 = plt.subplot(1, 3, 2)
# ax3 = plt.subplot(1, 3, 3, sharex=ax2, sharey=ax2)
#
# ax1.imshow(coin, cmap=plt.cm.gray)
# ax1.set_axis_off()
# ax1.set_title('template')
#
# ax2.imshow(image, cmap=plt.cm.gray)
# ax2.set_axis_off()
# ax2.set_title('image')
# # highlight matched region
# hcoin, wcoin = coin.shape
# rect = plt.Rectangle((x, y), wcoin, hcoin, edgecolor='r', facecolor='none')
# ax2.add_patch(rect)
#
# ax3.imshow(result)
# ax3.set_axis_off()
# ax3.set_title('`match_template`\nresult')
# # highlight matched region
# ax3.autoscale(False)
# ax3.plot(x, y, 'o', markeredgecolor='r', markerfacecolor='none', markersize=10)
#
# plt.savefig('test.png')
