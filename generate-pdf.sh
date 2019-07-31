#!/bin/bash

pushd people/
mkdir -p pdf
for f in people_badge_* ; do
	convert $f -resize 1080x360 -density 120x120 -units pixelspercentimeter  pdf/$f.pdf 
done
pdfunite pdf/people_badge_* all.pdf
rm -rf pdf
rm *.png
popd
