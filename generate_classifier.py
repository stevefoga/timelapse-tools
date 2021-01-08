"""
generate_classifier.py

Purpose: Make sklearn classifier using two sets of user-supplied training images.

Author:     Steve Foga
Created:    02 Nov 2017

Python version: 3.8.2

Source: http://www.ippatsuman.com/2014/08/13/day-and-night-an-image-classifier-
        with-scikit-learn/

...or...

https://web.archive.org/web/20160408173700/http://www.ippatsuman.com/2014/08/13/
day-and-night-an-image-classifier-with-scikit-learn/
"""
import os
import glob
import json
import time
from lib import common
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn import svm
import pickle


logger = common.logger


def calc_img_vector(img_path):
    """

    :param img_path:
    :return:
    """
    #return Common.process_image(Common.open_image(img_path))
    logger.debug("     reading image {} ...".format(img_path))
    image = common.ImageIO(img_path)
    return image.get_feature_vector()


def train_classifier(train_a, train_b, class_out):
    """

    :param train_a: <list> feature vector of image A
    :param train_b: <list> feature vector of image B
    :param class_out: <str> path to output
    :return: <sklearn.grid_search.GridSearchCV> training model (also pickles to file)
    """
    # combine good and bad vectors
    data = train_a + train_b

    # allocate training classes for each image vector
    target = [1] * len(train_a) + [0] * len(train_b)

    # split training data in a train set and a test set.
    x_train, x_test, y_train, y_test = train_test_split(
        data,
        target,
        test_size=0.5)

    # define the parameter search space
    parameters = {'kernel': ['linear', 'rbf'],
                  'C': [1, 10, 100, 1000],
                  'gamma': [0.01, 0.001, 0.0001]}

    # search for the best classifier within the search space and return it
    logger.info("     running GridSearchCV to determine best classifier ...")
    clf = GridSearchCV(svm.SVC(), parameters).fit(x_train, y_train)

    # write classifier parameters to file
    if clf:
        logger.info("     writing classifer to {} ...".format(class_out))
        pickle.dump(clf, open(class_out, 'wb'))
        logger.info("     ... done")

    return clf


def get_files(f_path, f_pattern):
    files = glob.glob(os.path.join(f_path, '*' + f_pattern))
    if files:
        logger.debug("     number of *{0} files found: {1}".format(f_pattern, len(files)))
        return files
    else:
        raise Exception("Could not find files in {0} using wildcard *{1}.".
                        format(f_path, f_pattern))


def read_vector_file(vec_path):
    """

    :param vec_path:
    :return:
    """
    logger.info("     reading vector file {} ...")
    with open(vec_path) as f:
        output = json.load(f)
    logger.info("     ... done")

    return output


def write_vector_file(vec_path, data):
    """

    :param vec_path:
    :param data:
    :return:
    """
    output = os.path.join(vec_path, 'image_vector_{0}.json'.format(time.strftime("%Y%m%d-%H%M%S")))

    logger.info("     writing vector data to {} ...".format(output))
    with open(output, 'w') as f:
        json.dump(data, f)
    logger.info("     ... done")


def main(group_a, group_b, class_out, img_ext='.jpg', dryrun=False):
    """

    :param group_a: <str> path to 'good' images OR json files
    :param group_b: <str> path to 'bad' images OR json files
    :param class_out: <str> path and filename of output file
    :param img_ext: <str> image extension, e.g., '.jpg', '.png' (ignored if group_a and group_b are .json)
    :param dryrun: <bool> run code but do not save classifier
    :return:
    """
    logger.info("Input arguments:")
    logger.info("     group_a: {}".format(group_a))
    logger.info("     group_b: {}".format(group_b))
    logger.info("     class_out: {}".format(class_out))
    logger.info("     img_ext: {}".format(img_ext))
    logger.info("     dryrun: {}\n".format(dryrun))

    # sanitize args
    if os.path.isdir(class_out):
        err_msg = "class_out (-o) is a directory, must include a file name!"
        logger.error(err_msg)
        raise Exception(err_msg)

    # if the inputs are not JSON files, they are assumed to be images
    # generate vectors for all images
    logger.info("Checking to see if inputs are images or JSON files ...")
    ext_a = os.path.splitext(group_a[-1])
    logger.debug("     ext_a: {}".format(ext_a))
    ext_b = os.path.splitext(group_b[-1])
    logger.debug("     ext_b: {}".format(ext_b))

    if ext_a != '.json' and ext_b != '.json':
        logger.info("Calculating image vectors ...")
        vector_a = [calc_img_vector(i) for i in get_files(group_a, img_ext)]
        vector_b = [calc_img_vector(i) for i in get_files(group_b, img_ext)]

        # write vector files to disk
        if not dryrun:
            write_vector_file(group_a, vector_a)
            write_vector_file(group_b, vector_b)
        else:
            print("--dryrun used, no results saved.")

    elif ext_a == '.json' and ext_b == '.json':
        logger.info("Reading vectorized image inputs from JSON files ...")
        vector_a = read_vector_file(group_a)
        vector_b = read_vector_file(group_b)

    else:
        raise Exception("Incorrect extensions supplied. ext_a={0} | ext_b={1}".format(ext_a, ext_b))

    # train the classifier for the image sets
    logger.info("Training classifier ...")
    train_classifier(vector_a, vector_b, class_out)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build classification model")

    req_named = parser.add_argument_group("Required named arguments")

    req_named.add_argument("--pos", help="Dir of positive/good images)", dest="group_a", required=True)
    req_named.add_argument("--neg", help="Dir of negative/bad images)", dest="group_b", required=True)
    req_named.add_argument("-o", help="Path and filename for output classification", dest="class_out", required=True)
    req_named.add_argument("-e", help="Image extent (default=.jpg)", dest="img_ext", default='.jpg', required=False)

    parser.add_argument("--dryrun", help="Run script, but do not execute actions", action="store_true", required=False)

    arguments = parser.parse_args()

    #print(arguments)

    main(**vars(arguments))
