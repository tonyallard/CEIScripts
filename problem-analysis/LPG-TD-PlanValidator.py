#!/usr/bin/python
import sys
import os
import re
import gzip
import subprocess

import AnalysisCommon

PROBLEM_PATH = "/mnt/data/problem-sets/[A-Za-z0-9\-_]+/[A-Za-z0-9\-_]+\.[pPdDlL]{4}"

ACTION_TIME = "[0-9]+\.[0-9]+\:"
ACTION_INSTANCE = "\([A-Za-z0-9\-_ ]+\)"
ACTION_DURATION = "\[D:[0-9]+\.[0-9]+"
DECIMAL_NUMBER = "[0-9]+\.[0-9]+"

OUTPUT_FOLDER = "output"
PLANS_FOLDER = "plans"

DEFAULT_TMP_PATH = "/tmp/"
DEFAULT_LOG_PATH = "."

SKIPPED_PROBLEMS = ["utms-flaw", "utms", "driverlogshift", "mmcr-no-tw", "mmcr"]

def replacePath(path):
	path = path.replace("-300", "")
	path = path.replace("-150", "")
	path = path.replace("-timewindows", "")
	path = path.replace("-problems", "")
	path = path.replace("sat", "satellite")
	path = path.replace("pipes", "pipesworld")
	return path

def getParameters(problemDir, logDir):
	params = []
	for root, dirs, files in os.walk(os.path.join(problemDir, OUTPUT_FOLDER)):
		for file in files:
			domain = ""
			problem = ""
			try:
				with gzip.open(os.path.join(root, file), 'rb') as f:
					buffer = AnalysisCommon.bufferFile(f)
					probFiles = re.findall(PROBLEM_PATH, buffer[1])
					domain = replacePath(probFiles[0])
					problem = replacePath(probFiles[1])
					planFile = os.path.join(problemDir, PLANS_FOLDER, file.replace("txt", "plan"))
					logFile = os.path.join(logDir, file.replace(".gz", ""))
					params.append(tuple([domain, problem, planFile, logFile]))
			except IOError:
				continue
		return params

def createTempFile(solution, tempDir, logFile):
	tmp_filename = os.path.join(tempDir, os.path.basename(solution[:-3]))
	try:
		with gzip.open(solution, 'rb') as f:
			buffer = AnalysisCommon.bufferFile(f)
			if len(buffer) == 0:
				return -1
			f = open(tmp_filename, 'w', 0)
			firstLine = True
			epoch = 0.0001
			epsilon = epoch
			for line in buffer:
				actionTime = re.findall(ACTION_TIME, line)
				if len(actionTime) != 1:
					raise RuntimeError("Error! Multiple action times found: %s"%actionTime)
				actionTime = re.findall(DECIMAL_NUMBER, actionTime[0])
				if len(actionTime) != 1:
					raise RuntimeError("Error! Multiple action times found: %s"%actionTime)
				actionTime = float(actionTime[0])
				if not firstLine:
					actionTime += epsilon
					epsilon += epoch

				actionInstance = re.findall(ACTION_INSTANCE, line)
				if len(actionInstance) != 1:
					raise RuntimeError("Error! Multiple action instances found: %s"%actionInstance)
				
				actionDuration = re.findall(ACTION_DURATION, line)
				if len(actionDuration) != 1:
					raise RuntimeError("Error! Multiple action durations found: %s"%actionDuration)
				actionDuration = re.findall(DECIMAL_NUMBER, actionDuration[0])
				f.write("%0.4f: %s  [%s]\n"%(actionTime, actionInstance[0], actionDuration[0]))
				logFile.write("%0.4f: %s  [%s]\n"%(actionTime, actionInstance[0], actionDuration[0]))
				firstLine = False
			f.close()
		return tmp_filename
	except IOError:
		return -1

def validatePlan(domain, problem, plan, logFile):
	validatorExec = "/mnt/data/bin/VAL/validate"
	validatorParams = "-t 0.001 -v"
	call_args = "%s %s %s %s %s"%(validatorExec, validatorParams, domain, problem, plan)
	subprocess.call(call_args, shell=True, stdout=logFile, stderr=logFile)
	
def main (args) :
	
	solutionPath = args[0]

	logPath = DEFAULT_LOG_PATH
	if len(args) > 1:
		logPath = args[1]

	tempDir = DEFAULT_TMP_PATH
	if len(args) > 2:
		tempDir = args[2]

	problemDomains = {}
	for root, dirs, files in os.walk(solutionPath):
		for directory in dirs:
			if directory in SKIPPED_PROBLEMS:
				continue
			#make log directory
			logDir = os.path.join(logPath, directory)
			if not os.path.exists(logDir):
				os.makedirs(logDir)

			problemDir = os.path.join(solutionPath, directory)
			problemDomains[directory] = getParameters(problemDir, logDir)
		break
	
	for domain in problemDomains:
		print domain
		for solution in problemDomains[domain]:
			logFile = open(solution[3], 'w', 0)
			tmpPlanPath = createTempFile(solution[2], tempDir, logFile)
			if tmpPlanPath is not -1:

				validatePlan(solution[0], solution[1], tmpPlanPath, logFile)
				os.remove(tmpPlanPath)
			logFile.close()


#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])