'''
add_map_to_timelapse.py

Purpose: for all geotagged images, derive a common map, track progress of each image, and overlay map on a copy of
         the images. Currently only works with GoPro geotags; support for other imagery could be created by modifying
         the get_coords() function, and the index key used to invoke it.

TODO:
    1) add argparse
    2) add custom graphics options for #1
    3) add option to control map location
    4) create option to call Open Street Map API for basemap
    5) create standalone executable (see: cpython, PyInstaller)

Author: Steve Foga
Created: 12 May 2018
Python version: 2.7.12
'''
import sys
import os
import glob
from PIL import Image
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

    long = [exif_data[4][i][0] for i in range(len(exif_data[4]))]
    if exif_data[3] == 'W':
        long[0] = long[0] * -1

    # convert degrees + decimal minutes to decimal degrees
    lat_dd = get_dd(lat)
    long_dd = get_dd(long)

    return [lat_dd, long_dd]


def main():
    if not img_in:
        sys.exit("could not find JPG images in {0}".format(dir_in))

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

    img_y_scaled = img_y * (map_pct_size * 0.01)
    img_x_scaled = img_x * (map_pct_size * 0.01)

    map_y_dim = img_y_scaled / map_dpi
    map_x_dim = img_x_scaled / map_dpi

    # map position, relative to the base image
    # /1.5 to offset from the lower left edge
    # TODO: fix this so plot offset works in any margin
    map_y_pos = int(round((map_y * img_y) / 1.6))
    map_x_pos = int(round((map_x * img_x) / 1.6))

    # determine bounding box of all images
    lats = [lc[0] for lc in img_coords.values()]
    longs = [lc[1] for lc in img_coords.values()]

    '''
    min_x = min(longs)
    max_x = max(longs)
    min_y = min(lats)
    max_y = max(lats)
    '''

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
        y_map = img_dims[0] * (map_pct_size * 0.01)
        x_map = img_dims[1] * (map_pct_size * 0.01)
        #imgplot = plt.imshow(img)
        '''
        # configure map plot dimensions
        plt.rcParams["figure.figsize"] = (map_x_dim, map_y_dim)
        #fig, ax = plt.figure(figsize=(map_x_dim, map_y_dim), dpi=map_dpi)

        fig, ax = plt.subplots()

        #fig.patch.set_alpha(alpha_level)
        fig.patch.set_alpha(0.0)

        # disable map plot frame
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        #fig.tick_params(top='off', bottom='off', left='off', right='off', labelleft='off', labelbottom='off')

        ax.plot(longs, lats, linewidth=line_width, zorder=1)
        if not breadcrumbs:
            ax.plot(value[1], value[0], 'ro', zorder=2)

        else:
            if prev_pts:
                ax.scatter([lc[1] for lc in prev_pts], [lc[0] for lc in prev_pts], c='gray', s=100, linewidth=0, zorder=2)
                ax.scatter(value[1], value[0], c='red', s=250, zorder=3)

            else:
                ax.scatter(value[1], value[0], c='red', s=250, zorder=2)

            prev_pts.append(value)

        # set axes to specific alpha
        ax.patch.set_alpha(alpha_level)

        # exclude axes
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        #ax.xticks([])
        #ax.yticks([])


        # export as transparent
        png_out = os.path.splitext(img_path)[0] + "_transparent.png"
        # set background color, if applicable
        #if bg_color:
        #    #ax.patch.set_facecolor(bg_color)
        #    fig.patch.set_alpha(0.5)
        #    fig.savefig(png_out)
        #else:

        #fig.savefig(png_out, transparent=True)
        fig.savefig(png_out)
        plt.close('all')

        # open target image
        base_img = Common.open_image(img_path)
        map_img = Common.open_image(png_out)

        # overlay PNG on target image
        base_img_rgba = base_img.convert("RGBA")
        map_img_rgba = map_img.convert("RGBA")
        base_img_rgba.paste(map_img_rgba, (map_x_pos, map_y_pos), map_img_rgba)
        #base_map = Imagbe.alpha_composite(base_img_rgba, map_img)
        # base_map = Image.blend(base_img, map_img, alpha=0.8)  # "images do not match"

        # save target image to new location
        img_out = os.path.splitext(img_path)[0] + "_map.JPG"
        base_img_rgba.save(img_out)

        # clean up old transparency
        if not keep_map:
            os.remove(png_out)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Add map to geotagged GoPro images.')

    # TODO: sort between "required", "optional features", and "optional graphics" (or something)
    parser.add_argument("src", description="Directory containing images")

    parser.add_argument("--breadcrumbs", action="store_true",
                        description="Insert gray dots for previously visited location, relative to time series",
                        required=False)

    parser.add_argument("--map-size", description="Percent of image space of which the map will occupy (default=20)",
                        default=20, range=(0,100), required=False)
    parser.add_argument("--map-dpi", description="DPI of map (default=50)", default=50, required=False)
    parser.add_argument("--map-x")
    parser.add_argument("--map-y")
    # TODO: finish me!
    dir_in = "/home/chrx/Projects/gopro_timelapse/"
    img_in = sorted(glob.glob(dir_in + "*.JPG"))
    breadcrumbs = True
    map_pct_size = 20  # (0-100, default=20) percent of image map occupies
    map_dpi = 50
    map_x = 1  # 0-1, where 0 is upper-left, 1 is lower-right
    map_y = 1
    line_width = 3
    alpha_level = 0.25
    # map_loc = "SE"  # (cardinal directions, default="SE") location of map on image
    keep_map = True
    bg_color = 'gray'