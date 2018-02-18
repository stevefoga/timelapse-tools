[![Build status](https://travis-ci.org/stevefoga/image-classifier.svg?master)](https://travis-ci.org/stevefoga)
# image-classifier

## Usage
These tools can be used to train a model using two sets of images, and then sort validation/target images. 

1) **Build model**: Run [generate_classifier.py](./generate_classifier.py) on a directory of desirable (known as good/positive) and undesirable (known as bad/negative) images. This outputs a sklearn.grid_search.GridSearchCV model.
2) **Execute model**: Run [sort_images.py](./sort_images.py) on a directory of images to sort them based upon the model built in step 1.

Additionally, the following utilities are included to facilitate time lapse video creation:

1) **Re-number files**: Run [batch_rename.py](utils/batch_rename.py) to renumber all images files, padded with zeros to match the maximum file count, where files are initially sorted alphanumerically.
2) **Pull specific time(s) of day**: Run [daily_subset_and_rename.py](utils/daily_subset_and_rename.py) to grab images between specific hour(s) of day, move to new folder, and optionally call [batch_rename.py](utils/batch_rename.py) to re-number the files after they are moved.

## Examples
I have written an example of how to use these tools for filtering unlit images captured by a time-lapse camera on [my blog](https://stevefoga.wordpress.com/).

## Required Non-Standard Libraries
- numpy
- sklearn
- pillow (PIL)

## Resources
I credit the majority of this work to this blog post: http://www.ippatsuman.com/2014/08/13/day-and-night-an-image-classifier-with-scikit-learn/
