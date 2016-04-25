#!usr/bin/python
from time import strftime, clock, time
from subprocess import call
import os
#-------------------------------------------------------------------#

#Initialise global constants
NOW = strftime("%Y%m%d_%H:%M:%S") #Now

ROOT_FOLDER="/home/tony/dev" #Root Folder

#Location of log files
SYS_LOG_FILE_NAME = NOW + "_COLIN_SYS_LOG.log"
EXP_LOG_FILE_NAME = NOW + "_COLIN_EXP_LOG.log"
OUTPUT_LOC = ROOT_FOLDER + "/exp-output/colin2"
SYS_LOG_FILE_LOC = OUTPUT_LOC + "/" + SYS_LOG_FILE_NAME
EXP_LOG_FILE_LOC = OUTPUT_LOC + "/" + EXP_LOG_FILE_NAME

#Location of input files
PDDL_FILE_LOC = ROOT_FOLDER + "/PDDL/1-Full-Specification"
DOMAIN_FILE= PDDL_FILE_LOC + "/LogisticsDomain.pddl"

#Location of Planner
PLANNER_LOC = ROOT_FOLDER + "/Planners/colin2/release/colin"
PLANNER = PLANNER_LOC + "/colin-clp"

#-------------------------------------------------------------------#

#Function to run planner once on problem
#Returns the time taken to solve problem
def solve(planner, domain, problem):
	start = time() #returns time since epoch in seconds (float)
	rc=call([planner, "-T", domain, problem], stdout=sysFile);
	stop = time()
	return (stop - start) * 1000

#Function to run planner on problem for a number of iterations
def runProblemTest(planner, domain, problem, iterations):
	averageSolveTime = 0
	for x in range(0, iterations):
		sysFile.write("----------Iteration " + str(x) + "----------\n")
		sysFile.flush()		
		solveTime = solve(planner, domain, problem)
		sysFile.write("Problem iteration complete. " + str(solveTime) + "ms to solve\n")
		expFile.write(str(solveTime) + "\n")
		averageSolveTime += solveTime
	averageSolveTime/=iterations
	return averageSolveTime

def runPlannerTest(planner, domain, problemLocation, iterations):
	totalSolveTime = 0	
	for problemFile in os.listdir(problemLocation):
		if (problemFile.startswith("p") and problemFile.endswith(".pddl")):
			sysFile.write("---------------Problem " + problemFile + "---------------\n")		
			expFile.write("---------------Problem " + problemFile + "---------------\n")
			problemFile = problemLocation + "/" + problemFile
			expFile.write(str(problemFile) + "\n")
			avgSolveTime = runProblemTest(planner, domain, problemFile, iterations)
			sysFile.write("Average Solve Time: " + str(avgSolveTime) + "ms\n");
			expFile.write("Average Solve Time: " + str(avgSolveTime) + "ms\n");
			totalSolveTime += avgSolveTime
	return totalSolveTime

#-------------------------------------------------------------------#
#MAIN function
expFile = open(EXP_LOG_FILE_LOC, 'a')
sysFile = open(SYS_LOG_FILE_LOC, 'a')

sysFile.write("--------------Begin Experiment---------------\n")
totalSolveTime = runPlannerTest(PLANNER, DOMAIN_FILE, PDDL_FILE_LOC, 100)
sysFile.write("Total Solve Time: " + str(totalSolveTime) + "ms\n")
expFile.write("Total Solve Time: " + str(totalSolveTime) + "ms\n")
sysFile.write("--------------End Experiment---------------\n")
sysFile.close()
expFile.close()
print os.times()

