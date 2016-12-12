import h5py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input_file', metavar='input', help='Gadget3 input file')
parser.add_argument('--nogas', action='store_true')
parser.add_argument('--sfr', action='store_true')
args = parser.parse_args()

def set_sfr_params(f, val):
    f['Header'].attrs.modify('Flag_Cooling', val)
    f['Header'].attrs.modify('Flag_Feedback', val)
    f['Header'].attrs.modify('Flag_Sfr', val)
    f['Header'].attrs.modify('Flag_StellarAge', val)
        
with h5py.File(args.input_file, "r+") as f:
    f['Header'].attrs.modify('Flag_Metals', 0)

    set_sfr_params(f, int(args.sfr))
   
    if (args.nogas):
        numpart = f['Header'].attrs['NumPart_Total']
        numpart[0] = 0
        f['Header'].attrs.modify('NumPart_Total', numpart)
        numpart = f['Header'].attrs['NumPart_ThisFile']
        numpart[0] = 0
        f['Header'].attrs.modify('NumPart_ThisFile', numpart)
        masses = f['Header'].attrs['MassTable']
        masses[0] = 0
        f['Header'].attrs.modify('MassTable', masses)    
        del f['PartType0']
