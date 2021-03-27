"""
batch_rename.py

Purpose: remove special characters that are inserted by the timelapse cam.

Author:     Steve Foga
Created:    18 November 2017

Python version: 3.9.2
"""
import os
import shutil
import glob

DEFAULT_EXTENSION = "jpg"


def get_sorted_images(src, ext):
    """

    :param src: <str>
    :param ext: <str>
    :return: <list>
    """
    return sorted(glob.glob(os.path.join(src, '*.{}'.format(ext))))


def batch_rename(src, extension=DEFAULT_EXTENSION, dst=None, move=False, renumber=False, dryrun=False):

    print("dst: {0}".format(dst))
    fn_in = get_sorted_images(src, extension)
    if not fn_in:
        fn_in = get_sorted_images(src, extension.upper())
        if not fn_in:
            fn_in = get_sorted_images(src, extension.lower())
    if not fn_in:
        raise Exception(f"No input images found in '{src}' with extensions '{extension}' "
                        f"(also tried '{extension.upper()}' and '{extension.lower()}')")

    if renumber:
        img_ct = 0
        # determine number of digits
        num_dig = len(str(len(fn_in)))

    for f in fn_in:
        fin = os.path.splitext(os.path.basename(f))[0]

        if renumber:
            # override entire filename with sequential value
            img_ct += 1
            fin_fix = str(img_ct).zfill(num_dig)
        else:
            # scrub the unwanted values
            fin_fix = fin.replace(":", "")
            fin_fix = fin_fix.replace("-", "")
            fin_fix = fin_fix.replace("_", "")

        fout = f.replace(fin, fin_fix)

        if dst:
            fn_out = os.path.join(dst, os.path.split(fout)[-1])
        else:
            fn_out = os.path.join(os.path.dirname(f), fout)

        if dryrun:
            print("Dryrun: copy {0} to {1}".format(f, fn_out))
        else:
            if move:
                shutil.move(f, fn_out)
            else:
                shutil.copy2(f, fn_out)  # use .copy2() to preserve metadata


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    req_named = parser.add_argument_group("Required named arguments")

    req_named.add_argument("src", help="Dir of input images; will overwrite files if -o not specified.")

    parser.add_argument("-e", "--ext",
                        help=f"File extension (will attempt lowercase and UPPERCASE instances of this string "
                             f"if the input fails (defaut={DEFAULT_EXTENSION})", dest="extension",
                        default=DEFAULT_EXTENSION)
    parser.add_argument("-o", help="Output dir", dest="dst", required=False)
    parser.add_argument("--renumber", help="Rename files to sequential numbers by alphanumeric order",
                        action="store_true", required=False)
    parser.add_argument("-m", "--move", help="Move files instead of making a copy", action="store_true", required=False)
    parser.add_argument("--dryrun", help="Run script, but do not execute actions", action="store_true", required=False)

    arguments = parser.parse_args()

    batch_rename(**vars(arguments))
