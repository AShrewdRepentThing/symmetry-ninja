#!/bin/bash

image=dust_fill.png

size=$( identify -ping -format "%wx%h" "${image}" )
x_upb=${size%x*}
y_upb=${size#*x}

#x_inc=10
#y_inc=10
#x_tile=100
#y_tile=100

x_inc=100
y_inc=60
x_tile=100
y_tile=60

for ((x=0; x<x_upb; x+=x_inc))
do
    for ((y=0; y<y_upb; y+=y_inc))
    do
        convert "${image}" -crop "${x_tile}x${y_tile}+${x}+${y}" "$x-$y.png"
    done
done
