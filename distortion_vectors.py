#! /usr/bin/env python3
"""
Create a vesta file which contains vectors 
connecting atomic positions before and after an ionic relaxation
"""

import argparse
import re

def read_in(settings):

    combined_positions = []
    combined_data = []

    for filename in [settings.initial_filename, settings.final_filename]:
    	data = open(filename,'r').read()
    	combined_data.append(data)

		match = re.search("", data)
    	if match:
    		positions =  float(match.groups()[0])
   	 	else:
    		error("Invalid file format (I am only able to parse Vesta files)")

    	positions = [[]]
    	combined_positions.append(positions)

    assert (len(combined_positions[0])==len(combined_positions[1]),"""different number of
    	atoms in initial and final files""")

    data = {initial_data: combined_data[0];
    		final_data: combined_data[1];
    		initial_positions: combined_positions[0]; 
    		final_positions: combined_positions[1]}

    return data

# def calc_displacement(data):

# 	data["displacement"] = 

# def print_to_file(data,settings):


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
		default=[0])
	parser.add_argument('--radius','-r',type=float, nargs=1, required=False,
		default=1.0)
	args = parser.parse_args()

	return args

if __name__=="__main__":

#     print ("""Welcome to the distortion_vectors script.
#     	   Type `distortion_vectors -h' to see command line options
#     	   """)
 	settings = parse_args()
# 	print ("Reading in data...")
# 	data = read_in(settings)
# 	print ("Calculating the displacements")
# 	data["displacement"] = calc_displacement(data)
# 	print ("Printing to file")
# 	print_to_file(data,settings)
# 	print ("All done.")
