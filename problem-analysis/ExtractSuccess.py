#! /usr/bin/python
#Author: Tony Allard
#Date: 07 October 2016
#Description: A Python script for extracting whether or not a planner was successful.

import sys
import os
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
			print "The following file produced a plan, but it was invalid:" +\
					"\n\t%s: %s"%(planner, filename)
			return
		elif (planner in AnalysisCommon.PLANNERS_THAT_WRITE_THEIR_OWN_PLAN_FILES) and \
			(AnalysisCommon.VALIDATOR_NO_PLAN in line):
			print "%s: %s did not produce a plan, but that maybe ok as it could "%(planner, filename) +\
					"have exhausted CPU/memory. Investigate."
			return
	raise RuntimeError("Error! No plan assessed for %s: %s"%(planner, filename))

def checkPlanExistsLPGTD(log, filename):
	for line in log:
		if (AnalysisCommon.VALIDATOR_PLAN_EXECUTE_SUCCESS in line) or \
			(AnalysisCommon.VALIDATOR_BAD_PLAN_DESCRIPTION in line):
			return
		elif (AnalysisCommon.VALIDATOR_PLAN_EXECUTE_FAILURE in line) or \
			(AnalysisCommon.VALIDATOR_PLAN_GOAL_FAILURE in line):
			print "The following file produced a plan, but it was invalid:\n\t%s"%filename
			return
	raise RuntimeError("Error! No plan assessed for %s"%filename)

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

			success = 0
			failure = 0

			for filename in os.listdir(logPath):
				fullQualified = os.path.join(logPath, filename)
				with gzip.open(fullQualified, 'rb') as f:
					try:
						buffer = AnalysisCommon.bufferFile(f)
					except IOError:
						continue
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue
				if extractValidatorSuccess(buffer, planner, fullQualified):
					success += 1
				else:
					failure += 1
			print "\t%s"%problemDomain
			print "\t\tSuccess: %i"%success
			print "\t\tFailure: %i"%failure

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])