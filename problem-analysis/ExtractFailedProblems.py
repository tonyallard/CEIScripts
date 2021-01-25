#! /usr/bin/python
#Author: Tony Allard
#Date: 06 April 2016
#Description: Common methods for problem analysis

import os
import sys
import argparse
import gzip
import re
import AnalysisCommon
import ExtractSuccess

segfault_check		= re.compile("%s|%s"%(	AnalysisCommon.SEGMENTATION_FAULT, \
											AnalysisCommon.SEGMENTATION_FAULT_IN_SUB_CMD))
timeout_check 		= re.compile(AnalysisCommon.TIMEOUT_DELIM)
mem_check 			= re.compile("%s|%s"%(AnalysisCommon.MEMORY_ERROR_DELIM, \
						AnalysisCommon.LPG_TIMEOUT_DELIM))
unsolvable_check 	= re.compile("%s|%s"%(	AnalysisCommon.SEARCH_FAILURE_DELIM, \
											AnalysisCommon.UNSOLVABLE_TPLAN))
invalidPlan_check 	= re.compile(AnalysisCommon.INVALID_PLAN_DELIM)

IGNORED_PROBLEMS = [ 
	"driverlogshift" #Driverlog shift is too different a format
]


class PlannerStats():
	
	def __init__(self):
		self.problems = set()
		
		self.SUCCESS_COUNT = {}
		self.FAILED_COUND = {}
		#SEG Faults
		self.SEGMENTATION_FAULT_COUNT = {}
		self.SEGMENTATION_FAULT_LIST = {}	
		#Memory
		self.EXCEEDED_MEMORY_LIMIT_COUNT = {}
		self.EXCEEDED_MEMORY_LIMIT_LIST = {}
		#Time
		self.EXCEEDED_TIME_ALLOCATED_COUNT = {}
		self.EXCEEDED_TIME_ALLOCATED_LIST = {}
		#Unsolvable
		self.PROBLEM_IS_UNSOLVABLE_COUNT = {}
		self.PROBLEM_IS_UNSOLVABLE_LIST = {}
		#Plan Invalid
		self.PLAN_FOUND_IS_INVALID_COUNT = {}
		self.PLAN_FOUND_IS_INVALID_LIST = {}
		#Other
		self.FAILED_FOR_OTHER_REASONS_COUNT = {}
		self.FAILED_FOR_OTHER_REASONS_LIST = {}
	
	def initProblem (self, problem):
		self.SUCCESS_COUNT[problem] = 0
		self.FAILED_COUND[problem] = 0
		#SEG Faults
		self.SEGMENTATION_FAULT_COUNT[problem] = 0
		self.SEGMENTATION_FAULT_LIST[problem] = []	
		#Memory
		self.EXCEEDED_MEMORY_LIMIT_COUNT[problem] = 0
		self.EXCEEDED_MEMORY_LIMIT_LIST[problem] = []
		#Time
		self.EXCEEDED_TIME_ALLOCATED_COUNT[problem] = 0
		self.EXCEEDED_TIME_ALLOCATED_LIST[problem] = []
		#Unsolvable
		self.PROBLEM_IS_UNSOLVABLE_COUNT[problem] = 0
		self.PROBLEM_IS_UNSOLVABLE_LIST[problem] = []
		#Plan Invalid
		self.PLAN_FOUND_IS_INVALID_COUNT[problem] = 0
		self.PLAN_FOUND_IS_INVALID_LIST[problem] = []
		#Other
		self.FAILED_FOR_OTHER_REASONS_COUNT[problem] = 0
		self.FAILED_FOR_OTHER_REASONS_LIST[problem] = []
		
	def incrementSuccess(self, problem):
		self.problems.add(problem)
		self.SUCCESS_COUNT[problem] += 1
		
	def incrementFailure(self, problem):
		self.problems.add(problem)
		self.FAILED_COUND[problem] += 1
		
	def incrementSegFault(self, problem):
		self.problems.add(problem)
		self.SEGMENTATION_FAULT_COUNT[problem] += 1
		
	def incrementMemoryFailure(self, problem):
		self.problems.add(problem)
		self.EXCEEDED_MEMORY_LIMIT_COUNT[problem] += 1
		
	def incrementTimeoutFailure(self, problem):
		self.problems.add(problem)
		self.EXCEEDED_TIME_ALLOCATED_COUNT[problem] += 1
		
	def incrementUnsolvableFailure(self, problem):
		self.problems.add(problem)
		self.PROBLEM_IS_UNSOLVABLE_COUNT[problem] += 1
		
	def incrementInvalidFailure(self, problem):
		self.problems.add(problem)
		self.PLAN_FOUND_IS_INVALID_COUNT[problem] += 1
		
	def incrementOtherFailure(self, problem):
		self.problems.add(problem)
		self.FAILED_FOR_OTHER_REASONS_COUNT[problem] += 1
		
	
	
	def addSegFaultProblem(self, problem, filename):
		self.problems.add(problem)
		self.SEGMENTATION_FAULT_LIST[problem].append(filename)
		
	def addMemFailProblem(self, problem, filename):
		self.problems.add(problem)
		self.EXCEEDED_MEMORY_LIMIT_LIST[problem].append(filename)
		
	def addTimeoutFailProblem(self, problem, filename):
		self.problems.add(problem)
		self.EXCEEDED_TIME_ALLOCATED_LIST[problem].append(filename)
		
	def addUnsolvableFailProblem(self, problem, filename):
		self.problems.add(problem)
		self.PROBLEM_IS_UNSOLVABLE_LIST[problem].append(filename)
		
	def addInvalidFailProblem(self, problem, filename):
		self.problems.add(problem)
		self.PLAN_FOUND_IS_INVALID_LIST[problem].append(filename)
		
	def addOtherFailProblem(self, problem, filename):
		self.problems.add(problem)
		self.FAILED_FOR_OTHER_REASONS_LIST[problem].append(filename)
	
