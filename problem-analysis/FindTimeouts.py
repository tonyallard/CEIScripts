#!/usr/bin/python3
#Author: Tony Allard
#Date: 15 November 2017
#Last Updated: 09 Feb 2021
#Description: A Python script for extracting segmentation faults from log files

import sys
import os
import argparse
import re
import gzip
import AnalysisCommon

segfault_check		= re.compile("%s|%s"%(	AnalysisCommon.SEGMENTATION_FAULT, \
											AnalysisCommon.SEGMENTATION_FAULT_IN_SUB_CMD))

def isSegFault(log):
	for line in log:
		#check problem for memory crash
		if segfault_check.search(line) is not None:
			return True
	return False

def main(args):

	parser = argparse.ArgumentParser(description='Determine problems that failed from execution logs.')
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
			numSegs = 0
			segPlans = []
			segCmds = []
			logPath = logStructure[planner][problemDomain]
			for filename in os.listdir(logPath):
				fullQualified = os.path.join(logPath, filename)
				with gzip.open(fullQualified, 'rt') as f:
					try:
						buffer = AnalysisCommon.bufferFile(f)
					except IOError:
						continue
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue
				if isSegFault(buffer):
					numSegs += 1
					segPlans.append(filename)
					segCmds.append(AnalysisCommon.extractPlannerCommand(buffer))
					
			print("\t%s: %s"%(problemDomain, numSegs))
			if args.verbose:
				i = 0
				for prob in sorted(segPlans):
					i+=1
					print("\t\t%s: %s"%(i,prob))
					
			if args.commands:
				for cmd in segCmds:
					print(cmd)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])
