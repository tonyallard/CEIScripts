#! /usr/bin/python
#Author: Tony Allard
#Date: 14 Mar 2016
#Description: A Python script for generating MMCR problems which enumerate 
#the tightness of time windows as described below.

#Usage: MMCR-Tightness-Geom-Fixed-4-3-1-4.py maxTightness numProblems numGeom /Path/To/Problems
#
#Four clusters, three locations per cluster, and one vehicle per cluster.
#Clusters are laid out in the following fashion
#
#     0
#    / \
#	1   2
#	 \ /	
#	  3
#
#Script generates as many problems as given via the arguments for the script.
#For example, if 100 problems were specified with a geometric enumeration of 4,
#400 problems would result.
#
#There are four cargo items resulting in deliveries requiring concurrency.
#Two items originate in cluster 0 and are required to be delivered to
#cluster 2 and 3, another item originates in cluster 2 and must be delivered 
#to cluster 3 and the last originates in cluser 1 and must be delivered to 
#cluster 0. Note: Cargo Locations are randomly selected from within the cluster.

#Vehicle origin is randomly sampled from locations within their cluster. 
#Time windows all start from zero, thereby increasing the possibility of 
#concurrency within the problems, as all delivery problems must be solved at once.
#The end of the time windows are generated by 2 * minimum estimated delivery 
#(as calculated by a dijkstras algorithm), decreasing following a geometic 
#sequence.
#
#Number of vehicles are fixed at 1 vehicles per cluster.
#Capacity is fixed to the number of cargo items, to effectively ensure 
#capacity constraints are not part of the problem, we are only interested in 
#testing the planners performance on time window concurrency.
#Load/Unlaod and travel times are fixed at 2
#Vehicle Utilisation cost is uniform at 2
#Cargo Size is defaulted to 1
#
#NOTE: The location layout remains the same for each problem it is randomly
#generated once. Vehicle initial locations are sampled uniformly from this 
#network.
#Cargo delivery is also fixed for this problem for specific sectors. 
#Locations within those sectors are sampled for each problem.
#


#! /usr/bin/python
import sys
import os
import random
import MMCRProbGen

def parseArgs(args):
	argName = ("Max Tightness", "Num Problems", "Max Geometric Enumerations", "Path")
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
	print "Usage " + name + " maxTightness numProblems numGeom pathToProblems\n"
	print "Example: " + name + " 3 100 5 /Path/To/Problems"

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

	numProblems = params[1]
	maxTightness = params[0]
	maxGeom = params[2]
	path = params[3]

	numSectors = 4
	numLocations = 3
	numVehicles = 1
	numCargo = 4
	
	#Create Fixed Problem
	capacityRange = numCargo * DEFAULT_CARGO_SIZE
	#Create 4 Sectors, three locations per sector
	sectors, locations, connectivityMap, initPDDL = MMCRProbGen.createSectors(numSectors, numLocations)
	initPDDL += MMCRProbGen.addLocationCapacity(locations, capacityRange)
	#Create one vehicle per sector
	vehicles, pddl2 = MMCRProbGen.createVehicles(sectors, numVehicles, connectivityMap, DEFAULT_TRAVEL_TIME, DEFAULT_LOAD_TIME, DEFAULT_UNLOAD_TIME, DEFAULT_COST)
	initPDDL+=pddl2
	initPDDL += MMCRProbGen.addVehicleCapacity(vehicles, capacityRange)

	#link sectors
	initPDDL += linkSectors(sectors, DEFAULT_TRAVEL_TIME, DEFAULT_LOAD_TIME, DEFAULT_UNLOAD_TIME, connectivityMap)
	
	#Create Cargo
	cargoes, pddl2 = MMCRProbGen.createCargo(numCargo, DEFAULT_CARGO_SIZE)
	initPDDL += pddl2

	#Create sampled problems	
	for p in range(0, numProblems):

		pddl = []
		pddl += initPDDL

		#randomly select vehicle origin
		pddl2, vehicleOriginMap = MMCRProbGen.getVehicleOrigin(vehicles, sectors)
		pddl += pddl2

		#select origin and destination for for cargoes
		goals = []
		deliveryInfo = {}
		
		goals2, deliveryInfo2, pddl2 = MMCRProbGen.getCargoLocations(cargoes[0], sectors[0], sectors[3])
		goals += goals2	
		deliveryInfo = dict(deliveryInfo.items() + deliveryInfo2.items())	
		pddl += pddl2
		goals2, deliveryInfo2, pddl2 = MMCRProbGen.getCargoLocations(cargoes[1], sectors[0], sectors[2])
		goals += goals2	
		deliveryInfo = dict(deliveryInfo.items() + deliveryInfo2.items())	
		pddl += pddl2
		goals2, deliveryInfo2, pddl2 = MMCRProbGen.getCargoLocations(cargoes[2], sectors[2], sectors[3])
		goals += goals2	
		deliveryInfo = dict(deliveryInfo.items() + deliveryInfo2.items())	
		pddl += pddl2
		goals2, deliveryInfo2, pddl2 = MMCRProbGen.getCargoLocations(cargoes[3], sectors[1], sectors[0])
		goals += goals2	
		deliveryInfo = dict(deliveryInfo.items() + deliveryInfo2.items())	
		pddl += pddl2
		
		#Determine time windows using geometric sequence
		for seq in range(0, maxGeom):
			pddl2 = []
			pddl2 += pddl		
			tightness = 1 + ((maxTightness - 1) * (1.0 / (2 ** seq)))
			#Create Random Time Windows
			pddl2 += MMCRProbGen.determineTimeWindows(deliveryInfo, connectivityMap, vehicleOriginMap, DEFAULT_TRAVEL_TIME, DEFAULT_LOAD_TIME, DEFAULT_UNLOAD_TIME, tightness, False, False)

			#Save problem to file
			name = "Prob-%i-%i-%i-%i-%s-%i"%(len(sectors), len(locations), 
				len(vehicles), len(cargoes), str(tightness).replace('.', '_'), p)
			MMCRProbGen.saveProblem(path+name, locations, vehicles, cargoes, pddl2, goals)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)