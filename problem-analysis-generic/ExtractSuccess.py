#! /usr/bin/python
#Author: Tony Allard
#Date: 07 October 2016
#Description: A Python script for extracting whether or not a planner was successful.

import sys
import os
import re
import AnalysisCommon

def extractSuccess(log):
	for line in log:
		if AnalysisCommon.SUCCESS_DELIM in line:
			return 1
	return 0

def main(args):
	inputPath = args[0]
	for filename in os.listdir(inputPath):
		fullQialified = os.path.join(inputPath, filename)
		f = open(fullQialified)
		buffer = AnalysisCommon.bufferFile(f)
		success = extractSuccess(buffer)
		print "%s,%i"%(filename, success)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])