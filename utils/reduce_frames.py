import os
import sys
import glob
from shutil import copyfile


DEFAULT_FILE_EXTENSION = ".jpg"
DEFAULT_KEEP_FACTOR = 2
TRANSFER_METHODS = ["link", "copy"]
DEFAULT_TRANSFER_METHOD = "link"


def do_transfer(fn_in, fn_out, transfer_method):
	if transfer_method == "link":
		os.link(fn_in, fn_out)
	elif transfer_method == "copy":
		copyfile(fn_in, fn_out)
	else:
		print("ERROR: transfer method {} not supported!".format(transfer_method))
		sys.exit(1)


def reduce_frames(src, dst, keep_factor, file_ext, transfer_method, dryrun):
	dir_with_pattern = os.path.join(src, "*{}".format(file_ext))
	files_in = sorted(glob.glob(dir_with_pattern))
	if not files_in:
		print("ERROR: no files found using wildcard path {}".format(dir_with_pattern))
		sys.exit(1)
	it = 0
	for f in files_in:
		if it % keep_factor == 0:
			file_out = os.path.join(dst, os.path.basename(f))
			print("'{0}' {1} to {2} ...".format(transfer_method, f, file_out))
			if not dryrun:
				do_transfer(f, file_out, transfer_method)
		it += 1
	if dryrun:
		print("\n--dryrun used; no files transferred.\n")


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Decimate files (sorted by name) using a keep factor")

	req_named = parser.add_argument_group("Required named arguments")

	req_named.add_argument("src", help="Directory containing input files", type=str)
	req_named.add_argument("dst", help="Directory where output files will be written", type=str)
	req_named.add_argument("-k", "--keep-factor",
						   help="Frequency of images to keep (e.g., '4' keeps every fourth image) (default={})".format(DEFAULT_KEEP_FACTOR),
						   type=int, default=DEFAULT_KEEP_FACTOR)
	req_named.add_argument("-f", "--file-ext",
						   help="File extension to filter (default='{}')".format(DEFAULT_FILE_EXTENSION),
						   default=DEFAULT_FILE_EXTENSION, type=str)
	req_named.add_argument("-tm", "--transfer-method",
						   help="how to transfer kept files (default='{}')".format(DEFAULT_TRANSFER_METHOD),
						   default=DEFAULT_TRANSFER_METHOD, choices=TRANSFER_METHODS, type=str)

	parser.add_argument("--dryrun", help="Run script, but do not execute actions", action="store_true", required=False)

	arguments = parser.parse_args()

	reduce_frames(**vars(arguments))
