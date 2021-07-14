#!/usr/bin/python3
#Author: Tony Allard
#Date: 01 July 2021
#Description: A Python script for extracting plans from output and putting them in the plans folder.

import sys
import os
import subprocess
import argparse
import re
import gzip
import AnalysisCommon

COLIN_LIKE_PLANNERS = [	"Colin-TRH-Colin", 
						"Popf-TRH-Popf", 
						"Colin-RPG", 
						"POPF-RPG", 
						"Optic", 
						"Optic-SLFRP", 
						"tplan",
						"tplanS0T0", 
						"tplanS0T1",
						"tplanS1T0",
						"tplanS1T1",
						"tplanS2T0",
						"tplanS2T1",
						"tplanS3T0",
						"tplanS3T1",
						"tplanS4T0",
						"tplanS4T1",
						"tplanS5T0",
						"tplanS5T1",
						"tplanS6T0",
						"tplanS6T1",
						"tplanS7T0",
						"tplanS7T1"
						 ]
LPG_PLANNERS = ["lpg-td"]
FD_PLANNERS = ["fd_FF", "fd_blind"]
METRICFF_PLANNERS = ["MetricFF"]
MADAGASCAR_PLANNERS = ["madagascar"]

#Regex to find plan
COLIN_PLAN_SYNTAX = "\d+\.*\d*:[\s]+\([0-9A-Za-z\-\_ ]+\)[\s]+\[\d+\.*\d*\]"
COLIN_PLAN_REGEX = re.compile(COLIN_PLAN_SYNTAX)


FD_PLAN_SYNTAX = "[0-9A-Za-z\-\_ ]+ \(1\)"
FD_PLAN_REGEX = re.compile(FD_PLAN_SYNTAX)

METRICFF_PLAN_SYNTAX = "\d+: [0-9A-Za-z\-\_ ]+\n"
METRICFF_PLAN_REGEX = re.compile(METRICFF_PLAN_SYNTAX)

MADAGASCAR_PLAN_SYNTAX = "([0-9A-Za-z\-\_]+\([0-9A-Za-z\-\_\,]+\))+"
MADAGASCAR_PLAN_REGEX = re.compile(MADAGASCAR_PLAN_SYNTAX)

TEMP_PATH = "/tmp/"

VAL_PARAMS = "-t 0.001 -v"

def getPlan(planner, logFile):
	#Output Plan
	matches = []
	if planner in COLIN_LIKE_PLANNERS:
		matches = [COLIN_PLAN_REGEX.findall(line) for line in logFile]
	elif planner in LPG_PLANNERS:
		matches = [LPGTD_PLAN_REGEX.findall(line) for line in logFile]
	elif planner in FD_PLANNERS:
		matches = [FD_PLAN_REGEX.findall(line) for line in logFile]
		for m in matches:
			if len(m) > 0:
				m[0] = m[0].replace(" (1)", ")")
				m[0] = "(" + m[0]
	elif planner in METRICFF_PLANNERS:
		matches = [METRICFF_PLAN_REGEX.findall(line) for line in logFile]
		for m in matches:
			if len(m) > 0:
				m[0] = re.sub("\d+: ", "(", m[0])
				m[0] = m[0].replace("\n", ")")
	elif planner in MADAGASCAR_PLANNERS:
		matches = [MADAGASCAR_PLAN_REGEX.findall(line) for line in logFile]
		for m in matches:
			m[:] = [x.replace("(", " ") for x in m]
			m[:] = [x.replace(",", " ") for x in m]
			m[:] = ["(" + x for x in m]			
	else:
		print("Error: Unmatched Planner. Plans not extracted or validated.")
	
	plan = []
	for ms in matches:
		for m in ms:
			plan.append(m)
			
	return plan
			

def updateExpBase(file, new_base):
	parts = re.split('exp/', file)
	return os.path.join(new_base, parts[1])

def getPlanFilename(logFile):

	suffix_start_idx = logFile.find(AnalysisCommon.COMPRESSED_LOG_FILE_EXT)
	return logFile[:suffix_start_idx] + AnalysisCommon.PLAN_FILE_EXT	

def getLogStructure(path):
	logStructure = {}
		
	for problem in os.listdir(path):
		logStructure[problem] = {}

		logDir = os.path.join(path, problem, AnalysisCommon.OUTPUT_DIR)
		planDir = os.path.join(path, problem, AnalysisCommon.PLANS_DIR)
		
		logStructure[problem][AnalysisCommon.OUTPUT_DIR] = logDir
		logStructure[problem][AnalysisCommon.PLANS_DIR] = planDir
				
	return logStructure
	
def bufferCompressedFile(filename):
	with gzip.open(filename, 'rt') as f:
		try:
			buffer = AnalysisCommon.bufferFile(f)
		except IOError:
			print("There was an error reading %s!"%filename)
			buffer = -1
		f.close()
		
	return buffer

