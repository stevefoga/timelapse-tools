"""
sort_images.py

Purpose: Call classify_images.py, and use those results to sort images

Author:     Steve Foga
Created:    02 Nov 2017

Python version: 2.7.12
"""
import os
import sys
import pickle
import time
from classify_images import classify

t0 = time.time()


def main(img_path, img_ext, model, good_path, bad_path, dryrun=False):
    """
    :param img_path: <str> path to dir containing image(s)
    :param img_ext: <str> image extent (e.g., '.jpg')
    :param model: <str> path to model file
    :param good_path: <str> path to output dir for good/matching image(s)
    :param bad_path: <str> path to output dir for bad/non-matching image(s)
    :param dryrun: <bool> run code but do not move images

    :return:
    """
    # load classifier model
    clf = pickle.load(open(model, 'rb'))

    # classify images
    results = classify(img_path, img_ext, clf)

    for result in results:
        img_name = os.path.basename(result[0])
        if result[1] == 0:
            print("GOOD. Moving {0} to {1}".format(result[0], os.path.join(bad_path, img_name)))
            if not dryrun:
                os.rename(result[0], os.path.join(bad_path, img_name))

        elif result[1] == 1:
            print("BAD. Moving {0} to {1}".format(result[0], os.path.join(good_path, img_name)))
            if not dryrun:
                os.rename(result[0], os.path.join(good_path, img_name))

        else:
            print("Result value {0} is not 0 or 1.".format(result[1]))
            sys.exit(-1)

        if dryrun:
            print("--dryrun option used, no files moved.")

    t1 = time.time()
    m, s = divmod(t1 - t0, 60)
    h, m = divmod(m, 60)
    print("Total runtime: {0}h, {1}m, {2}s.".format(h, round(m, 3), round(s, 3)))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Classify images using classify_images.py, and sort into output dirs")

    req_named = parser.add_argument_group("Required named arguments")

    req_named.add_argument("-i", help="Path to image(s)", dest="img_path", required=True)
    req_named.add_argument("-e", help="Image extension (e.g., .jpg)", dest="img_ext", required=True)
    req_named.add_argument("-m", help="Path to model file", dest="model", required=True)
    req_named.add_argument("--pos", help="Output dir path for good image(s)", dest="good_path", required=True)
    req_named.add_argument("--neg", help="Output dir path for bad image(s)", dest="bad_path", required=True)

    parser.add_argument("--dryrun", help="Run script, but do not execute actions", action="store_true", required=False)

    arguments = parser.parse_args()

    main(**vars(arguments))
