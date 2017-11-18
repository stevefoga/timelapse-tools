'''
batch_rename.py

Purpose: remove special characters that are inserted by the timelapse cam.

Author:     Steve Foga
Created:    18 November 2017

Python version: 2.7.10
'''
import os
import shutil
import glob

def main(src, dst=None, dryrun=False, renumber=False):

    print("dst: {0}".format(dst))
    fn_in = sorted(glob.glob(os.path.join(src,'*.jpg')))

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
            print("Dryrun: move {0} to {1}".format(f, fn_out))
        else:
            shutil.move(f, fn_out)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    req_named = parser.add_argument_group("Required named arguments")

    req_named.add_argument("src", help="Dir of input images; will overwrite files if -o not specified.")

    parser.add_argument("-o", help="Output dir", dest="dst", required=False)
    parser.add_argument("--renumber", help="Rename files to sequential numbers by alphanumeric order",
                        action="store_true", required=False)
    parser.add_argument("--dryrun", help="Run script, but do not execute actions", action="store_true", required=False)

    arguments = parser.parse_args()

    main(**vars(arguments))
