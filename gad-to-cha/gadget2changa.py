#!/usr/bin/python

import gadget
import ChaNGa
import argparse
import os

def get_output_file(file_name):
    input_dir, input_name = os.path.split(file_name)
    input_file_basename, _ = os.path.splitext(input_name)
    
    if input_dir != '':
        input_dir += '/'
    
    return input_dir + input_file_basename

parser = argparse.ArgumentParser(description='Convert GADGET2 files to ChaNGa files')
parser.add_argument('gadget_file', metavar='GADGET', nargs=1, help='GADGET2 HDF5 file to convert')
parser.add_argument('param_file', metavar='Parameter', nargs=1, help='GADGET2 parameter file to convert')
parser.add_argument('--convert_bh', action='store_true', help='Treat boundary particles as black holes')
args = parser.parse_args()

output_file = get_output_file(args.gadget_file) + '.tipsy'
gadget_file = gadget.File(args.gadget_file)
gadget_params = gadget.Parameter_file(args.param_file)
changa_params, mass_factor = ChaNGa.convert_parameter_file(gadget_params)
 
# Output the parameter file
with open(output_parameter_filename, 'w') as f:
     for k,v in changa_params.items():
         f.write('{0:20s}'.format(k))
         f.write('{0:10s}'.format(v))
 
tipsy_file = tipsy.File()
tipsy_file.convert(gadget_params, gadget_file, args.convert_bh)
tipsy_file.save(output_file)