#!/usr/bin/python
import sys
import os
import re
import argparse
from shutil import copyfile

#PREDICATE_TO_CHANGE = "(\()at( C[0-9]{1,2} L[0-9]{1,2}\))"
#CHANGE_TO = "at1"

PREDICATE_TO_CHANGE = "(\()available( C[0-9]{1,2}\))"
CHANGE_TO = "available1"

PRED_REGEX = re.compile(PREDICATE_TO_CHANGE)

def change_propositions(buffer, new_file):
	for line in buffer:
		if PRED_REGEX.search(line):
			new_line = PRED_REGEX.sub(f"\\1{CHANGE_TO}\\2",line)
			new_file.write(new_line)
		else:
			new_file.write(line)

def bufferFile(file):
	fileBuffer = []
	for line in file:
		fileBuffer.append(line)
	return fileBuffer
			
def main(args):
	parser = argparse.ArgumentParser(description='A script for changing a proposition name in PDDL problem files.')
	parser.add_argument('path',
						metavar='/path/to/pddl/files',
						type=str,
						help='the location of the pddl files to modify')
	parser.add_argument('new_path',
						metavar='/path/to/store/updated/files',
						type=str,
						help='the location to write new pddl files')
	parser.add_argument('--dont-copy-domain',
						type=bool,
						default=False,
						help='Whether the domain files (if found) should be copied to the new location.')

	args = parser.parse_args()
	
	if (not os.path.isdir(args.path)):
		print(f"Error: The path to the PDDL files to modify is not a valid path ({args.path}).")
		sys.exit(-1)

	if (not os.path.isdir(args.new_path)):
		print(f"Error: The path to save modified PDDL files is not valid ({args.new_path}).")
		sys.exit(-2)

	for root, dirs, files in os.walk(args.path):
		for file in files:
			if "DOMAIN" in file:
				if not args.dont_copy_domain:
					copyfile(os.path.join(root, file), os.path.join(args.new_path, file))
				continue

			f = open(os.path.join(root, file), 'r')
			buffer = bufferFile(f)
			f.close()

			w = open(os.path.join(args.new_path, file), 'w')
			change_propositions(buffer, w)
			w.close()
		break


#Run Main Function
if __name__ == "__main__":
	main(sys.argv)
