#!/usr/bin/python3
#Author: Tony Allard
#Date: 15 November 2017
#Last Updated: 09 Feb 2021
#Description: A Python script for extracting segmentation faults from log files

import sys
import os
import argparse
import re
import AnalysisCommon

mem_check 			= re.compile("%s|%s|%s"%(AnalysisCommon.MEMORY_ERROR_DELIM, \
						AnalysisCommon.MADAGASCAR_MEMORY_DELIM, \
						AnalysisCommon.MADAGASCAR_OWN_ALLOC_MEMORY_DELIM))

def isMemoryFail(log):
	for line in log:
		#check problem for memory crash
		if mem_check.search(line) is not None:
			return True
	return False

def main(args):

	parser = argparse.ArgumentParser(description='Determine planner / problem combinations that failed due to exceeeding allowed memory.')
	parser.add_argument('path',
	                    metavar='/path/to/logs/',
						type=str,
		                help='the location of the logs')
	parser.add_argument('-v',
						'--verbose',
						action='store_true',
						help='Show the logs that recorded failed')
	parser.add_argument('-c',
						'--commands',
						action='store_true',
						help='Show the commands for the failed plans')
	args = parser.parse_args()
	
	if not os.path.isdir(args.path):
		print("Error: %s is not a valid directory"%args.path)
		sys.exit(-1)


	logStructure = AnalysisCommon.getLogStructure(args.path)

	for planner in sorted(logStructure):
		print(planner)
		for problemDomain in logStructure[planner]:
			numFail = 0
			failPlans = []
			failCmds = []
			logPath = logStructure[planner][problemDomain]
			for filename in os.listdir(logPath):
				fullQualified = os.path.join(logPath, filename)
				buffer = AnalysisCommon.bufferCompressedFile(fullQualified)
				if buffer == -1:
					continue
				
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue
				if isMemoryFail(buffer):
					numFail += 1
					failPlans.append(filename)
					failCmds.append(AnalysisCommon.extractPlannerCommand(buffer))
					
			print("\t%s: %s"%(problemDomain, numFail))
			if args.verbose:
				i = 0
				for prob in sorted(failPlans):
					i+=1
					print("\t\t%s: %s"%(i,prob))
					
			if args.commands:
				for cmd in sorted(failCmds):
					print(cmd)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])
