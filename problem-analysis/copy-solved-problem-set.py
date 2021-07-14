#! /usr/bin/python
#Author: Tony Allard
#Date: 30 May 2021
#Description: Copies all problems to a target directory, where at least one planner solved the problem

import os
import sys
import argparse
import gzip
import re
from shutil import copyfile
import AnalysisCommon
import ExtractSuccess

def extractProblemName(logFileBuffer):

	plannerCommand = AnalysisCommon.extractPlannerCommand(logFileBuffer)
	parts = plannerCommand.split(" ")
	domain_prob = []
	for part in parts[1:]: #ignore first one that is the planner executable
		if "pddl" in part.lower():
			domain_prob.append(part.split("/")[-1]) #get last one
	
	return domain_prob		

def processLogs(logStructure):

	results = {}
	for planner in logStructure:
		for problemDomain in logStructure[planner]:
			if problemDomain not in results:
				results[problemDomain] = {}
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
				if ExtractSuccess.extractValidatorSuccess(buffer, planner, fullQualified):
					domain_prob = extractProblemName(buffer)
					results[problemDomain][domain_prob[1]] = domain_prob[0]

	return results

def main(args):

	parser = argparse.ArgumentParser(description='Copy problems that were marked as solved by at least one planner.')
	parser.add_argument('log_path',
	                    metavar='/path/to/logs/',
						type=str,
		                help='the location of the logs')
	parser.add_argument('problem_path',
	                    metavar='/path/to/problems/',
						type=str,
		                help='the location of the problem files')	          
	parser.add_argument('new_problem_path',
	                    metavar='/path/to/copy/problems/',
						type=str,
		                help='the desired location to copy the problem files')	          		                
	args = parser.parse_args()
	
	if not os.path.isdir(args.log_path):
		print "Error: %s is not a valid directory"%(args.log_path)
		sys.exit(-1)
		
	if not os.path.isdir(args.problem_path):
		print "Error: %s is not a valid directory"%(args.problem_path)
		sys.exit(-1)
		
	if not os.path.isdir(args.new_problem_path):
		print "Error: %s is not a valid directory"%(args.new_problem_path)
		sys.exit(-1)

	logStructure = AnalysisCommon.getLogStructure(args.log_path)
	results = processLogs(logStructure)
	
	print results
	
	for problemDomain in results:
		print "%s:"%problemDomain
		problemFolder = os.path.join(args.problem_path, problemDomain)
		if not os.path.isdir(problemFolder):
			print "Error: %s is not in the problems directory. Skipping..."%(problemFolder)
			continue
		
		print results[problemDomain].keys()
		for problem in os.listdir(problemFolder):
			print problem
			print results[problemDomain].keys()
			if problem in results[problemDomain].keys(): #problem was solved
				print "found"
				print (problemDomain, results[problemDomain][problem], problem)
				new_problem_path = os.path.join(args.new_problem_path, problemDomain)
				
				original_problem = os.path.join(problemFolder, problem)
				original_domain = os.path.join(problemFolder, results[problemDomain][problem])
				
				new_problem = os.path.join(new_problem_path, problem)
				new_domain = os.path.join(new_problem_path, results[problemDomain][problem])				
				
				if not os.path.exists(new_problem_path):
					os.mkdir(new_problem_path)
						
				copyfile(original_problem, new_problem)
				copyfile(original_domain, new_domain)				

	

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)
