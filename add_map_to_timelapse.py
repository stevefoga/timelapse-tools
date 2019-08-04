"""
add_map_to_timelapse.py

Purpose: for all geotagged images, derive a common map, track progress of each image, and overlay map on a copy of
         the images. Currently only works with GoPro geotags; support for other imagery could be created by modifying
         the get_coords() function, and the index key used to invoke it.

TODO:
    1) add option to control map location
    2) create option to call Open Street Map API for basemap
    3) create standalone executable (see: cpython, PyInstaller)

Author: Steve Foga
Created: 12 May 2018
Python version: 2.7.12
"""
import os
import glob
import warnings
import matplotlib.pyplot as plt
from PIL import Image
from collections import OrderedDict
from lib import common, geotools

## TODO: add logging module, use debug for coordinate conversion
## example: image 756 jumps


def main(src, breadcrumbs, keep_map, dryrun, map_size, map_dpi, map_x, map_y, map_line_width, map_alpha, map_point_size,
         map_point_color, bc_point_size, bc_point_color):
    if not os.path.isdir(src):
        raise Exception("src must be a directory")

    img_in = glob.glob(os.path.join(src, "*.JPG"))

    if not img_in:
        raise Exception("could not find JPG images in {0}".format(src))

    img_coords = OrderedDict()

    it = 0
    total = len(img_in)

    for i in img_in:

        it += 1
        common.progress(it, total, "coords extracted from exif")

        #io = Common.open_image(i)
        #info = io._getexif()
        image = common.ImageIO(i)

        #print(info)

        # write [lat, long] to dictonary key 'image.JPG'
        try:
            #img_coords[i] = geotools.get_coords(info[34853])
            img_coords[i] = geotools.get_coords(image.image_exif[34853])
        except KeyError:
            warnings.warn("Skipping: Could not find coordinates for image {0}".format(i))
            continue

    # grab size of last image opened (assuming all images are same size; to be used for scaling map later)
    #img_y = io.size[1]
    #img_x = io.size[0]
    img_x, img_y = image.get_size()

    map_x_dim, map_y_dim = geotools.calc_map_dims(img_x, img_y, map_size, map_dpi)

    # set map within target image
    map_y_pos = geotools.scale_map_to_img(map_y, img_y)
    map_x_pos = geotools.scale_map_to_img(map_x, img_x)

    # determine bounding box of all images
    lats = [lc[0] for lc in img_coords.values()]
    longs = [lc[1] for lc in img_coords.values()]

    # make plot
    plt.plot(longs, lats)

    # make plot for each image
    if breadcrumbs:
        prev_pts = []

    it = 0
    total = len(img_coords)

    for img_path, value in img_coords.items():

        it += 1
        common.progress(it, total, "maps plotted")

        '''
        # open image as plot
        img = plt.imread(img_path)
        img_dims = img.shape
        y_map = img_dims[0] * (map_size * 0.01)
        x_map = img_dims[1] * (map_size * 0.01)
        #imgplot = plt.imshow(img)
        '''
        # configure map plot dimensions
        plt.rcParams["figure.figsize"] = (map_x_dim, map_y_dim)

        # initiate plots
        fig, ax = plt.subplots()

        # set farthest background layer as transparent
        fig.patch.set_alpha(0.0)

        # disable map plot frame
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        ax.plot(longs, lats, linewidth=map_line_width, zorder=1)
        if not breadcrumbs:
            ax.plot(value[1], value[0], marker='o', zorder=2, color=map_point_color, markersize=map_point_size)

        else:
            if prev_pts:  # make breadcrumbs on plot
                ax.scatter([lc[1] for lc in prev_pts], [lc[0] for lc in prev_pts], c=bc_point_color, s=bc_point_size,
                           linewidth=0, zorder=2)
                ax.plot(value[1], value[0], marker='o', color=map_point_color, markersize=map_point_size, zorder=3)

            else:
                ax.plot(value[1], value[0], marker='o', color=map_point_color, markersize=map_point_size, zorder=2)

            prev_pts.append(value)

        # set axes to specific alpha
        ax.patch.set_alpha(map_alpha)

        # exclude axes
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

        # export as transparent
        png_out = os.path.splitext(img_path)[0] + "_transparent.png"

        fig.savefig(png_out)
        plt.close('all')

        # open target image
        #base_img = common.open_image(img_path)
        #map_img = common.open_image(png_out)
        base_img = common.ImageIO(img_path)
        map_img = common.ImageIO(png_out)

        # overlay PNG on target image
        #base_img_rgba = base_img.convert("RGBA")
        #map_img_rgba = map_img.convert("RGBA")
        #base_img_rgba.paste(map_img_rgba, (map_x_pos, map_y_pos), map_img_rgba)
        base_img_rgba = base_img.overlay(map_img, map_x_pos, map_y_pos)

        # save target image to new location
        img_out = os.path.splitext(img_path)[0] + "_map.JPG"
        if not dryrun:
            # convert RGBA to RGB w/ mask (otherwise JPG format will not work)
            # solution found at https://stackoverflow.com/a/9459208
            #base_img_jpg_out = Image.new("RGB", base_img_rgba.size, (255, 255, 255))
            #base_img_jpg_out.paste(base_img_rgba, mask=base_img_rgba.split()[3])
            base_img_jpg_out = base_img_rgba.rgba_to_rgb_mask()

            # write image to JPG file
            base_img_jpg_out.save(img_out)

        # clean up old transparency
        if not keep_map:
            os.remove(png_out)


