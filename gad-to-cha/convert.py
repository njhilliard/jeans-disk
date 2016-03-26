import sys
from param_dict import g2c_dict

class convert_g2c():
    """Class to provide conversion from gadget to
        changa parameter files"""
    def __init__(self):
        self.comments = []
        self.comments = []
        self.gad_name = []
        self.gad_vals = []
        self.comm_idx = []
        self.prms_idx = []
        self.empt_idx = []
        self.lines    = []

    def read(self, f_name):
        """Read gadget parameter file"""
        with open(f_name, 'r') as f:
            self.lines = f.readlines()

    def parse(self):
        """Parse the gadget parameter file"""
        for i,line in enumerate(self.lines):
            #Remove comments
            if '%' in list(line)[0]:
                self.comments.append('#' + line) #store comment-only lines
                self.comm_idx.append(i) #store comment indices to remove?
            #elif '%' in list(line):   #remove endline comments
                #lines[i] = line.split('%',1)[0]
            # remove empty lines or lines beginning with space
            elif ' ' in list(line)[0] or len(line)==1:
                self.empt_idx.append(i)
            else:
                self.gad_name.append(line.split()[0])
                self.gad_vals.append(line.split()[1])
                self.prms_idx.append(i)

    def build_dict(self, f_name, d_name):
        """Build a conversion dictionary from a gadget params file"""
        with open(dict_name, 'w') as f:
            f.write('# gadget.param : changa.param\n')
            f.write(d_name + ' = {\\\n')
            for prm_name in self.gdt_name:
                f.write('    {:40}{}'.format(\
                        '\'' + prm_name + '\'',':\'\',\\'))
                f.write('\n')
            f.write('        }')

    def write(self, f_name, g2c_dict):
        """Write output changa parameter file"""
        with open(f_name, 'w') as f:
            comm_ct = 0
            prms_ct = 0
            for i in range(len(self.lines)):
                if i in self.comm_idx: # Write comments
                    f.write(self.comments[comm_ct])
                    f.write('\n')
                    comm_ct += 1
                elif i in self.empt_idx: # Write blank lines
                    f.write('') 
                    f.write('\n')
                # Write nonempty dict matches and vals
                elif i in self.prms_idx:
                    if g2c_dict[self.gad_name[prms_ct]] == '':
                        pass
                    else:
                        f.write('{:25}'.format(\
                                        g2c_dict[self.gad_name[prms_ct]]))
                        f.write('   {}'.format(self.gad_vals[prms_ct]))
                        f.write('\n')
                    prms_ct += 1
                else: # Tell when something doesn't work
                    print('badline written to' + fwrite)
                    f.write('badline')
                    f.write('\n')


if __name__ == "__main__":

    fopen = 'gadget.params'
    fwrite = 'changa.params'
    convert = convert_g2c()
    convert.read(fopen)
    convert.parse()
    convert.write(fwrite, g2c_dict)

