#! /usr/bin/python
#Author: Tony Allard
#Date: 07 Oct 2016
#Description: A Python script for removing TILs from problems generated with the MMCR generators

#Usage: MMCR-Tightness-Geom-4-3-1.py /Path/To/Problems/With/TILS /Path/To/Save/Problems/Without

import sys
import os
import re
import MMCRProbGen

TIL_DELIMITER = re.compile("[\s]*at[\s]*\d+(\.\d*)?|\.\d+")

def printUsage(name):
	print "Multi-Modal Cargo Routing (MMCR) Problem TIL Remover"
	print "By releasing this code we imply no warranty as to its reliability and its use is entirely at your own risk.\n"
	print "Usage " + name + " InputPath OutputPath\n"
	print "\tExample: " + name + " /Path/To/Problems/With/TILS /Path/To/Save/Problems/Without"

def removeTILs(f, filename, outputPath):
	outFile = os.path.join(outputPath, filename)
	output = open(outFile, 'w')
	for line in f:
		if not re.search(TIL_DELIMITER, line):
			output.write(line)
			

def main(name, args):
	argName = ("Input Path", "Output Path")
	params = dict()
	try:
		params = MMCRProbGen.parseArgs(args, argName)
	except:
		printUsage(name)
		sys.exit(1)

	inputPath = params[argName[0]]
	outputPath = params[argName[1]]
	
	for filename in os.listdir(inputPath):
		fullQialified = os.path.join(inputPath, filename)
		f = open(fullQialified, 'r')
		removeTILs(f, filename, outputPath)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[0], sys.argv[1:])