if __name__ == "__main__":
    import argparse

    # functions to define specific data type ranges
    def restricted_float(x):
        x = float(x)
        if x < 0.0 or x > 1.0:
            raise argparse.ArgumentTypeError("{0} not in range [0.0, 1.0]".format(x,))
        return x

    def restricted_int(x):
        if x is int:
            if x < 0 or x > 100:
                raise argparse.ArgumentTypeError("{0} not in range [0, 100]".format(x))
            return x
        else:
            raise argparse.ArgumentTypeError("{0} must be type int".format(x))

    parser = argparse.ArgumentParser(description='Add map to geotagged GoPro images.', add_help=False)

    # argument categories
    req = parser.add_argument_group("Required arguments")
    opt_flag = parser.add_argument_group("Optional flags")
    opt_map = parser.add_argument_group("Optional map arguments")

    # required args
    req.add_argument("src", help="Directory containing images")

    # optional flags
    opt_flag.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    opt_flag.add_argument("--breadcrumbs", action="store_true",
                          help="Insert gray dots for previously visited location, relative to time series",
                          required=False)
    opt_flag.add_argument("--keep-map", action="store_true", help="Save copy of map as separate image '*_map.JPG'",
                          required=False)
    opt_flag.add_argument("--dryrun", action="store_true",
                          help="Run script, but do not alter files (cleans up all intermediate files)",
                          default=False)

    # optional map args
    opt_map.add_argument("--map-size",
                         help="Percent of image space of which the map will occupy (range=(0, 100), default=20)",
                         default=20, type=restricted_int, required=False)
    opt_map.add_argument("--map-dpi", help="DPI of map (default=50)", default=50, type=int, required=False)
    opt_map.add_argument("--map-x", help="X location of map relative to target image (range=(0.0, 1.0), default=1.0)",
                         default=1.0, type=restricted_float, required=False)
    opt_map.add_argument("--map-y", help="Y location of map relative to target image (range=(0.0, 1.0), default=1.0)",
                         default=1.0, type=restricted_float, required=False)
    opt_map.add_argument("--map-line-width", help="Width of map line (default=3)", default=3, type=float,
                         required=False)
    opt_map.add_argument("--map-alpha", help="Level of transparency of map background (range=(0.0,1.0), default=0.25)",
                         type=restricted_float, default=0.25, required=False)
    opt_map.add_argument("--map-point-size", help="Size of current location point (default=25)", type=int, default=25,
                         required=False)
    opt_map.add_argument("--map-point-color", help="Color of current location point (default=gray)", default='red',
                         required=False)
    opt_map.add_argument("--bc-point-size", help="Size of breadcrumb point(s) (default=10)", type=int, default=10,
                         required=False)
    opt_map.add_argument("--bc-point-color", help="Color of breadcrumb point(s) (default=gray)", default='gray',
                         required=False)

    arguments = parser.parse_args()

    main(**vars(arguments))
