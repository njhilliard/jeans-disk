#!/usr/bin/python

import gadget
import ChaNGa
import tipsy
import argparse
import os

def get_output_file(file_name):
    input_dir, input_name = os.path.split(file_name)
    input_file_basename, _ = os.path.splitext(input_name)
    
    if input_dir != '':
        input_dir += '/'
    
    return input_dir + input_file_basename

parser = argparse.ArgumentParser(description='Convert GADGET2 files to ChaNGa files')
parser.add_argument('gadget_file', metavar='GADGET', help='GADGET2 HDF5 file to convert')
parser.add_argument('param_file', metavar='Parameter', help='GADGET2 parameter file to convert')
parser.add_argument('--convert-bh', action='store_true', help='Treat boundary particles as black holes')
parser.add_argument('--preserve-boundary-softening', action='store_true', help='Preserve softening lengths for boundary particles')
parser.add_argument('--no-param-list', action='store_true', help='Do not store a complete list ChaNGa parameters in "param_file"')
args = parser.parse_args()

output_file = get_output_file(args.gadget_file)

gadget_file = gadget.File(args.gadget_file)
gadget_params = gadget.Parameter_file(args.param_file)
changa_params, mass_factor = ChaNGa.convert_parameter_file(gadget_params)

tipsy_file = tipsy.gadget_converter(gadget_params, gadget_file, mass_factor, args.convert_bh, args.preserve_boundary_softening)
 
changa_params['bDoGas'] = int(tipsy_file.gas is not None)

#Output the parameter file
with open(output_file + '.ChaNGa.params', 'w') as f:
     for k in sorted(changa_params):
         f.write('{0:20s}{1:s}\n'.format(k, str(changa_params[k])))

if not args.no_param_list:
    with open(output_file + '.ChaNGa.params', 'a') as f:
        f.write('\n# Complete parameter list below\n')
        for k in sorted(ChaNGa.all_parameters):
            f.write('#{0:30s}{1:s}\n'.format(k, ChaNGa.all_parameters[k]))
             
tipsy_file.save(output_file + '.tipsy')
