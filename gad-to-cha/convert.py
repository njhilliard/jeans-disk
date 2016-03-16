import sys
from param_dict import gad_to_cha_dict

filename = 'gadget.params'
#filename = sys.argv[1]

if __name__ == "__main__":

    comments = []
    comm_idx = []
    gad_prms = []

    with open(filename, 'r') as f:
        lines = f.readlines()

    for i,line in enumerate(lines):

        #Remove comments
        if '%' in list(line)[0]:
            comments.append(line) #store comment-only lines
            comm_idx.append(i)    #store comment indices to remove?
        #elif '%' in list(line):   #remove endline comments
            #lines[i] = line.split('%',1)[0]
        # remove empty lines or lines beginning with space
        elif ' ' in list(line)[0] or len(line)==1:
            pass
        else:
            gad_prms.append(line.split()[0])

    #print gadget parameters fromatted
    #for prm_name in gdt_prms:
        #print('    {:40}{}'.format('\'' + prm_name + '\'',':\'\',\\'))

