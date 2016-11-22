#!/usr/bin/python
#Author: Tony Allard
#Date: 21 November 2016
#Description: A Python script for extracting problems that were unsovleable.

import sys
import os
import re
import AnalysisCommon

def extractUnsolveable(log):
	for line in log:
		if AnalysisCommon.SEARCH_FAILURE_DELIM in line:
			return 1
	return 0

def main(args):
	inputPath = args[0]
	for filename in os.listdir(inputPath):
		if os.path.isdir(os.path.join(inputPath, filename)):
			continue
		fullQialified = os.path.join(inputPath, filename)
		f = open(fullQialified)
		buffer = AnalysisCommon.bufferFile(f)
		unsovleable = extractUnsolveable(buffer)
		if unsovleable:
			print "%s,%i"%(filename, unsovleable)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])