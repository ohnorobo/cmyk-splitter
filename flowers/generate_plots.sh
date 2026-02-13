magick convert urn.jpeg urn.png

magick urn.png -colorspace CMYK -separate urn_%d.png

magick convert -monochrome urn_0.png urn_C.png
magick convert -monochrome urn_1.png urn_M.png
magick convert -monochrome urn_3.png urn_K.png
magick convert urn_2.png -threshold 65% -type bilevel urn_Y.png

python3 StringyPlotter/StringyPlotter.py urn_C.png urn_C_big.svg 50 25
python3 StringyPlotter/StringyPlotter.py urn_M.png urn_M_big.svg 50 25
python3 StringyPlotter/StringyPlotter.py urn_Y.png urn_Y_big.svg 50 25
python3 StringyPlotter/StringyPlotter.py urn_K.png urn_K_big.svg 25 25

rsvg-convert urn_C_big.svg --width=17cm --keep-aspect-ratio -f svg -o urn_C.svg
rsvg-convert urn_M_big.svg --width=17cm --keep-aspect-ratio -f svg -o urn_M.svg
rsvg-convert urn_Y_big.svg --width=17cm --keep-aspect-ratio -f svg -o urn_Y.svg
rsvg-convert urn_K_big.svg --width=17cm --keep-aspect-ratio -f svg -o urn_K.svg

rm urn.png \
   urn_0.png \
   urn_C.png \
   urn_1.png \
   urn_M.png \
   urn_2.png \
   urn_Y.png \
   urn_3.png \
   urn_K.png \
   urn_C_big.svg \
   urn_M_big.svg \
   urn_Y_big.svg \
   urn_K_big.svg