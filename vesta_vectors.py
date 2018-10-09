#! /usr/bin/env python3
"""
Create a vesta file which contains vectors 
connecting atomic positions before and after an ionic relaxation.
For constant cell volume and shape.
It does not know which route the atom took,
but assumes that if over half a lattice length
that is moved into another neighbouring cell.
"""

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
	        "initial_positions": combined_positions[0],
	        "final_positions": combined_positions[1],
	        }

	for atom_id in sorted(settings.atoms_removed, reverse=True):
	    del data["initial_positions"][atom_id-1]
	    
	for atom_id in sorted(settings.atoms_inserted, reverse=True):
	    del data["final_positions"][atom_id-1]

	assert len(combined_positions[0])==len(combined_positions[1]),"Unequal number of atoms before and after relaxation"

	struct_match=re.findall(r"CELLP\n\s+(\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+)",combined_data[0])[0]
	data["cell_lengths"] = [float(x) for x in struct_match.split()]

    return data

def calc_displacement(data):

	displacement_frac = np.subtract(combined_positions[1],combined_positions[0])
	displacement_frac_adjusted = [[-(1-x) if (x>0.5) else x for x in line] for line in displacement_frac]
	displacement_angs = np.multiply(displacement_frac_adjusted,data["cell_lengths"])
 	return displacement_angs
 	# what about non-cubic cells? should be fine ---> important that cell shape does not change
 	# how to handle displacement when atoms move into neighbouring cells?

def print_to_file(data,settings):


def parse_args():

	parser = argparse.ArgumentParser(description="""Create a vesta file which
	contains vectors connecting atomic positions before and after an ionic 
	relaxation""")
	parser.add_argument('--filenames','-f',type=str, nargs=2, required=False,
		default=["POSCAR.vesta","CONTCAR.vesta"]
		)
	parser.add_argument('--colour','-c',type=int, nargs=3,required=False,
		default=[255,0,0])
	parser.add_argument('--id','-i',type=int, nargs='+',required=False,
		default=[])
	parser.add_argument('--radius','-r',type=float, nargs=1, required=False,
		default=1.0)
	parser.add_argument('--atoms_removed','-ar',type=int,nargs='+',required=False,
		default=[])
	parser.add_argument('--atoms_inserted','-ai',type=int,nargs='+',required=False,
		default=[])
	parser.add_argument('--cutoff', '-x', type=float, nargs=1, required=False,
		default = 0.05)
	args = parser.parse_args()

	return args

if __name__=="__main__":

     print ("""Welcome to the vesta_vectors.
     	   Type `vesta_vectors -h' to see the command line options
    	   """)
 	settings = parse_args()
 	print ("Reading in data...")
 	data = read_in(settings)
 	print ("Calculating the displacements")
 	data["vectors"] = calc_displacement(data)
 	print ("Printing to file")
	print_to_file(data,settings)
	print ("All done.")
