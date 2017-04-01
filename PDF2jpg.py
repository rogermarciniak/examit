from wand.color import Color
from wand.image import Image


"""
This tool converts the .pdf to .jpg for use with OpenCV.
"""


def convert(test):
    # opens the pdf file stream with the correct resolution
    # so that the elements are qood quality
    with Image(file=test, format='pdf', resolution=300) as img:
        img.compression_quality = 100
        # sets background colour
        img.background_color = Color("white")
        # because the pdf contains transparency that becomes black
        # we need to remove it, the space will assume background colour
        img.alpha_channel = 'remove'
        # saved as a .jpg so OpenCV can use it
        img.format = 'jpeg'
        fn = 'test.jpg'
        img.save(filename=fn)
        # jpeg_bin = img.make_blob('jpeg')
        return fn
