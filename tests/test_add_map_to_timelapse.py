import pytest
import add_map_to_timelapse


crds = [45, 20, 102872980]
exif_data = {
    1: u'N',
    2: ((44, 1), (11, 1), (102872399, 10000000)),
    3: u'W',
    4: ((94, 1), (0, 1), (178621199, 10000000)),
    5: '\x00',
    6: (280381, 1000),
    7: ((20, 1), (9, 1), (18, 1)),
    29: u'2018:01:01'
}
x_size = 20
y_size = 20
mp_size = 200
mp_dpi = 300
map_dim = 200
img_dim = 2000

def test_get_dd():
    dd_out = add_map_to_timelapse.get_dd(crds)
    assert dd_out == 45.335047883

def test_get_coords():
    lat, long = add_map_to_timelapse.get_coords(exif_data)
    assert lat == 44.18504787331667
    assert long == -94.00297701998333

def test_calc_map_dims():
    x_dim, y_dim = add_map_to_timelapse.calc_map_dims(x_size, y_size, mp_size, mp_dpi)
    assert x_dim == 0.13333333333333333
    assert y_dim == 0.13333333333333333

def test_calc_map_dims_bad_x():
    with pytest.raises(Exception):
        add_map_to_timelapse.calc_map_dims(-1, y_size, mp_size, mp_dpi)

def test_calc_map_dims_bad_y():
    with pytest.raises(Exception):
        add_map_to_timelapse.calc_map_dims(x_size, -10, mp_size, mp_dpi)

def test_calc_map_dims_bad_size():
    with pytest.raises(Exception):
        add_map_to_timelapse.calc_map_dims(x_size, y_size, 0, mp_dpi)

def test_calc_map_dims_bad_dpi():
    with pytest.raises(Exception):
        add_map_to_timelapse.calc_map_dims(x_size, y_size, mp_size, -100)

def test_scale_map_to_img():
    map_pos = add_map_to_timelapse.scale_map_to_img(map_dim, img_dim)
    assert map_pos == 250000
