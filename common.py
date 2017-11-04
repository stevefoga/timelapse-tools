"""
common.py

Common tools used between Python modules.

Author:     Steve Foga
Created:    02 Nov 2017

Python version: 2.7.13
"""


class Common():
    @staticmethod
    def open_image(img_path):
        """
        Open image file.

        :param img_path: <str>

        :return: <PIL.Image>
        """
        import sys
        from PIL import Image

        try:
            iopen = Image.open(img_path)
            print("Opened image {0}".format(img_path))

        except IOError:
            sys.exit("{0} could not be opened.".format(img_path))

        else:
            return iopen

    @staticmethod
    def process_image(image, blocks=4):
        """
        Given a PIL Image object it returns its feature vector.

        :param image: <PIL.Image> image to process.
        :param blocks: <int> number of block to subdivide the RGB space (default=4).

        :return: <list> feature vector if successful. None if the image is not RGB.
        """
        import sys

        if not image.mode == 'RGB':
            sys.exit("Image mode {0} not supported.".format(image.mode))

        feature = [0] * blocks * blocks * blocks
        pixel_count = 0
        for pixel in image.getdata():
            ridx = int(pixel[0] / (256 / blocks))
            gidx = int(pixel[1] / (256 / blocks))
            bidx = int(pixel[2] / (256 / blocks))
            idx = ridx + gidx * blocks + bidx * blocks * blocks
            feature[idx] += 1
            pixel_count += 1

        return [x / float(pixel_count) for x in feature]