def isSegFault(log):
	for line in log:
		#check problem for memory crash
		if segfault_check.search(line) is not None:
			return True
	return False


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
			
			if problem in IGNORED_PROBLEMS:
				continue
			logDir = os.path.join(plannerDir, problem, AnalysisCommon.OUTPUT_DIR)
			logStructure[planner][problem] = logDir
	return logStructure
	
def processLogs(logStructure):

	results = {}
	for planner in logStructure:
		results[planner] = PlannerStats()
		for problemDomain in logStructure[planner]:
			logPath = logStructure[planner][problemDomain]

			results[planner].initProblem(problemDomain)

			for filename in os.listdir(logPath):
				fullQualified = os.path.join(logPath, filename)
				with gzip.open(fullQualified, 'rb') as f:
					try:
						buffer = AnalysisCommon.bufferFile(f)
					except IOError:
						continue
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue
				if ExtractSuccess.extractValidatorSuccess(buffer, planner, fullQualified):
					results[planner].incrementSuccess(problemDomain)
				else:
					results[planner].incrementFailure(problemDomain)
					if isSegFault(buffer):
						results[planner].addSegFaultProblem(problemDomain, filename)
						results[planner].incrementSegFault(problemDomain)
					elif isMemoryFail(buffer):
						results[planner].addMemFailProblem(problemDomain, filename)
						results[planner].incrementMemoryFailure(problemDomain)
					elif isTimeOutFail(buffer):
						results[planner].addTimeoutFailProblem(problemDomain, filename)
						results[planner].incrementTimeoutFailure(problemDomain)
					elif isUnsolvable(buffer):
						results[planner].addUnsolvableFailProblem(problemDomain, filename)
						results[planner].incrementUnsolvableFailure(problemDomain)
					elif isInvalidPlan(buffer):
						results[planner].addInvalidFailProblem(problemDomain, filename)
						results[planner].incrementInvalidFailure(problemDomain)
					else:
						results[planner].addOtherFailProblem(problemDomain, filename)
						results[planner].incrementOtherFailure(problemDomain)
						
	return results
			
def main(args):

	parser = argparse.ArgumentParser(description='Determine problems that failed from execution logs.')
	parser.add_argument('path',
	                    metavar='/path/to/logs/',
						type=str,
		                help='the location of the logs')
	parser.add_argument('-v',
						'--verbose',
						action='store_true',
						help='verbosity of the output')
	args = parser.parse_args()
	
	if not os.path.isdir(args.path):
		print "Error: %s is not a valid directory"%(args.path)
		sys.exit(-1)


	logStructure = getLogStructure(args.path)
	results = processLogs(logStructure)
	
	#Print statistics
	for planner in results:
		print "%s:"%planner
		plannerStat = results[planner]
		for problem in plannerStat.problems:
			print "\t%s:"%problem
			print "\t\tSuccess: %i"%plannerStat.SUCCESS_COUNT[problem]
			print "\t\tFailure: %i (%i SIGSEGV, %i memory, %i timeout, %i unsolvable, %i invalid plan, %i other)"\
				%(	plannerStat.FAILED_COUND[problem],
					plannerStat.SEGMENTATION_FAULT_COUNT[problem],
					plannerStat.EXCEEDED_MEMORY_LIMIT_COUNT[problem],
					plannerStat.EXCEEDED_TIME_ALLOCATED_COUNT[problem],
					plannerStat.PROBLEM_IS_UNSOLVABLE_COUNT[problem],
					plannerStat.PLAN_FOUND_IS_INVALID_COUNT[problem],
					plannerStat.FAILED_FOR_OTHER_REASONS_COUNT[problem])
	
			if args.verbose:
				#Print problems
				if plannerStat.SEGMENTATION_FAULT_COUNT[problem] > 0:
					print "\t\t\tProblems that had a Segmentation Fault:"
					for prob in plannerStat.SEGMENTATION_FAULT_LIST[problem]:
						print "\t\t\t\t%s"%prob
						
				if plannerStat.EXCEEDED_MEMORY_LIMIT_COUNT[problem] > 0:
					print "\t\t\tProblems that ran out of memory:"
					for prob in plannerStat.EXCEEDED_MEMORY_LIMIT_LIST[problem]:
						print "\t\t\t\t%s"%prob

				if plannerStat.EXCEEDED_TIME_ALLOCATED_COUNT[problem] > 0:
					print "\n\t\t\tProblems that exceeded CPU time:"
					for prob in plannerStat.EXCEEDED_TIME_ALLOCATED_LIST[problem]:
						print "\t\t\t\t%s"%prob

				if plannerStat.PROBLEM_IS_UNSOLVABLE_COUNT[problem] > 0:
					print "\n\t\t\tProblems that were unsolvable:"
					print "\t\t\t\t !Note this could be a sub-planner failure!"
					for prob in plannerStat.PROBLEM_IS_UNSOLVABLE_LIST[problem]:
						print "\t\t\t\t%s"%prob

				if plannerStat.PLAN_FOUND_IS_INVALID_COUNT[problem] > 0:
					print "\n\t\t\tProblems where the plan found was invlaid:"
					for prob in plannerStat.PLAN_FOUND_IS_INVALID_LIST[problem]:
						print "\t\t\t\t%s"%prob

				if plannerStat.FAILED_FOR_OTHER_REASONS_COUNT[problem] > 0:
					print "\n\t\t\tProblems failed for other reasons:"
					for prob in plannerStat.FAILED_FOR_OTHER_REASONS_LIST[problem]:
						print "\t\t\t\t%s"%prob

	

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)
