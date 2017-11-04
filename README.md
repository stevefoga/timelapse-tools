# image-classifier
=====
## Usage
These tools can be used to train a model using two sets of images, and then sort validation/target images. 

1) **Build model**: Run [generate_classifier.py](./generate_classifier.py) on a directory of desirable (known as good/positive) and undesirable (known as bad/negative) images. This outputs a sklearn.grid_search.GridSearchCV model.
2) **Execute model**: Run [sort_images.py](./sort_images.py) on a directory of images to sort them based upon the model built in step 1.

## Examples
I'm working on compiling an example of how to use these tools for filtering unlit images captured by a time-lapse camera on [my blog](https://stevefoga.wordpress.com/).

## Required Non-Standard Libraries
- numpy
- sklearn
- PIL

## Resources
I credit the majority of this work to a blog post on a now defunct site: https://web.archive.org/web/20160408173700/http://www.ippatsuman.com/2014/08/13/day-and-night-an-image-classifier-with-scikit-learn/. 
