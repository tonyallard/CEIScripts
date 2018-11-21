#! /usr/bin/python
#Author: Tony Allard
#Date: 06 April 2016
#Description: Common methods for problem analysis

import os
import sys
import gzip
import re
import AnalysisCommon
import ExtractSuccess

timeout_check = re.compile(AnalysisCommon.TIMEOUT_DELIM)
mem_check = re.compile("%s|%s"%(AnalysisCommon.MEMORY_ERROR_DELIM, \
		AnalysisCommon.LPG_TIMEOUT_DELIM))
unsolvable_check = re.compile(AnalysisCommon.SEARCH_FAILURE_DELIM)
invalidPlan_check = re.compile(AnalysisCommon.INVALID_PLAN_DELIM)

def isMemoryFail(log):
	for line in log:
		#check problem for memory crash
		if mem_check.search(line) is not None:
			return True
	return False

def isTimeOutFail(log):
	for line in log:
		#check problem for timeout
		if timeout_check.search(line) is not None:
			return True
	return False

def isUnsolvable(log):
	for line in log:
		#check problem for timeout
		if unsolvable_check.search(line) is not None:
			return True
	return False

def isInvalidPlan(log):
	for line in log:
		#check problem for timeout
		if invalidPlan_check.search(line) is not None:
			return True
	return False

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
	inputPath = args[1]
	verbose = False
	if len(args) > 2:
		verbose = True

	logStructure = getLogStructure(inputPath)

	for planner in logStructure:
		print planner
		for problemDomain in logStructure[planner]:
			logPath = logStructure[planner][problemDomain]

			memFailProbe = []
			timeoutFailProbs = []
			unsolvableProbs = []
			invalidPlanProbs = []
			otherFailProbs = []
			success = 0
			failure = 0
			memFails = 0
			timeoutFails = 0
			unsolvableFails = 0
			invalidPlanFails = 0
			otherFails = 0

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
				if ((planner == "lpg-td" and \
						ExtractSuccess.extractLPGTDSuccess(buffer, fullQualified)) or \
						(ExtractSuccess.extractValidatorSuccess(buffer, fullQualified))):
						success += 1
				else:
					failure += 1
					if isMemoryFail(buffer):
						memFailProbe.append(filename)
						memFails += 1
					elif isTimeOutFail(buffer):
						timeoutFailProbs.append(filename)
						timeoutFails += 1
					elif isUnsolvable(buffer):
						unsolvableProbs.append(filename)
						unsolvableFails += 1
					elif isInvalidPlan(buffer):
						invalidPlanProbs.append(filename)
						invalidPlanFails += 1
					else:
						otherFailProbs.append(filename)
						otherFails += 1
			
			print "\t\tSuccess: %i"%success
			print "\t\tFailure: %i (%i memory, %i timeout, %i unsolvable, %i invalid plan, %i other)"\
				%(failure, memFails, timeoutFails, unsolvableFails, invalidPlanFails, otherFails)
			if verbose:
				#Print problems
				if memFails > 0:
					print "\t\t\tProblems that ran out of memory:"
					for prob in memFailProbe:
						print "\t\t\t\t%s"%prob

				if timeoutFails > 0:
					print "\n\t\t\tProblems that exceeded CPU time:"
					for prob in timeoutFailProbs:
						print "\t\t\t\t%s"%prob

				if unsolvableFails > 0:
					print "\n\t\t\tProblems that were unsolvable:"
					for prob in unsolvableProbs:
						print "\t\t\t\t%s"%prob

				if invalidPlanFails > 0:
					print "\n\t\t\tProblems where the plan found was invlaid:"
					for prob in invalidPlanProbs:
						print "\t\t\t\t%s"%prob

				if otherFails > 0:
					print "\n\t\t\tProblems failed for other reasons:"
					for prob in otherFailProbs:
						print "\t\t\t\t%s"%prob

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)