def writeBuffer2File(filename, buffer):
	with open(filename, 'wt') as f_out:
		for line in buffer:
			f_out.write("%s\n"%line.rstrip())
		f_out.close()
		
def writeBuffer2CompressedFile(filename, buffer):
	with gzip.open(filename, 'wt') as f_out:
		for line in buffer:
			f_out.write("%s\n"%line.rstrip())
		f_out.close()

def main(args):

	parser = argparse.ArgumentParser(description='A Python script for extracting plans from output and putting them in the plans folder, if no plan already exists.')
	parser.add_argument('path',
	                    metavar='/path/to/planner/logs/',
						type=str,
		                help='the location of the logs for a specific planner')
	parser.add_argument('-v',
						'--verbose',
						action='store_true',
						help='Show the problems that were updated')
	parser.add_argument('-o',
						'--overwrite',
						action='store_true',
						help='If a plan already exists, overwrite it')
	parser.add_argument('-s',
						'--simulate',
						action='store_true',
						help='Show what would occur, but don\'t actually update')
	parser.add_argument('--update_val', 
						metavar='/path/to/val/executable',
						nargs=1, 
						type=str,
						help='Update the log with the validation from the provided validator')
	parser.add_argument('--exp_loc', 
						metavar='/path/to/exp/construct/',
						nargs=1, 
						type=str,
						help='Update base location of exp with the new path')
	args = parser.parse_args()
	
	if not os.path.isdir(args.path):
		print("Error: %s is not a valid directory"%args.path)
		sys.exit(-1)
		
	planner = os.path.basename(os.path.normpath(args.path))
	logStructure = getLogStructure(args.path)
	print ("Fixing Plans for %s"%planner)
	for problem in logStructure:
		logPath = logStructure[problem][AnalysisCommon.OUTPUT_DIR]
		planPath = logStructure[problem][AnalysisCommon.PLANS_DIR]
		print(problem)
		existingPlans = 0
		plansWritten = 0
		plans_updated = []
		for logFile in os.listdir(logPath):
			#Obtain the plan file paths
			fullQualifiedLog = os.path.join(logPath, logFile)
			planFilename = getPlanFilename(logFile)
			fullQualifiedPlan = os.path.join(planPath, planFilename)
			fullQualifiedPlan_compressed = os.path.join(planPath, planFilename + '.gz')
			
			#Check if the current plan file is empty
			planBuffer = bufferCompressedFile(fullQualifiedPlan_compressed)
			if planBuffer == -1:
				continue #File Read Error

			#If the plan has content
			if len(planBuffer) > 0:
				existingPlans += 1
				#And we are not overwriting
				if not args.overwrite:
					continue
					
			#Read in the current logfile to get the plan
			logBuffer = bufferCompressedFile(fullQualifiedLog)
			if logBuffer == -1:
				continue #File read error
			
			if not AnalysisCommon.isProblemLog(logFile, logBuffer):
				continue
			
			plan = getPlan(planner, logBuffer)
			if len(plan) == 0:
				continue #no plan found
			
			#Write the plan file and validate if necessary
			if not args.simulate:
				#write plan to disk
				writeBuffer2File(fullQualifiedPlan, plan)
					
				if args.update_val:
					if not os.path.isfile(args.update_val[0]):
						print ("Validate command is not a file. Skipping validation...")
						continue

					domain = AnalysisCommon.getDomain(logBuffer)
					problem = AnalysisCommon.getProblem(logBuffer)
					
					if args.exp_loc[0]:
						if not os.path.isdir(args.exp_loc[0]):
							print("New base exp path invalid. Skipping validation...")
							continue
								
						domain = updateExpBase(domain, args.exp_loc[0])
						problem = updateExpBase(problem, args.exp_loc[0])
										
					val_cmd = "%s %s %s %s %s"%(args.update_val[0], VAL_PARAMS, domain, problem, fullQualifiedPlan)
					result = subprocess.run(val_cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					
					#write new val output to log file (replace old output)
					newLogBuffer = []
					for line in logBuffer:
						newLogBuffer.append(line)
						if line.lower().startswith(AnalysisCommon.PLAN_VALIDATION.lower()):
							break #Validation point found
						
					for line in result.stdout.splitlines():
						newLogBuffer.append(line)
					
					writeBuffer2CompressedFile(fullQualifiedLog, newLogBuffer)
				#compress plan and delete file
				writeBuffer2CompressedFile(fullQualifiedPlan_compressed, plan)
				os.remove(fullQualifiedPlan)
				
			plans_updated.append(logFile)
			plansWritten += 1
			
		print("\t%i plans written"%plansWritten)
		if args.overwrite:
			print("\t%i were existing and overwritten"%existingPlans)
		else:
			print("\t%i were existing and skipped"%existingPlans)
		if (args.verbose):
			print("\tPlans written for:")
			for prob in plans_updated:
				print("\t%s"%prob)
				
			

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])
