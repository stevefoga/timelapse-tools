"""
classify_image.py

Purpose:    Use classifier made by generate_classifier.py to classify an image.

Author:     Steve Foga
Created:    02 Nov 2017

Python version: 2.7.12
"""
import os
import sys
import glob
import numpy as np
from lib.common import Common


def classify(img_in, img_ext, model):
    """
    Classify images, return text file of file paths of grouped images.

    :param img_in: <str> Path to images to be classified
    :param img_ext: <str> Image extension, e.g., '.jpg'
    :param model: <sklearn.grid_search.GridSearchCV> model file (hint: read with pickle.load())

    :return: <list> zipped with (/path/to/image.ext, 0_or_1)
    """
    # find images
    img_path = os.path.join(img_in, '*' + img_ext)
    img = glob.glob(img_path)
    if not img:
        print("Could not find images for string {0}".format(img_path))
        sys.exit(-1)

    # get the best estimate from the classifier
    classifier = model.best_estimator_

    output = []
    for i in img:
        # read target image(s)
        img_open = Common.open_image(i)

        # open image as vector
        img_vec = Common.process_image(img_open)

        # reshape vector (sklearn >= 0.19 requires this)
        np_vec = np.array(img_vec).reshape((len(img_vec), 1)).reshape(1, -1)

        # run classifier to determine if image is in group A (1) or group b (0)
        out = classifier.predict(np_vec)

        if type(out) is not np.ndarray:
            print("No result returned for image {0}".format(i))
            sys.exit(-1)
        else:
            output.append(out[0])

    return zip(img, output)
