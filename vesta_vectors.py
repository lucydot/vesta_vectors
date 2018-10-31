#! /usr/bin/env python3
"""
Create a vesta file which contains vectors 
connecting atomic positions before and after an ionic relaxation.
For constant cell volume and shape.
"""
import numpy as np
import argparse
import re

def read_in(settings):

    combined_positions = []
    combined_data = []

    for filename in [settings.filenames[0], settings.filenames[1]]:
        data = open(filename,'r').read()
        combined_data.append(data)
        
        struct_match=re.search(r"STRUC.*THERI",data,flags=re.S)[0]
        pos_match=re.findall(r"\d+\D+\s+\D+\d+\s+\d+\.\d+\s+(.*?)\s+\d+\D+\s+\d+",struct_match)

        if pos_match:
            positions = [[float(y) for y in x.split()] for x in pos_match]
        else:
            raise ValueError("Invalid file format (I am only able to parse Vesta files)")


        combined_positions.append(positions)
    
    data = {"initial_data": combined_data[0],
            "final_data": combined_data[1],
            "initial_positions": combined_positions[0], # positions in fractional coordinates
            "final_positions": combined_positions[1], # positions in fractional coordinates
            }


    struct_match=re.findall(r"CELLP\n\s+(\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+)",combined_data[0])[0]
    data["cell_lengths"] = [float(x) for x in struct_match.split()] # cell lengths in angstrong

    return data

def delete_atoms(data):

    for atom_id in sorted(settings.atoms_removed, reverse=True):
        del data["initial_positions"][atom_id-1]   # remove initial atoms which are not found in final structure
        
    for atom_id in sorted(settings.atoms_inserted, reverse=True):
        del data["final_positions"][atom_id-1]     # remove final atoms which are not in initial structure

    assert len(data["initial_positions"])==len(data["final_positions"]),"Unequal number of atoms before and after relaxation"
    return data 

def calc_displacement(data):

    # displacement in fractional coordinates
    displacement_frac = np.subtract(data["final_positions"],data["initial_positions"])

    # We cannot know which route the atom took, but we assume that if the vector is over half a lattice length,
    # then the atom moved into the neighbouring cell.
    displacement_frac_adjusted = [[-(1-x) if (x>0.5) else x for x in line] for line in displacement_frac]

    # Final vectors are in angstrong
    data["vectors"] = np.multiply(displacement_frac_adjusted,data["cell_lengths"])
    return data

def calc_bounds(data):

    # the output vesta structure is centred around this atom in the initial structure
    centre_position = data["initial_positions"][settings.centre_atom[0]-1]
    data["min_bound"] = [x-0.5 for x in centre_position]
    data["max_bound"] = [x+0.5 for x in centre_position]
    return data

