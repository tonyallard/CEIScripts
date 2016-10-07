#! /usr/bin/python
#Author: Tony Allard
#Date: 07 October 2016
#Description: A Python script for extracting the number of dead ends encountered by the planner.
#Extracts data to CSV file, including averages.

import sys
import os
import re
import AnalysisCommon

DEAD_END_COUNT_DELIM = "#; Search encountered"
DEAD_END_COUNT_TERM_DELIM = " dead ends"

def extractDeadEnds(log):
	for line in log:
		if DEAD_END_COUNT_DELIM in line:
			deadEndCount = re.findall(r'\d+\.\d+', line)
			if len(deadEndCount) == 0:
				return 0
			return int(deadEndCount[0])

def main(args):
	inputPath = args[0]
	for filename in os.listdir(inputPath):
		fullQialified = os.path.join(inputPath, filename)
		f = open(fullQialified)
		buffer = AnalysisCommon.bufferFile(f)
		deadEndCount = extractDeadEnds(buffer)
		print filename, deadEndCount

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])