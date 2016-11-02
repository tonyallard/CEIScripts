#! /usr/bin/python
#Author: Tony Allard
#Date: 02 Nov 2016
#Description: Selects a random x number of specific problems from a set.

import sys
import os
import random
from shutil import move

def getCargoNum(filename):
	return int(filename.split("-")[4])

def getProblemNum(filename):
	return int(filename.split("-")[5])

def main (args):
	maxProblems = int(args[0])
	maxCargo = int(args[1])
	numProblems = int(args[2])
	problemPath = args[3]
	movePath = args[4]

	#Initialise Data Structure
	problemSets = {}
	for x in range(0, maxCargo):
		problemSets[x+1] = {}
		for y in range(0, maxProblems):
			problemSets[x+1][y] = []

	#Populate Problems
	for filename in os.listdir(problemPath):
		cargo = getCargoNum(filename)
		problemNum = getProblemNum(filename)
		problemSets[cargo][problemNum].append(filename)

	#Select Problem Instances
	selected = []
	for x in range(0, maxCargo):
		result = random.sample(problemSets[x+1], numProblems)
		for y in result:
			for instance in problemSets[x+1][y]:
				#Move problem
				try:
					move(problemPath+instance, movePath+instance)
				except IOError:
					print "There was an error moving %s"%instance
					return



#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])