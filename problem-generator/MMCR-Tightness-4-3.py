#! /usr/bin/python
#Author: Tony Allard
#Date: 14 May 2016
#Description: A Python script for generating random the MMCR problems as described below

#Usage: MMCR-4-3-2.py MaxCargo NumProblems

#Four clusters, three locations per cluster, and two vehicles per cluster.
#Clusters are laid out in the following fashion
#
#        O
#       / \
#	O   O
#	 \ /	
#	  O
#
#Script generates as many problems as given via an argument for the script. 
#Problems are generated by sampling num cargo between 1 and MaxCargo argument. 
#Cargo origin and desitnation are randomly sampled from all locations, vehicle 
#origin are also randomly sampled from locations within their cluster. Time 
#windows are sampled from ...
#Capacity is sampled from between 1 and max(1, maxCargo / 2)
#Load/Unlaod and travel times are fixed at 2
#Vehicle Utilisation cost is uniform at 2
#Cargo Size is defaulted to 1

#! /usr/bin/python
import sys
import os
import random
import MMCRProbGen

def parseArgs(args):
	argName = ("Max Cargo", "Max Tightness", "Num Problems", "Path")
	if (len(args) != 4):
		print "Error: Incorrect number of arguments."
		raise SyntaxError
	i = 0
	params = dict()
	for x in args[:-1]:
		try:
			params[i] = int(x)
		except ValueError:
			print "Error: %s must be an integer" %argName[i]
			raise SyntaxError
		i+=1
	params[len(args)-1]=str(args[-1])
	return params

def printUsage(name):
	print "Multi-Modal Cargo Routing (MMCR) Problem Generator"
	print "By releasing this code we imply no warranty as to its reliability and its use is entirely at your own risk.\n"
	print "Usage " + name + " maxCargo maxTightness maxTightness numProblems\n"
	print "Example: " + name + " 3 2 100 /Path/To/Problems"

def linkSectors(sectors, travelTime, loadTime, unloadTime, connectivityMap):
	pddl = []
	#link sectors 0 and 1
	pddl += MMCRProbGen.linkSectors(sectors[0], sectors[1], travelTime, loadTime, unloadTime, connectivityMap)
	#link sectors 0 and 2
	pddl += MMCRProbGen.linkSectors(sectors[0], sectors[2], travelTime, loadTime, unloadTime, connectivityMap)
	#link sectors 1 and 3
	pddl += MMCRProbGen.linkSectors(sectors[1], sectors[3], travelTime, loadTime, unloadTime, connectivityMap)
	#link sectors 2 and 3
	pddl += MMCRProbGen.linkSectors(sectors[2], sectors[3], travelTime, loadTime, unloadTime, connectivityMap)
	return pddl

def main(args):
	DEFAULT_CARGO_SIZE = 1
	DEFAULT_TRAVEL_TIME = 2
	DEFAULT_LOAD_TIME = 2
	DEFAULT_UNLOAD_TIME = 2
	DEFAULT_COST = 2
	
	output = []
	params = dict()
	try:
		params = parseArgs(args[1:])
	except:
		printUsage(args[0])
		sys.exit(1)

	numProblems = params[2]
	maxCargo = params[0]
	maxTightness = params[1]
	path = params[3]
	
	for p in range(0, numProblems):
		#Sample max Cargo
		numCargo = random.randint(1, maxCargo)
		capacityRange = numCargo * DEFAULT_CARGO_SIZE
		numVehicles = numCargo
		tightness = random.randint(1, maxTightness)
		#Create 4 Sectors, three locations per sector
		sectors, locations, connectivityMap, pddl = MMCRProbGen.createSectors(4, 3, capacityRange, False)

		#Create the number of vehicles per sector as there are cargo
		vehicles, pddl2 = MMCRProbGen.createVehicles(sectors, numVehicles, connectivityMap, capacityRange, DEFAULT_TRAVEL_TIME, DEFAULT_LOAD_TIME, DEFAULT_UNLOAD_TIME, DEFAULT_COST, False)
		pddl+=pddl2

		#link sectors
		pddl += linkSectors(sectors, DEFAULT_TRAVEL_TIME, DEFAULT_LOAD_TIME, DEFAULT_UNLOAD_TIME, connectivityMap)

		#Create Cargo
		cargoes, pddl2 = MMCRProbGen.createCargo(numCargo, DEFAULT_CARGO_SIZE)
		pddl += pddl2

		#randomly select vehicle origin
		pddl += MMCRProbGen.getVehicleOrigin(vehicles, sectors)

		#randomly select origin and destination for for cargoes
		goals, deliveryInfo, pddl2 = MMCRProbGen.getCargoLocations(cargoes, locations)
		pddl += pddl2

		#Create Random Time Windows
		pddl += MMCRProbGen.determineTimeWindows(deliveryInfo, connectivityMap, DEFAULT_TRAVEL_TIME, tightness, False)

		#Save problem to file
		name = "Prob-%i-%i-%i-%i-%i-%i"%(len(sectors), len(locations), len(vehicles), len(cargoes), tightness, p)
		MMCRProbGen.saveProblem(path+name, locations, vehicles, cargoes, pddl, goals)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)