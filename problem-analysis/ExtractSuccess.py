#! /usr/bin/python3
#Author: Tony Allard
#Date: 07 October 2016
#Description: A Python script for extracting whether or not a planner was successful.

import sys
import os
import argparse
import re
import gzip
import AnalysisCommon

def extractLPGTDSuccess(log, filename):
	checkPlanExistsLPGTD(log, filename)
	for line in log:
		if AnalysisCommon.LPGTD_SUCCESS_DELIM in line:
			return 1
	return 0

def extractColinSuccess(log, planner, filename):
	checkPlanExists(log, planner, filename)
	for line in log:
		if AnalysisCommon.COLIN_SUCCESS_DELIM in line:
			return 1
	return 0

def extractValidatorSuccess(log, planner, filename):
	checkPlanExists(log, planner, filename)
	for line in log:
		if AnalysisCommon.VALIDATOR_SUCCESS in line:
			return 1
		elif AnalysisCommon.VALIDATOR_FAILURE in line:
			return 0
	raise RuntimeError("Error! Success unknown for %s"%filename)

def checkPlanExists(log, planner, filename):
	for line in log:
		if AnalysisCommon.VALIDATOR_PLAN_EXECUTE_SUCCESS in line:
			return
		elif (AnalysisCommon.VALIDATOR_PLAN_EXECUTE_FAILURE in line) or \
			(AnalysisCommon.VALIDATOR_PLAN_GOAL_FAILURE in line):
			print("The following file produced a plan, but it was invalid:" +\
					"\n\t%s: %s"%(planner, filename))
			return
		elif (planner in AnalysisCommon.PLANNERS_THAT_WRITE_THEIR_OWN_PLAN_FILES) and \
			(AnalysisCommon.VALIDATOR_NO_PLAN in line):
			print("%s: %s did not produce a plan, but that maybe ok as it could "%(planner, filename) +\
					"have exhausted CPU/memory. Investigate.")
			return
	raise RuntimeError("Error! No plan assessed for %s: %s"%(planner, filename))

def checkPlanExistsLPGTD(log, filename):
	for line in log:
		if (AnalysisCommon.VALIDATOR_PLAN_EXECUTE_SUCCESS in line) or \
			(AnalysisCommon.VALIDATOR_BAD_PLAN_DESCRIPTION in line):
			return
		elif (AnalysisCommon.VALIDATOR_PLAN_EXECUTE_FAILURE in line) or \
			(AnalysisCommon.VALIDATOR_PLAN_GOAL_FAILURE in line):
			print("The following file produced a plan, but it was invalid:\n\t%s"%filename)
			return
	raise RuntimeError("Error! No plan assessed for %s"%filename)

def main(args):
	
	parser = argparse.ArgumentParser(description='A Python script for extracting the coverage of a problem domain from experimentation logs.')
	parser.add_argument('path',
	                    metavar='/path/to/planner/logs/',
						type=str,
		                help='the location of the logs for a specific planner')
	args = parser.parse_args()
		                
	if not os.path.isdir(args.path):
		print("Error: %s is not a valid directory"%args.path)
		sys.exit(-1)
	
	inputPath = args.path

	logStructure = AnalysisCommon.getLogStructure(inputPath)

	for planner in logStructure:
		print(planner)
		for problemDomain in logStructure[planner]:
			logPath = logStructure[planner][problemDomain]

			success = 0
			failure = 0

			for filename in os.listdir(logPath):
				fullQualified = os.path.join(logPath, filename)
				buffer = AnalysisCommon.bufferCompressedFile(fullQualified)
				if buffer == -1:
					continue
			
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue
				if extractValidatorSuccess(buffer, planner, fullQualified):
					success += 1
				else:
					failure += 1
			print("\t%s"%problemDomain)
			print("\t\tSuccess: %i"%success)
			print("\t\tFailure: %i"%failure)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])
