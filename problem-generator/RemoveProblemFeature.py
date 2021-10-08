#!/usr/bin/python
'''
A script for removing specific PDDL features from domain/problem files
'''
import sys
import os
import re
from shutil import copyfile

#Usage *.py /path/to/files /new/path/to/files [copy domains]


TIL = "\(at [0-9]+\.?[0-9]* \([a-zA-Z0-9\-_ \(\)]+\)"
MAYBE_DECIMAL_NUMBER = "[0-9]+\.?[0-9]*"
PREDICATE = "\([a-zA-Z0-9\-_ ]+\)"
NOT_TEXT = "\([ ]*not[ ]*\("
#(\(( )*(not) ( )?)?
#( ( )?\))?

METRIC = "[\s]*\(:metric minimize \(total-cost\)\)"

def bufferFile(file):
	fileBuffer = []
	for line in file:
		fileBuffer.append(line)
	return fileBuffer

def findTILs(problem):
	tils = []
	for line in problem:
		til = re.findall(TIL, line)
		if len(til) == 1:
			tils.append(til[0])
	return tils
	
	
def removeMetric(buffer, f):
	metric_searcher = re.compile(METRIC)
	for line in buffer:
		if not metric_searcher.search(line):
			f.write(line)
			
def main(args):
	problemPath = args[0]
	newProblemPath = args[1]
	createDomainFiles = False
	if len(args) == 3:
		createDomainFiles = True

	for root, dirs, files in os.walk(problemPath):
		for file in files:
			if "DOMAIN" in file:
				if createDomainFiles:
					copyfile(os.path.join(root, file), os.path.join(newProblemPath, file))
				continue

			f = open(os.path.join(root, file), 'r')
			buffer = bufferFile(f)
			f.close()
			
			w = open(os.path.join(newProblemPath, file), 'w')
			removeMetric(buffer, w)
			w.close()
		break


#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])
