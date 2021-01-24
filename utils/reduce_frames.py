import os
import sys
import glob
import time
import shutil


DEFAULT_FILE_EXTENSION = ".jpg"
DEFAULT_KEEP_FACTOR = 2
TRANSFER_METHODS = ["link", "copy"]
DEFAULT_TRANSFER_METHOD = "link"


def do_transfer(fn_in, fn_out, transfer_method, overwrite=False):
	out_exists = os.path.isfile(fn_out)
	if transfer_method == "link":
		if out_exists and overwrite:
			os.remove(fn_out)
		os.link(fn_in, fn_out)

	elif transfer_method == "copy":
		if out_exists and overwrite:
			os.remove(fn_out)
		shutil.copyfile(fn_in, fn_out)

	else:
		print("ERROR: transfer method {} not supported!".format(transfer_method))
		sys.exit(1)


def reduce_frames(src, dst, keep_factor, file_ext, transfer_method, no_renumber=False, overwrite=False, dryrun=False):
	print("---------------------------------------------------------")
	print("Inputs:")
	print("  src: {}".format(src))
	print("  dst: {}".format(dst))
	print("  keep_factor: {}".format(keep_factor))
	print("  file_ext: {}".format(file_ext))
	print("  transfer_method: {}".format(transfer_method))
	print("  no_renumber: {}".format(no_renumber))
	print("  overwrite: {}".format(overwrite))
	print("  dryrun: {}".format(dryrun))
	print("---------------------------------------------------------\n")

	dir_with_pattern = os.path.join(src, "*{}".format(file_ext))
	files_in = sorted(glob.glob(dir_with_pattern))
	if not files_in:
		print("ERROR: no files found using wildcard path {}".format(dir_with_pattern))
		sys.exit(1)
	it = 0
	renumber_ct = 0
	# determine number of digits
	num_dig = len(str(len(files_in)))
	if not no_renumber:
		print("WARNING: files will be renamed sequentially, using {} number places".format(num_dig))
		print("  sleeping 15 seconds before continuing...")
		time.sleep(15)
	for f in files_in:
		if it % keep_factor == 0:
			if no_renumber:
				file_out = os.path.join(dst, os.path.basename(f))
			else:
				# override entire filename with sequential value
				renumber_ct += 1
				fin_fix = str(renumber_ct).zfill(num_dig)
				file_out = os.path.join(dst, fin_fix + file_ext)
			print("'{0}' {1} to {2} ...".format(transfer_method, f, file_out))
			if not dryrun:
				do_transfer(f, file_out, transfer_method, overwrite=overwrite)
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
						   help="Frequency of images to keep (e.g., '4' keeps every fourth image) (default={})"
						   .format(DEFAULT_KEEP_FACTOR),
						   type=int, default=DEFAULT_KEEP_FACTOR)
	req_named.add_argument("-f", "--file-ext",
						   help="File extension to filter (default='{}')".format(DEFAULT_FILE_EXTENSION),
						   default=DEFAULT_FILE_EXTENSION, type=str)
	req_named.add_argument("-tm", "--transfer-method",
						   help="How to transfer kept files (default='{}')".format(DEFAULT_TRANSFER_METHOD),
						   default=DEFAULT_TRANSFER_METHOD, choices=TRANSFER_METHODS, type=str)

	parser.add_argument("--no-renumber", help="Do NOT rename transferred files to sequential numbering",
						action="store_true")
	parser.add_argument("--overwrite", help="Overwrite existing destination file(s)", action="store_true")
	parser.add_argument("--dryrun", help="Run script, but do not execute actions", action="store_true", required=False)

	arguments = parser.parse_args()

	reduce_frames(**vars(arguments))
