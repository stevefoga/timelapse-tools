[![Build status](https://travis-ci.org/stevefoga/image-classifier.svg?master)](https://travis-ci.org/stevefoga)
# timelapse-tools

## Usage
This toolbox can be used to train a model using two sets of images, and then sort validation/target images; rename 
images to assist in time lapse creation; overlay a map on geotagged time lapse images. 

### Image classifier
1) **Build model**: Run [generate_classifier.py](./generate_classifier.py) on a directory of desirable (known as 
   good/positive) and undesirable (known as bad/negative) images. This outputs a sklearn.model_selection.GridSearchCV 
   model.
2) **Execute model**: Run [sort_images.py](./sort_images.py) on a directory of images to sort them based upon the 
   model built in step 1.

### Video creation tools
Additionally, the following utilities are included to facilitate time lapse video creation:

1) **Re-number files**: Run [batch_rename.py](utils/batch_rename.py) to sort and renumber (`--renumber`) all images 
   files, padded with zeros to match the maximum file count. The software ffmpeg requires input images to be numbered 
   as such.
2) **Pull specific time(s) of day**: Run [daily_subset_and_rename.py](utils/daily_subset_and_rename.py) to grab images 
   between specific hour(s) of day, move to new folder, and optionally call [batch_rename.py](utils/batch_rename.py) 
   to re-number the files after they are moved.
3) **Decimate files**: Run [reduce_frames.py](utils/reduce_frames.py) to remove files based upon a "keep factor" 
   (e.g., a factor of '4' keeps every fourth image.) Images will automatically be renumbered, but can be disabled. 

### Map overlay
Run [add_map_to_timelapse.py](add_map_to_timelapse.py) to add map to images (note: only works with GoPro's geotags.)

## Examples
I have written an example of how to use these tools for filtering unlit images captured by a time-lapse camera on 
[my blog](https://stevefoga.wordpress.com/).

## Required Non-Standard Libraries
- numpy
- sklearn
- pillow (PIL)

Conda one-liner to create environment:
```
create --yes --name timelapse-tools -c conda-forge python=3 numpy scipy scikit-learn pillow
```  

## Resources
I credit this work in part to this blog post: 
http://www.ippatsuman.com/2014/08/13/day-and-night-an-image-classifier-with-scikit-learn/
