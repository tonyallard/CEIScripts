#! /usr/bin/python
#Author: Tony Allard
#Date: 15 November 2017
#Description: A Python script for extracting segmentation faults from log files

import sys
import os
import re
import gzip
import AnalysisCommon

SEG_FAULT = "segmentation"

def containsSegFault(log):
	for line in log:
		if SEG_FAULT in line.lower():
			return 1
	return 0

def getLogStructure(rootDir):
	logStructure = {}
	for planner in os.listdir(rootDir):
		plannerDir = os.path.join(rootDir, planner)
		
		if (not os.path.isdir(plannerDir)):
			continue
		
		logStructure[planner] = {}

		for problem in os.listdir(plannerDir):
			#Driverlog shift is too different a format
			if problem == "driverlogshift":
				continue
			logDir = os.path.join(plannerDir, problem, AnalysisCommon.OUTPUT_DIR)
			logStructure[planner][problem] = logDir
	return logStructure

def main(args):
	inputPath = args[0]


	logStructure = getLogStructure(inputPath)

	for planner in logStructure:
		print planner
		for problemDomain in logStructure[planner]:
			logPath = logStructure[planner][problemDomain]
			print "\t%s"%problemDomain
			for filename in os.listdir(logPath):
				fullQualified = os.path.join(logPath, filename)
				with gzip.open(fullQualified, 'rb') as f:
					try:
						buffer = AnalysisCommon.bufferFile(f)
					except IOError:
						continue
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue
				if containsSegFault(buffer):
					print "\t\t%s"%filename

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])