#!/usr/bin/python3
#Author: Tony Allard
#Date: 15 November 2017
#Last Updated: 09 Feb 2021
#Description: A Python script for extracting invalid plans from log files

import sys
import os
import argparse
import re
import gzip
import AnalysisCommon

invalidPlan_check 	= re.compile(AnalysisCommon.VALIDATOR_FAILURE)

def isInvalidPlan(log):
	for line in log:
		#check problem for timeout
		if invalidPlan_check.search(line) is not None:
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
	planStructure = AnalysisCommon.getPlanStructure(args.path)

	for planner in sorted(logStructure):
		print(planner)
		for problemDomain in logStructure[planner]:
			numFail = 0
			failPlans = []
			failCmds = []
			logPath = logStructure[planner][problemDomain]
			planPath = planStructure[planner][problemDomain]
			for filename in os.listdir(logPath):
				fullQualified = os.path.join(logPath, filename)
				with gzip.open(fullQualified, 'rt') as f:
					try:
						buffer = AnalysisCommon.bufferFile(f)
					except IOError:
						continue
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue
					
				fullQualifiedPlan = os.path.join(planPath, 
					filename.replace(
						AnalysisCommon.COMPRESSED_LOG_FILE_EXT,
						AnalysisCommon.COMPRESSED_PLAN_FILE_EXT))
						
				with gzip.open(fullQualifiedPlan, 'rt') as p:
					try:
						planBuffer = AnalysisCommon.bufferFile(p)
					except IOError:
						continue
						
				if isInvalidPlan(buffer) and planBuffer:
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
