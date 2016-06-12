#!/bin/bash

for n in *.png
do
   #echo "mv $n $(echo $n | sed -e 's/.png/.x/')"
   #echo "mv $n $(echo $n | sed -e 's/dusti(*)_*.png/$1_$2.x/')"
   echo "mv $n $(echo $n | sed -e 's/dusti(*)_*.png/*.x/')"
done

