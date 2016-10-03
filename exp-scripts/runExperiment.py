#!/usr/bin/python

import sys
import os
from datetime import datetime
import processProblem

def main (args):

	expStart = datetime.now()
	print "%s : Experiment Started"%expStart
	directory = args[0]
	for filename in os.listdir(directory):
		fullPath = directory + filename
		print fullPath
		processProblem.main(fullPath)

	expEnd = datetime.now()
	print "%s : Experiment Completed"%expEnd
	print "Runtime: %s seconds."%((expEnd-expStart).total_seconds())


#Run Main Function
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Error: There must be at least 1 argument"
		sys.exit(1)
	main(sys.argv[1:])