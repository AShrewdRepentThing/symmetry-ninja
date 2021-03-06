#!/usr/bin/env python

import re, os, numpy, PIL
from PIL import Image

multiplier = 5
stemex = re.compile(r'([^\d]*)([\d]*)\.png')

# Access all PNG files in directory
allfiles = os.listdir(os.getcwd())
image_list = [filename for filename in allfiles if  filename[-4:] in ['.png','.PNG']]

# Assuming all images are the same size, get dimensions of first image
w, h = Image.open(image_list[0]).size
N = len(image_list)

def get_name(image, i):
    base, num = stemex.findall(image)[0]
    suffix = (int(num) - 1) * multiplier + i
    fname = '%s_%i.png' % (base, suffix)
    return fname

def get_ith_interpolate(i, num, image_1, image_2):
    array = numpy.zeros((h, w, 4), numpy.float)
    ia_1 = numpy.array(Image.open(image_1), dtype=numpy.float)
    ia_2 = numpy.array(Image.open(image_2), dtype=numpy.float)
    comb_array = ((num - i) * ia_1 + i * ia_2) / num
    comb_array = numpy.array(numpy.round(comb_array), dtype=numpy.uint8)
    out = Image.fromarray(comb_array, mode='RGBA')
    fname = get_name(image_1, i)
    out.save(fname)

for image_1, image_2 in zip(image_list, image_list[1:] + image_list[:1]):
    for i in range(multiplier):
        get_ith_interpolate(i, multiplier, image_1, image_2)
