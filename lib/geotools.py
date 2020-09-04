"""
geotools.py

Purpose: general tools for handing geospatial information.

Author:     Steve Foga
Created:    03 Aug 2019
"""


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


def calc_map_dims(x_size, y_size, mp_size, mp_dpi):
    """
    Calculate output map size.

    :param x_size: <int or float> Image x dimension
    :param y_size: <int or float> Image y dimension
    :param mp_size: <int> Percent of image space of which the map will occupy
    :param mp_dpi: <int> Map density, as dots per inch
    :return: <list> [x_dimension, y_dimension]
    """
    if x_size <= 0:
        raise Exception("x_size must be greater than 0; value supplied: {0}".format(x_size))
    if y_size <= 0:
        raise Exception("y_size must be greater than 0; value supplied: {0}".format(y_size))
    if mp_size <= 0:
        raise Exception("mp_size must be greater than 0; value supplied: {0}".format(mp_size))
    if mp_dpi <= 0:
        raise Exception("mp_dpi must be greater than 0; value supplied: {0}".format(mp_dpi))

    img_y_scaled = y_size * (mp_size * 0.01)
    img_x_scaled = x_size * (mp_size * 0.01)

    map_y_dim = img_y_scaled / mp_dpi
    map_x_dim = img_x_scaled / mp_dpi

    return map_x_dim, map_y_dim


def scale_map_to_img(map_dim, img_dim):
    """
    Set map position, relative to the base image
    # TODO: fix this so plot offset works in any margin (only works in LR now)
    :param map_dim: <int or float>
    :param img_dim: <int or float>
    :return: <int or float>
    """
    # using /1.6 to offset from the lower left edge
    map_pos = int(round((map_dim * img_dim) / 1.6))

    return map_pos