'''
daily_subset_and_rename.py

Purpose: copy images from times X to Y for each day to new folder, optionally rename using batch_rename.py


'''
import os
import sys
import glob
import re
import shutil
import batch_rename


def int2padstr(int_val):
    """

    :param int_val:
    :return:
    """
    if int_val < 10:
        return str(int_val).zfill(2)
    else:
        return str(int_val)


def build_regex(int_val, end_val=9):
    """

    :param int_val:
    :param end_val:
    :return:
    """
    return '[{0}][{1}-{2}]'.format(int_val[0], int_val[1], end_val)


def build_re_range(val_one, val_two):
    # make sure numbers have ones and tens place
    str_one = int2padstr(val_one)
    str_two = int2padstr(val_two)

    # if same tens place, do not create min|max range
    if str_one[0] == str_two[0]:
        time_range = '{0}'.format(build_regex(str_one, end_val=int(str_two[1])))
    else:
        time_range = '[{0}|{1}]'.format(build_regex(str_one), build_regex(str_two))

    return re.compile(time_range + ':\d{2}:\d{2}')


def main(src, dst, time_start, time_end, ext='.jpg', renumber=False, dryrun=False):
    """

    :param dir_in: <str>
    :param dir_out: <str>
    :param time_start: <int>
    :param time_end: <int>
    :param ext: <str>
    :param renumber: <bool>
    :param dryrun: <bool>
    :return:
    """
    if not os.path.exists(dst) and not dryrun:
        print("Creating directory {0}".format(dst))
        os.mkdir(dst)

    # get files
    fn_in = sorted(glob.glob(os.path.join(src, '*' + ext)))
    if not fn_in:
        sys.exit("Could not find any files for input dir {0} using extension {1}".format(src, ext))

    # sort files by time of day
    fn_in_match = [i for i in fn_in if build_re_range(time_start, time_end).findall(i)]
    if not fn_in_match:
        sys.exit("Could not find any matches in {0} between hours {1} and {2}".format(src, time_start, time_end))

    # copy to new dir
    if not dryrun:
        [shutil.copy2(fc, dst) for fc in fn_in_match]

        # optionally re-number using batch_rename.py
        if renumber:
            batch_rename.main(dst, renumber=True)

    else:
        print("--dryrun uesd; no files will be moved. Results: {0}".format(fn_in_match))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    req_named = parser.add_argument_group("Required named arguments")

    req_named.add_argument("src", help="Dir of input images.")
    req_named.add_argument("dst", help="Output dir for moved images.")
    req_named.add_argument("time_start", help="Start hour.")
    req_named.add_argument("time_end", help="End hour.")

    parser.add_argument("--ext", help="Extension of input files (default='.jpg')", default=".jpg", required=False)
    parser.add_argument("--renumber", help="Rename files to sequential numbers by alphanumeric order",
                        action="store_true", required=False)
    parser.add_argument("--dryrun", help="Run script, but do not execute actions", action="store_true", required=False)

    arguments = parser.parse_args()

    main(**vars(arguments))
