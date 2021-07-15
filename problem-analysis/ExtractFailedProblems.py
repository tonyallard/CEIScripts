#! /usr/bin/python
#Author: Tony Allard
#Date: 06 April 2016
#Description: Extracts the reasons for failue from experimenation log files.

import os
import sys
import argparse
import re
import AnalysisCommon
import ExtractSuccess
import FindSegFaults
import FindMemFails
import FindTimeouts
import FindUnsolvables
import FindInvalidPlan

from PlannerStats import *

def processLogs(logStructure):

	results = {}
	for planner in logStructure:
		results[planner] = PlannerStats()
		for problemDomain in logStructure[planner]:
			logPath = logStructure[planner][problemDomain]

			results[planner].initProblem(problemDomain)

			for filename in os.listdir(logPath):
				fullQualified = os.path.join(logPath, filename)
				buffer = AnalysisCommon.bufferCompressedFile(fullQualified)
				if buffer == -1:
					continue
			
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue
				if ExtractSuccess.extractValidatorSuccess(buffer, planner, fullQualified):
					results[planner].addSuccessProblem(problemDomain, filename)
					results[planner].incrementSuccess(problemDomain)
				else:
					results[planner].incrementFailure(problemDomain)
					if FindSegFaults.isSegFault(buffer):
						results[planner].addSegFaultProblem(problemDomain, filename)
						results[planner].incrementSegFault(problemDomain)
					elif FindMemFails.isMemoryFail(buffer):
						results[planner].addMemFailProblem(problemDomain, filename)
						results[planner].incrementMemoryFailure(problemDomain)
					elif FindTimeouts.isTimeout(buffer):
						results[planner].addTimeoutFailProblem(problemDomain, filename)
						results[planner].incrementTimeoutFailure(problemDomain)
					elif FindUnsolvables.isUnsolvable(buffer):
						results[planner].addUnsolvableFailProblem(problemDomain, filename)
						results[planner].incrementUnsolvableFailure(problemDomain)
					elif FindInvalidPlan.isInvalidPlan(buffer):
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
						help='Show the logs that recorded failed')
	parser.add_argument('-V',
						'--Verbose',
						action='store_true',
						help='Show the logs that recorded successful plans')
	args = parser.parse_args()
	
	if not os.path.isdir(args.path):
		print "Error: %s is not a valid directory"%(args.path)
		sys.exit(-1)


	logStructure = AnalysisCommon.getLogStructure(args.path)
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
			elif args.Verbose:
				if plannerStat.SUCCESS_COUNT[problem] > 0:
					print "\n\t\t\tProblems that recorded a successful plan:"
					for prob in plannerStat.SUCCESS_LIST[problem]:
						print "\t\t\t\t%s"%prob
					

	

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)
