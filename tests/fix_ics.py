import h5py
from shutil import copyfile
import sys

if len(sys.argv) != 2:
    print("Usage: {0:s} input_file".format(sys.argv[0]))
    exit()

input_file = sys.argv[1]
temp_file = input_file + '.tmp'

copyfile(input_file, temp_file)

with h5py.File(temp_file, "r+") as f:
    del f['PartType0']
    f['Header'].attrs.modify('Flag_Cooling', 0)
    f['Header'].attrs.modify('Flag_Feedback', 0)
    f['Header'].attrs.modify('Flag_Metals', 0)
    f['Header'].attrs.modify('Flag_Sfr', 0)
    f['Header'].attrs.modify('Flag_StellarAge', 0)
