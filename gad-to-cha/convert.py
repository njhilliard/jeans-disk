#!/usr/bin/python

# Need to add some cleanup for unnecessary lines (mainly comments and
#  whitespace)

import sys
from astropy import units as u
from param_dict import g2c_name_dict

class convert_g2c():
    """Class to provide conversion from gadget to
        changa parameter files"""
    def __init__(self):
        self.comments = []
        self.gad_name = []
        self.comm_idx = []
        self.prms_idx = []
        self.empt_idx = []
        self.inlines  = []
        self.outlines = []
        self.prm_dict = {}

    def read(self, f_name):
        """Read gadget parameter file"""
        with open(f_name, 'r') as f:
            self.inlines = f.readlines()

    def parse(self):
        """Parse the gadget parameter file"""
        for i,line in enumerate(self.inlines):
            line.rstrip('\n')
            #Remove comments
            if '%' in list(line)[0]:
                #changa prms comments begin with pound
                self.comments.append('#' + line)
                self.comm_idx.append(i) #store comment indices
            #elif '%' in list(line):   #remove endline comments
                #lines[i] = line.split('%',1)[0]
            # remove empty lines or lines beginning with space
            elif ' ' in list(line)[0] or len(line)==1:
                self.empt_idx.append(i)
            else:
                linesplit = line.split()
                self.gad_name.append(linesplit[0])
                self.prm_dict[linesplit[0]] = linesplit[1]
                self.prms_idx.append(i)
        return self.prm_dict

    def build_dict(self, f_name, d_name):
        """Build a conversion dictionary from a gadget params file.
           Currently untested."""
        with open(dict_name, 'w') as f:
            #f.write('# gadget.param : changa.param\n')
            f.write(d_name + ' = {\\\n')
            for prm_name in self.gdt_name:
                f.write('    {:40}{}'.format(\
                        '\'' + prm_name + '\'',':\'\',\\'))
                f.write('\n')
            f.write('        }')

    def build_outlines(self, g2c_name_dict):
        """Write output changa parameter file"""
        comm_ct = 0
        prms_ct = 0
        for i in range(len(self.inlines)):
            if i in self.prms_idx:
                if g2c_name_dict[self.gad_name[prms_ct]] == '':
                    pass
                else:
                    hold2 = [g2c_name_dict[self.gad_name[prms_ct]],\
                             self.prm_dict[self.gad_name[prms_ct]]]
                    self.outlines.append(hold2)
                prms_ct += 1
            # Add comment lines
            elif i in self.comm_idx:
                #self.outlines.append(self.comments[comm_ct])
                comm_ct += 1
            elif i in self.empt_idx: # Add blank lines
                #self.outlines.append('') 
                pass
            # Add nonempty dict matches and converted vals
            else: # Tell when something doesn't work
                print('Error: unknown line passed to build_outlines')
                self.outlines.append('badline')

        # remove lines after last parameter 
        # (may be better to do this earlier)
        for i,line in enumerate(reversed(self.outlines)):
            if type(line) == list:
                last_prm_idx = len(self.outlines) - i
                break
            else:
                pass
        self.outlines = self.outlines[:last_prm_idx]
        
        return self.outlines

    def convert_vals(self):
        """Convert parameter values"""
        # wall runtime limit seconds to minutes
        self.prm_dict['TimeLimitCPU'] =\
                str(int(self.prm_dict['TimeLimitCPU'])/ 60)
        # timesteps
        #####self.prm_dict['TimeBetSnapshot'] =\
        # gadget courant factor is half of normal
        self.prm_dict['CourantFac'] =\
                str(2 * float(self.prm_dict['CourantFac']))
        # convert cm to kpc
        unitlength = float(self.prm_dict['UnitLength_in_cm']) * u.cm
        self.prm_dict['UnitLength_in_cm'] =\
                str(float(unitlength.to(u.kpc) / u.kpc))
        # convert g to solar masses
        unitmass = float(self.prm_dict['UnitMass_in_g']) * u.g
        self.prm_dict['UnitMass_in_g'] =\
                str(float(unitmass.to(u.solMass) / u.solMass))

        return self.prm_dict

    def write(self, f_name):
        """Write output changa parameter file"""
        with open(f_name, 'w') as f:
            for line in self.outlines:
                if len(line)==2:
                    f.write('{:20}'.format(line[0])) # name
                    f.write('    {}'.format(line[1])) # val
                    f.write('\n')
                else:
                    f.write(line)
                    f.write('\n')


if __name__ == "__main__":
    fopen = 'gadget.params'
    fwrite = 'changa.params'
    convert = convert_g2c()
    convert.read(fopen)
    #print(convert.parse())
    #print(convert.build_outlines(g2c_name_dict))
    convert.parse()
    #print(convert.convert_vals())
    convert.convert_vals()
    convert.build_outlines(g2c_name_dict)
    convert.write(fwrite)

