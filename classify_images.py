"""
classify_image.py

Purpose:    Use classifier made by generate_classifier.py to classify an image.

Author:     Steve Foga
Created:    02 Nov 2017

Python version: 3.8.2
"""
import os
import glob
import numpy as np

from lib import common


logger = common.logger


def classify(img_in, img_ext, model, subset_count=False):
    """
    Classify images, return text file of file paths of grouped images.

    :param img_in: <str> Path to images to be classified
    :param img_ext: <str> Image extension, e.g., '.jpg'
    :param model: <sklearn.grid_search.GridSearchCV> model file (hint: read with pickle.load())
    :param subset_count: <int> subset number of test images to use instead of the entire dataset

    :return: <list> zipped with (/path/to/image.ext, 0_or_1)
    """
    # find images
    img_path = os.path.join(img_in, '*' + img_ext)
    logger.debug("image path with wildcard: {}".format(img_path))
    img = glob.glob(img_path)
    if not img:
        raise Exception("Could not find images for string {0}".format(img_path))
    total_img_count = len(img)
    logger.info("number of images found: {}".format(total_img_count))
    # handle subset, if supplied
    if subset_count:
        if subset_count < 1:
            raise Exception("Subset count must be greater than 0, value supplied: {}".format(subset_count))
        if subset_count >= total_img_count:
            subset_count = total_img_count
        logger.info("Subset specified, using only first {} images".format(subset_count))
        img = img[0:subset_count]

    # get the best estimate from the classifier
    logger.info("Getting classifier ...")
    classifier = model.best_estimator_

    output = []
    counter = 0
    logger.info("Applying classifier to each image ...")
    for i in img:
        # read target image(s)
        img_open = common.ImageIO(i)
        #img_open = Common.open_image(i)

        # open image as vector
        img_vec = img_open.get_feature_vector()

        # reshape vector (sklearn >= 0.19 requires this)
        np_vec = np.array(img_vec).reshape((len(img_vec), 1)).reshape(1, -1)

        # run classifier to determine if image is in group A (1) or group b (0)
        out = classifier.predict(np_vec)

        if type(out) is not np.ndarray:
            raise Exception("No result returned for image {0}".format(i))
        else:
            output.append(out[0])

        counter += 1
        common.progress(counter, total_img_count, "images classified")

    return zip(img, output)
