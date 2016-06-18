#!/bin/bash

./divide_vert -i spritesheet.png line-%02d.png
montage line-*.png -rotate 90 -geometry '1x1<' -tile 1x -background none joined.png
./divide_vert -i joined.png sprite-%03d.png
mogrify -rotate 270 sprite-*.png
