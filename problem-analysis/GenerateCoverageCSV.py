#! /usr/bin/python3
#Author: Tony Allard
#Date: 01 Feb 2021
#Description: Create a CSV for easier planner coverage comparison

import os
import sys
import argparse
import gzip
import re
import AnalysisCommon
import ExtractSuccess


IGNORED_PROBLEMS = [ 
	"driverlogshift" #Driverlog shift is too different a format
]

PLANNERS_TO_PRINT = [

	"Colin-RPG",
	#"NoSD-Colin-RPG",
	"POPF-RPG",
	#"NoSD-POPF-RPG",
	#"Optic-RPG",
	#"Optic-SLFRP",
	#"lpg-td",
	"Colin-TRH-Colin",
	#"ablation-Colin-TRH-Colin",
	"Popf-TRH-Popf",
	#"ablation-Popf-TRH-Popf",
	#"NoSD-Colin-TRH-Colin",
	#"NoSD-ablation-Colin-TRH-Colin",
	#"NoSD-Popf-TRH-Popf",
	#"NoSD-ablation-Popf-TRH-Popf",
	#"MetricFF",
	#"fd_FF",
	#"fd_blind",
	#"madagascar",
	"tplanS0T0", #All Ground Operators
	"tplanS0T1",
	"tplanS1T0", #Selective Ground Operators
	"tplanS1T1",
	"tplanS2T0", #Operator Add Effects
	"tplanS2T1",
	"tplanS3T0", #Most Recent Operator Add Effects
	"tplanS3T1",
	"tplanS4T0", #Operator Effects
	"tplanS4T1",
	"tplanS5T0", #Most Recent Operator Effects
	"tplanS5T1"
]

def check_file_writable(fnm):
    if os.path.exists(fnm):
        # path exists
        if os.path.isfile(fnm): # is it a file or a dir?
            # also works when file is a link and the target is writable
            return os.access(fnm, os.W_OK)
        else:
            return False # path is a dir, so cannot write as a file
    # target does not exist, check perms on parent dir
    pdir = os.path.dirname(fnm)
    if not pdir: pdir = '.'
    # target is creatable if parent dir is writable
    return os.access(pdir, os.W_OK)

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

def incrementCoverage(results, planner, domain, problem, increment=1):
	if domain not in results:
		results[domain] = {}
	if problem not in results[domain]:
		results[domain][problem] = {}
	if planner not in results[domain][problem]:
		results[domain][problem][planner] = 0
		
	results[domain][problem][planner] += increment
	
def processLogs(logStructure):
	
	FILE_SUFFIX = ".PDDL"
	results = {}
	for planner in logStructure:
		for problemDomain in logStructure[planner]:
			logPath = logStructure[planner][problemDomain]
			for filename in os.listdir(logPath):
				problem = filename[0:filename.upper().find(FILE_SUFFIX)]
				fullQualified = os.path.join(logPath, filename)
				
				with gzip.open(fullQualified, 'rt') as f:
					try:
						buffer = AnalysisCommon.bufferFile(f)
					except IOError:
						continue
				
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue
				if ExtractSuccess.extractValidatorSuccess(buffer, planner, fullQualified):
					incrementCoverage(results, planner, problemDomain, problem)
				else:
					incrementCoverage(results, planner, problemDomain, problem, 0)
	return results
	
def main(args):

	parser = argparse.ArgumentParser(description='Output a CSV for easier planner coverage comparison')
	parser.add_argument('path',
	                    metavar='/path/to/logs/',
						type=str,
		                help='the location of the logs')
	parser.add_argument('-o',
						'--output',
	                    metavar='/path/to/csv/file/',
						type=str,
						help='Output to file instead of console')
	args = parser.parse_args()
	
	if not os.path.isdir(args.path):
		print("Error: %s is not a valid directory"%(args.path))
		sys.exit(-1)
		
	if args.output and not check_file_writable(args.output):
		print("Error: Cannot write to %s"%(args.output))
		sys.exit(-1)


	logStructure = getLogStructure(args.path)
	results = processLogs(logStructure)
	
	print('Problem', end='')
	for planner in PLANNERS_TO_PRINT:
		print(",%s"%planner, end='')
	print()
	
	for domain in results:
		print("{},".format(domain))
		for problem in sorted(results[domain].keys()):
			print("{},".format(problem), end='')
			for planner in PLANNERS_TO_PRINT:
				if planner not in results[domain][problem]:
					print("N/A,", end="")
				else:
					print("{},".format(results[domain][problem][planner]), end='')
			print()

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)