def print_to_file(data,settings):

    VECTR_str=r"\1 "
    for i,atom in enumerate(data["vectors"]):
        if np.linalg.norm(atom) > settings.cutoff[0]: # only create vector if more than cutoff modulus
            VECTR_str += "{0} {1} {2} {3} 0\n {0} 0 0 0 0\n 0 0 0 0 0\n".format(i+1,atom[0],atom[1],atom[2]) # create vectors
    
    VECTT_str=r"\1 "
    i=1
    for atom in data["vectors"]:
        if np.linalg.norm(atom) > settings.cutoff[0]: # only create vector if more than cutoff modulus
            VECTT_str += "{0} {1} {2} {3} {4} 0\n".format(i,settings.radius[0], settings.colour[0], settings.colour[1], settings.colour[2]) # set vector radius and colour
            i+=1

    ATOMT_match = re.search(r"ATOMT.*SCENE",data["initial_data"],flags=re.S)[0]  
    ATOMT_corrected = re.sub(r'([a-zA-Z]+\s+)\d+\.\d+',r"\1 0.0001",ATOMT_match)  # this make all atoms reaaaalllly small

    SITET_match = re.search(r"SITET.*VECTR",data["initial_data"],flags=re.S)[0]
    SITET_corrected = re.sub(r'([a-zA-Z]+\d+\s+)\d+\.\d+',r"\1 0.0001",SITET_match) # this make all atoms reaaaalllly small

    BONDP_match = re.search(r"BONDP.*POLYP",data["initial_data"],flags=re.S)[0]   
    BONDP_corrected = re.sub(r'(\d+\s+\d+\s+)\d+\.\d+',r"\1 0.0001",BONDP_match)  # this makes all bonds reaaaalllly small

    SBOND_match = re.search(r"SBOND.*SITET",data["initial_data"],flags=re.S)[0]
    SBOND_corrected = re.sub(r'(\s+\d\s+\d\s+\d\s+\d\s+\d\s+)\d+\.\d+',r"\1 0.0001",SBOND_match) # make all bonds reaaaalllly small

    # substitute the above strings into the output data string
    data["output_data"] = re.sub(r'(VECTR\n)',VECTR_str,data["final_data"])   
    data["output_data"] = re.sub(r'(VECTT\n)',VECTT_str,data["output_data"])
    data["output_data"] = re.sub(r'(ATOMT.*SCENE)',ATOMT_corrected,data["output_data"],flags=re.S)
    data["output_data"] = re.sub(r'(BONDP.*POLYP)',BONDP_corrected,data["output_data"],flags=re.S)
    data["output_data"] = re.sub(r'(SBOND.*SITET)',SBOND_corrected,data["output_data"],flags=re.S)
    data["output_data"] = re.sub(r'(SITET.*VECTR)',SITET_corrected,data["output_data"],flags=re.S)
    data["output_data"] = re.sub(r'(VECTS).*(FORMP)',r"\1 {} \n \2".format(settings.scale_factor[0]),data["output_data"],flags=re.S) # set vector scale factor
    if settings.centre_atom: # centre the output structure around a particular atom
        data["output_data"] = re.sub(r'(BOUND).*(SBOND)',r"\1 \n {0} {1} {2} {3} {4} {5} \n 0 0 0 0 0 \n \2".format(data["min_bound"][0],data["max_bound"][0],data["min_bound"][1],data["max_bound"][1],data["min_bound"][2],data["max_bound"][2]),data["output_data"],flags=re.S)

    file_out = open('vectors.vesta','w+')
    file_out.write(data["output_data"])
    file_out.close()

def parse_args():

    parser = argparse.ArgumentParser(description="""Create a vesta file containing
    vectors that connect atomic positions before and after an ionic 
    relaxation""")
    parser.add_argument('--filenames','-f',type=str, nargs=2, required=False,
        default=["initial.vesta","final.vesta"], help="name of initial and final vesta files"
        )
    parser.add_argument('--colour','-c',type=int, nargs=3,required=False,
        default=[255,0,0], help="vector colour (in RGB)")
    parser.add_argument('--radius','-r',type=float, nargs=1, required=False,
        default=[0.5], help="vector radius (in angstrom")
    parser.add_argument('--atoms_removed','-ar',type=int,nargs='+',required=False,
        default=[], help='index position of atoms in initial structure which have been removed in final structure (indexing from one)')
    parser.add_argument('--atoms_inserted','-ai',type=int,nargs='+',required=False,
        default=[], help='index position of atoms which have been inserted into the final structure (indexing from one)')
    parser.add_argument('--cutoff', '-x', type=float, nargs=1, required=False,
        default=[0.1], help="vectors with a modulus below this value will not be displayed (in angstrom)")
    parser.add_argument('--scale_factor', '-sf', type=float, nargs=1, required=False,
        default=[1.0], help='scale all vector moduli by this fixed amount')
    parser.add_argument('--centre_atom', '-ca', type=int, nargs=1, required=False,
        default=None, help='the output vesta structure is centred around an atom in the initial structure, specified by this index position (indexing from one)')
    
    args = parser.parse_args()

    return args

if __name__=="__main__":

    print ("""Welcome to the vesta_vectors. \nType `vesta_vectors -h' to see the command line options.
           """)
    settings = parse_args()
    print ("Reading in data...")
    data = read_in(settings)
    print ("Calculating...")
    if settings.centre_atom:
        data = calc_bounds(data)
    data = delete_atoms(data)
    data = calc_displacement(data)

    print ("Printing to file")
    print_to_file(data,settings)
    print ("All done.")
