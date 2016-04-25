#!usr/bin/python
#Author: Tony Allard
#Date: 14 May 2014
#Description: A Python script for running experiments on the YAHSP Planner

from time import strftime
from timeit import timeit
from subprocess import call
import os

#-------------------------------Global Constants------------------------------#

NOW = strftime("%Y%m%d_%H:%M:%S") #Now

ROOT_FOLDER=".." #Root Folder

#Location of log files
SYS_LOG_FILE_NAME = NOW + "_YAHSP_SYS_LOG.log"
EXP_LOG_FILE_NAME = NOW + "_YAHSP_EXP_LOG.csv"
OUTPUT_LOC = ROOT_FOLDER + "/exp-output/yahsp"
SYS_LOG_FILE_LOC = OUTPUT_LOC + "/" + SYS_LOG_FILE_NAME
EXP_LOG_FILE_LOC = OUTPUT_LOC + "/" + EXP_LOG_FILE_NAME

#Location of input files
PDDL_FILE_LOC = ROOT_FOLDER + "/PDDL/6-No-Fluents-Or-Durative-Actions-Or-TILs"
DOMAIN_FILE= PDDL_FILE_LOC + "/LogisticsDomain.pddl"

#Location of Planner
PLANNER_LOC = ROOT_FOLDER + "/Planners/YAHSP"
PLANNER = PLANNER_LOC + "/yahsp"

#---------------------------------Functions----------------------------------#

#Function to run planner on problem for a number of iterations
def runProblemTest(planner, domain, problem, problemName, iterations):
	expFile.write(problemName + " ")
	call_arguments = """[
        '%s',
        '%s', '%s'], # pass additional parameters by adding elements to this list
        stdout=stdout,
        stderr=stderr
	""" % (planner, domain, problem)

	time_taken = timeit(stmt = "subprocess.call(%s)" % call_arguments,
		    setup = """import subprocess;
from __main__ import sysFile
stdout = sysFile;
stderr = sysFile
""", number = iterations) * 1000 #convert to ms
	expFile.write(str(time_taken) + " ")
	avgSolveTime = time_taken / iterations
	expFile.write(str(avgSolveTime) + "\n");
	return avgSolveTime

def runPlannerTest(planner, domain, problemLocation, iterations):
	totalSolveTime = 0	
	for problemName in os.listdir(problemLocation):
		if (problemName.startswith("p") and problemName.endswith(".pddl")):
			sysFile.write("---------------Problem " + problemName + "---------------\n")	
			problemFile = problemLocation + "/" + problemName
			avgSolveTime = runProblemTest(planner, domain, problemFile, problemName, iterations)
			sysFile.write("Average Solve Time: " + str(avgSolveTime) + "ms\n");
			totalSolveTime += avgSolveTime
	return totalSolveTime

#-----------------------------------Main function--------------------------------#
#Open Output Files
expFile = open(EXP_LOG_FILE_LOC, 'a')
expFile.write('"Problem Name" "Total Time" "Average Time"\n')
sysFile = open(SYS_LOG_FILE_LOC, 'a')
#Run experiment
sysFile.write("--------------Begin Experiment---------------\n")
totalSolveTime = runPlannerTest(PLANNER, DOMAIN_FILE, PDDL_FILE_LOC, 10)
sysFile.write("Total Solve Time: " + str(totalSolveTime) + "ms\n")
sysFile.write("--------------End Experiment---------------\n")
sysFile.close()
expFile.close()
print "Time Taken: " + str(os.times())
