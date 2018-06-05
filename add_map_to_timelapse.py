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
import sys
import os
import glob
import matplotlib.pyplot as plt
from lib.common import Common


def progress(count, total, suffix=''):
    """
    Display progress bar in command line

    :param count: <int> current iteration
    :param total: <int> total number of iterations
    :param suffix: <str> text to be plotted next to bar (should be description of progress)
    :return:
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[{0}] {1}{2} {3}\r'.format(bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben


def get_dd(crds):
    """
    Convert degrees+decimal minutes to decimal degrees

    :param crds: <list> [degrees, minutes, decimal minutes]
    :return: <float> decimal degrees
    """
    # combine minutes and decimal minutes to form single number
    dec_min = crds[1] + float('.0' + '0'.zfill(len(str(crds[2])) - 2) + '1') * crds[2]

    # conversion equation
    if crds[0] < 0:
        dec_deg = crds[0] - (dec_min / 60.)
    else:
        dec_deg = crds[0] + (dec_min / 60.)

    return dec_deg


def get_coords(exif_data):
    """
    Get coordinates from gopro exif data.

    :param exif_data: <dict> dictionary of gps data
    :return: <list> [longitude,latitude] in decimal degrees
    """
    # extract coordinates from exif data
    lat = [exif_data[2][i][0] for i in range(len(exif_data[2]))]
    if exif_data[1] == 'S':
        lat[0] = lat[0] * -1

    lng = [exif_data[4][i][0] for i in range(len(exif_data[4]))]
    if exif_data[3] == 'W':
        lng[0] = lng[0] * -1

    # convert degrees + decimal minutes to decimal degrees
    lat_dd = get_dd(lat)
    long_dd = get_dd(lng)

    return [lat_dd, long_dd]


def main(src, breadcrumbs, keep_map, dryrun, map_size, map_dpi, map_x, map_y, map_line_width, map_alpha, map_point_size,
         map_point_color, bc_point_size, bc_point_color):
    if not os.path.isdir(src):
        raise Exception("src must be a directory")

    img_in = glob.glob(src + "*.JPG")

    if not img_in:
        raise Exception("could not find JPG images in {0}".format(src))

    img_coords = {}

    it = 0
    total = len(img_in)

    for i in img_in:

        it += 1
        progress(it, total, "coords extracted from exif")

        io = Common.open_image(i)
        info = io._getexif()

        #print(info)

        # write [lat, long] to dictonary key 'image.JPG'
        img_coords[i] = get_coords(info[34853])

    # calculate output map size
    # grab size of last image opened (assuming all images are same size; to be used for scaling map later)
    img_y = io.size[1]
    img_x = io.size[0]

    img_y_scaled = img_y * (map_size * 0.01)
    img_x_scaled = img_x * (map_size * 0.01)

    map_y_dim = img_y_scaled / map_dpi
    map_x_dim = img_x_scaled / map_dpi

    # map position, relative to the base image
    # /1.5 to offset from the lower left edge
    # TODO: fix this so plot offset works in any margin (only works in LR now)
    map_y_pos = int(round((map_y * img_y) / 1.6))
    map_x_pos = int(round((map_x * img_x) / 1.6))

    # determine bounding box of all images
    lats = [lc[0] for lc in img_coords.values()]
    longs = [lc[1] for lc in img_coords.values()]

    # make plot
    plt.plot(lats, longs)

    # make plot for each image
    if breadcrumbs:
        prev_pts = []

    it = 0
    total = len(img_coords)

    for img_path, value in img_coords.items():

        it += 1
        progress(it, total, "maps plotted")

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
            ax.plot(value[1], value[0], 'ro', zorder=2)

        else:
            if prev_pts:
                ax.scatter([lc[1] for lc in prev_pts], [lc[0] for lc in prev_pts], c=bc_point_color, s=bc_point_size,
                           linewidth=0, zorder=2)
                ax.scatter(value[1], value[0], c=map_point_color, s=map_point_size, zorder=3)

            else:
                ax.scatter(value[1], value[0], c=map_point_color, s=map_point_size, zorder=2)

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
        base_img = Common.open_image(img_path)
        map_img = Common.open_image(png_out)

        # overlay PNG on target image
        base_img_rgba = base_img.convert("RGBA")
        map_img_rgba = map_img.convert("RGBA")
        base_img_rgba.paste(map_img_rgba, (map_x_pos, map_y_pos), map_img_rgba)

        # save target image to new location
        img_out = os.path.splitext(img_path)[0] + "_map.JPG"
        if not dryrun:
            base_img_rgba.save(img_out)

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
                          help="Run script, but do not alter files (cleans up all intermediate files",
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
    opt_map.add_argument("--map-point-size", help="Size of current location point (default=250)", type=int, default=250,
                         required=False)
    opt_map.add_argument("--map-point-color", help="Color of current location point (default=gray)", default='red',
                         required=False)
    opt_map.add_argument("--bc-point-size", help="Size of breadcrumb point(s) (default=100)", type=int, default=100,
                         required=False)
    opt_map.add_argument("--bc-point-color", help="Color of breadcrumb point(s) (default=gray)", default='gray',
                         required=False)

    arguments = parser.parse_args()

    main(**vars(arguments))
