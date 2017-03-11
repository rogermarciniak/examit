from wand.image import Image
from wand.color import Color

"""
This tool converts the .pdf to .jpg for use with OpenCV.
"""
# TODO: MAKE THIS A CALLABLE METHOD

# opens the pdf with the correct resolution
# so that the elements are qood quality
with Image(filename='test.pdf', resolution=300) as img:
	img.compression_quality = 100
	# sets background colour
	img.background_color = Color("white")
	# because the pdf contains transparency that becomes black
	# we need to remove it, the space will assume background colour
	img.alpha_channel = 'remove'
	# saved as a .jpg so OpenCV can use it
	img.save(filename='test.jpg')
