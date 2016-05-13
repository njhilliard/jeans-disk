#!/usr/bin/python

import sys
import numpy as np
import math
from collections import OrderedDict
from astropy import units as u
from astropy.constants import G
from param_dict import g2c_name_dict

class convert_g2c():
    """Class to provide conversion from gadget to
        changa parameter files"""
    def __init__(self):
        self.inlines  = []
        self.outlines = []
        self.gad_dict = OrderedDict()
        self.cha_dict = OrderedDict()

    def read(self, f_name):
        """Read gadget parameter file"""
        with open(f_name, 'r') as f:
            self.inlines = f.readlines()

    def parse(self, g2c_name_dict):
        """Parse the gadget parameter file"""
        for line in self.inlines:
            line.rstrip('\n')
            if not '%' in list(line)[0] and not ' ' in list(line)[0]\
                                        and not len(line)==1:
                linesplit = line.split()
                self.gad_dict[linesplit[0]] = linesplit[1]
        for key in g2c_name_dict:
            if g2c_name_dict[key] != '':
                self.cha_dict[g2c_name_dict[key]] = self.gad_dict[key]

        return self.gad_dict, self.cha_dict

    def build_outlines(self):
        """Write output changa parameter file"""
        for key in self.cha_dict:
            self.outlines.append([key, self.cha_dict[key]])
        
        return self.outlines

    def convert_vals(self):
        """Convert parameter values"""
        # mash together gadget directory output and file prefix
        self.cha_dict['achOutFile'] =\
                self.gad_dict['OutputDir'] + '/'\
                + self.gad_dict['SnapshotFileBase']
        # wall runtime limit seconds to minutes
        self.cha_dict['iWallRunTime'] =\
                str(int(self.gad_dict['TimeLimitCPU'])/ 60)
        # simulation start step
        if self.gad_dict['TimeBegin'] != 0:
            step_floor = math.floor(float(self.gad_dict['TimeBegin'])/\
                                    float(self.cha_dict['dDelta']))
            self.cha_dict['iStartStep'] = str(step_floor)
        else:
            self.cha_dict['iStartStep'] = '0'
        # number of simulation steps
        self.cha_dict['nSteps'] = str(math.ceil(\
                (float(self.gad_dict['TimeMax'])\
                 - float(self.gad_dict['TimeBegin']))\
                / float(self.cha_dict['dDelta'])))
        # output writing interval
        self.cha_dict['iOutInterval'] = str(math.ceil(\
                float(self.gad_dict['TimeBetSnapshot'])\
                / float(self.cha_dict['dDelta'])))
        # output to log file interval
        self.cha_dict['iLogInterval'] = str(math.floor(\
                float(self.gad_dict['TimeBetStatistics'])\
                / float(self.cha_dict['dDelta'])))
        # factor difference for Eta parameter
        self.cha_dict['dEta'] = str(math.sqrt(\
                2 * float(self.gad_dict['ErrTolIntAccuracy'])))
        # gadget courant factor is half of normal
        self.cha_dict['dEtaCourant'] =\
                str(2 * float(self.gad_dict['CourantFac']))
        # convert cm to kpc
        unitlength = float(self.gad_dict['UnitLength_in_cm']) * u.cm
        dKpcUnit = float(unitlength.to(u.kpc) / u.kpc)
        self.cha_dict['dKpcUnit'] = str(dKpcUnit)
        # convert g to solar masses
        unitmass = float(self.gad_dict['UnitMass_in_g']) * u.g
        unitvelocity = float(self.gad_dict['UnitVelocity_in_cm_per_s'])\
                       * u.cm / u.s
        dMsolUnit =float(  ( ( ((dKpcUnit * u.kpc).to(u.m))**3\
                              / (unitlength / unitvelocity)**2\
                             ) / G\
                           ).to(u.Msun) / u.Msun\
                        )
        mass_convert_factor = float(float(dMsolUnit) * u.Msun\
                                    / unitmass.to(u.Msun))
        self.cha_dict['dMsolUnit'] = str(dMsolUnit)
        print('Warning: mass of simulation has changed due to changa G=1')

        return self.cha_dict, mass_convert_factor

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
    fwrite = 'changa.param'
    convert = convert_g2c()
    convert.read(fopen)
    convert.parse(g2c_name_dict)
    print(convert.convert_vals()[1])
    convert.build_outlines()
    convert.write(fwrite)

