import os
import sys
import glob 
from shutil import copyfile


skip_value = 2  # 1: do not skip; 2: pick every other frame; 3: every third; etc.
fn_in = r"D:\plant_timelapse_2020\renumber"
fn_out = r"D:\plant_timelapse_2020\renumber_oddonly"

files_in = sorted(glob.glob(os.path.join(fn_in, "*.jpg")))
if not files_in:
	print("no files found")
	sys.exit(1)
it = 0
for f in files_in:
	if it % skip_value == 0:
		file_out = os.path.join(fn_out, os.path.basename(f))
		print("copying {0} to {1} ...".format(f, file_out))
		copyfile(f, file_out)
	it += 1