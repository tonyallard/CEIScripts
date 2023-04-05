#! /usr/bin/python3
#Author: Tony Allard
#Date: 14 Mar 2016
#Description: A Python script for generating MMCR problems which enumerate 
#the tightness of time windows as described below.

#Usage: MMCR-Generator.py -c config.json /Path/To/Problems
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
#For example, if there is a maximum of 4 cargo deliveries with 10 problems per cargo
#with a geometric enumeration of 4, 160 problems would result.
#
#Problems are generated in bins from 1 to the max_cargo argument. 
#Cargo origin and desitnation are randomly sampled from all locations per problem. 
#Vehicle origin are also randomly sampled from locations within their cluster. 
#Time windows all start from zero, thereby increasing the possibility of 
#concurrency within the problems, as all delivery problems must be solved at once.
#The end of the time windows are generated by 2 * minimum estimated delivery 
#(as calculated by a breadth-first search algorithm), decreasing following a geometic 
#sequence.
#
#Number of vehicles are fixed at 1 vehicles per cluster.
#Capacity is fixed to the number of cargo items, to effectively ensure 
#capacity constraints are not part of the problem. We are only interested in 
#testing the planners performance on time window concurrency.
#Load/Unlaod and travel times are fixed at 2
#Vehicle Utilisation cost is uniform at 2
#Cargo Size is defaulted to 1
#
#NOTE: The location layout remains the same for each problem it is randomly
#generated once. Vehicle initial locations are sampled uniformly from this 
#network. Number of cargo and their delivery is sampled per problem
#

import sys
import os
import random
import argparse
import json
import MMCRProbGen

def linkSectors(sectors, connectivityMap, travelTime, loadTime, unloadTime):
	pddl = []
	#link sectors 0 and 1
	pddl += MMCRProbGen.linkSectors(sectors[0], sectors[1], connectivityMap, travelTime, loadTime, unloadTime)
	#link sectors 0 and 2
	pddl += MMCRProbGen.linkSectors(sectors[0], sectors[2], connectivityMap, travelTime, loadTime, unloadTime)
	#link sectors 1 and 3
	pddl += MMCRProbGen.linkSectors(sectors[1], sectors[3], connectivityMap, travelTime, loadTime, unloadTime)
	#link sectors 2 and 3
	pddl += MMCRProbGen.linkSectors(sectors[2], sectors[3], connectivityMap, travelTime, loadTime, unloadTime)
	return pddl

def main(args):
	parser = argparse.ArgumentParser(
		prog = 'Multi-Modal Cargo Routing (MMCR) Problem Generator',
		description='Generator to create a suite of MMCR problems in a specific sector setup.',
		epilog = f'Example usage: {args[0]} -c /path/to/config/file.json /path/to/folder')
	parser.add_argument('path',
	                    metavar='/path/to/folder',
						type=str,
		                help='the path to store problem pddl files')
	parser.add_argument('-c',
						'--config',
						required=True,
						type=str,
						metavar='/path/to/config/file.json',
						help='Config file that defines the problems to produce')
	
	args = parser.parse_args()

	path = os.path.dirname(args.path)
	if (len(path) and not os.path.isdir(path)):
		print("Error: {p} is not a valid path.".format(
			p = path
		))
		sys.exit(-1)
		
	if not os.path.isfile(args.config):
		print("Error: {c} is not a valid configuration file".format(
			c = args.config
		))
		sys.exit(-1)

	with open(args.config) as f:
		config = json.load(f)
	
	print("Configuration used: {cn} ({cf})".format(
		cn = config["name"],
		cf = args.config
	))
	
	
	deafult_cargo_size = config["default-cargo-size"]
	deafult_travel_time = config["default-travel-time"]
	deafult_load_time = config["default-load-time"]
	deafult_unload_time = config["default-unload-time"]
	deafult_cost = config["default-cost"]
	
	cities = config["cities"]
	locations_per_city = config["locations-per-city"]
	vehicles_per_city = config["vehicles-per-city"]
	
	num_simulations = config["num-simulations"]
	min_cargo = config["cargo"]["min"]
	max_cargo = config["cargo"]["max"]
	max_tightness = config["max-tightness"]
	max_dilation = config["dilation"]["max"]
	min_dilation = config["dilation"]["min"]
	
	#Create 4 Sectors, three locations per sector
	sectors, locations, connectivityMap, initPDDL = MMCRProbGen.createSectors(cities, locations_per_city)

	#Create one vehicle per sector
	vehicles, pddl2 = MMCRProbGen.createVehicles(sectors, vehicles_per_city, connectivityMap, deafult_travel_time, deafult_load_time, deafult_unload_time, deafult_cost)
	initPDDL += pddl2

	#link sectors
	initPDDL += linkSectors(sectors, connectivityMap, deafult_travel_time, deafult_load_time, deafult_unload_time)
	
	probNum = 0

	for c in range(min_cargo, max_cargo+1):
		#Setup num Cargo
		numCargo = c
		capacityRange = numCargo * deafult_cargo_size
		
		pddl = []
		pddl += initPDDL
		
		#Add Location Capacity
		pddl += MMCRProbGen.addLocationCapacity(locations, capacityRange)
		#Add Vehicle Capacity
		pddl += MMCRProbGen.addVehicleCapacity(vehicles, capacityRange)
	
		#Create Cargo
		cargoes, pddl2 = MMCRProbGen.createCargo(numCargo, deafult_cargo_size)
		pddl += pddl2
	
		for p in range(0, num_simulations):

			pddl2 = []
			pddl2 += pddl

			#randomly select vehicle origin
			pddl3, vehicleOriginMap = MMCRProbGen.getVehicleOrigin(vehicles, sectors)
			pddl2 += pddl3

			#randomly select origin and destination for for cargoes
			goals, deliveryInfo, pddl3 = MMCRProbGen.getRandomCargoLocations(cargoes, locations)
			pddl2 += pddl3

			for seq in range(min_dilation, max_dilation + 1):

				probNum += 1
				
				pddl3 = []
				pddl3 += pddl2		
				tightness = 1 + ((max_tightness - 1) * (1.0 / (2 ** seq)))
				#Create Random Time Windows
				pddl3 += MMCRProbGen.determineTimeWindows(deliveryInfo, connectivityMap, vehicleOriginMap, deafult_travel_time, deafult_load_time, deafult_load_time, tightness, False, False)

				#Save problem to file
				name = "Prob-%i-%i-%i-%i-%i-%s-%i"%(len(sectors), len(locations), len(vehicles), 
					len(cargoes), p, str(tightness).replace('.', '_'), probNum)
				MMCRProbGen.saveProblem(os.path.join(path,name), locations, vehicles, cargoes, pddl3, goals)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)