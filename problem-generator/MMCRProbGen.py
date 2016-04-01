#! /usr/bin/python

#Provides all the helper methods for creating MMCR Problems

import sys
import random
import dijkstra

def parseArgs(args):
	argName = ("Number of Sectors", "Locations per Sector", "Vehicles per Sector", "Number of Cargo in Problem", "Number of Problems")
	if (len(args) != 5):
		print "Error: Incorrect number of arguments."
		raise SyntaxError
	i = 0
	params = dict()
	for x in args:
		try:
			params[i] = int(x)
		except ValueError:
			print "Error: %s must be an integer" %argName[i]
			raise SyntaxError
		i+=1
	return params

def printUsage(name):
	print "Multi-Modal Cargo Routing (MMCR) Problem Generator"
	print "By releasing this code we imply no warranty as to its reliability and its use is entirely at your own risk.\n"
	print "Usage " + name + " numSectors locationsPerSector vehiclesPerSector numCargoes numProblems\n"
	print "Example: " + name + " 2 3 1 2 100"

def createSectors(numSectors, numLocations):
	locCount = 0
	sectors = []
	pddl = []
	locations = []
	connectivityMap = {}
	#creat
	for s in range(0, numSectors):
		#Create Sector
		sect = {}
		sect["loc"] = []
		for l in range(0, numLocations):
			#Create Location
			loc = "L" + str(locCount)
			locCount += 1
			sect["loc"] += [loc]
			locations += [loc]
			connectivityMap[loc] = {}
			
		sectors += [sect]
	return sectors, locations, connectivityMap, pddl

def addLocationCapacity(locations, maxCapactiy, sampleCapacity=False):
	pddl = []
	for l in locations:
		lCap = maxCapactiy
		if sampleCapacity:
			#Add Sampled Capacity
			lCap = random.randint(1, maxCapactiy)
		pddl.append("(= (remaining-capacity %s) %i)" %(l, lCap))
	return pddl

def createVehicles(sectors, numVehicles, connectivityMap, travelTime, loadTime, unloadTime, cost):
	vehCount = 0
	pddl = []
	vehicles = []
	for s in sectors:
		s["veh"] = []
		for v in range(0, numVehicles):
			#Create Vehicle
			veh = "V" + str(vehCount)
			vehCount+=1
			s["veh"] += [veh]
			vehicles += [veh]
			#Add Cost
			pddl += ["(= (cost %s) %i)" %(veh, cost)]
			#Make Available
			pddl += ["(available %s)" %veh]
			#Make Ready
			pddl += ["(ready-loading %s)" %veh]
			#Add to Sector
			i = 0
			for l in s["loc"]:
				#Add load / unload times
				pddl += ["(= (load-time %s %s) %i)" %(veh, l, loadTime)]
				pddl += ["(= (unload-time %s %s) %i)" %(veh, l, unloadTime)]
				#Add Travel Times
				for d in s["loc"][i+1:]:
					pddl += linkLocations(l, d, veh, travelTime)
					#Add conectivity
					connectivityMap[l][d] = travelTime
					connectivityMap[d][l] = travelTime
				i+=1
	return vehicles, pddl

def addVehicleCapacity(vehicles, maxCapactiy, sampleCapacity=True):
	pddl = []
	for v in vehicles:
		vCap = maxCapactiy
		if sampleCapacity:
			#Add Sampled Capacity
			vCap = random.randint(1, maxCapactiy)
		pddl.append("(= (remaining-capacity %s) %i)" %(v, vCap))
	return pddl

def createCargo(numCargo, size):
	cargoes = []
	carCount = 0
	pddl = []
	for c in range(0, numCargo):
		#Create Cargo
		car = "C" + str(carCount)
		carCount+=1
		cargoes += [car]
		#Add Size
		pddl += ["(= (size %s) %i)" %(car, size)]
	return cargoes, pddl

def getRandomCargoLocations(cargoes, locations):
	pddl = []
	goals = []
	deliveryInfo = {}
	for c in cargoes:
		origin = random.choice(locations)
		destination = random.choice(locations)
		while (destination == origin):
			destination = random.choice(locations)
		pddl += ["(at %s %s)"%(c, origin)]
		goals += ["(at %s %s)"%(c, destination)]
		deliveryInfo[c] = [origin, destination]
	return goals, deliveryInfo, pddl

def getCargoLocations(cargo, originSect, destSect):
	pddl = []
	goals = []
	deliveryInfo = {}
	origin = random.choice(originSect["loc"])
	destination = random.choice(destSect["loc"])
	pddl = ["(at %s %s)"%(cargo, origin)]
	goals = ["(at %s %s)"%(cargo, destination)]
	deliveryInfo[cargo] = [origin, destination]
	return goals, deliveryInfo, pddl

def getVehicleOrigin(vehicles, sectors):
	pddl = []
	vehicleOriginMap = {}
	for s in sectors:
		for v in s["veh"]:
			origin = random.choice(s["loc"])
			vehicleOriginMap[v] = origin
			pddl += ["(at %s %s)"%(v, origin)]
	return pddl, vehicleOriginMap

def linkLocations (loc1, loc2, vehicle, travelTime):
	pddl = []
	pddl += ["(= (travel-time %s %s %s) %i)" %(vehicle, loc1, loc2, travelTime)]
	pddl += ["(= (travel-time %s %s %s) %i)" %(vehicle, loc2, loc1, travelTime)]
	return pddl

def linkSectors(sect1, sect2, travelTime, loadTime, unloadTime, connectivityMap):
	pddl = []
	#Randomly select a location to link
	loc1 = random.choice(sect1["loc"])
	loc2 = random.choice(sect2["loc"])
	#link sectors
	for v in (sect1["veh"] + sect2["veh"]):
		pddl += linkLocations(loc1, loc2, v, travelTime)
		#create dummy locations to take load/unload into account
		loc1_a = loc1 + "-%i"%len(connectivityMap)
		loc2_a = loc2 + "-%i"%len(connectivityMap)
		connectivityMap[loc1_a] = {}
		connectivityMap[loc2_a] = {}
		connectivityMap[loc1][loc1_a] = loadTime
		connectivityMap[loc1_a][loc1] = unloadTime
		connectivityMap[loc1_a][loc2_a] = travelTime
		connectivityMap[loc2_a][loc1_a] = travelTime
		connectivityMap[loc2][loc2_a] = loadTime
		connectivityMap[loc2_a][loc2] = unloadTime
	#add load and unload times
	for v in sect1["veh"]:
		pddl += ["(= (load-time %s %s) %i)" %(v, loc2, loadTime)]
		pddl += ["(= (unload-time %s %s) %i)" %(v, loc2, unloadTime)]
	for v in sect2["veh"]:
		pddl += ["(= (load-time %s %s) %i)" %(v, loc1, loadTime)]
		pddl += ["(= (unload-time %s %s) %i)" %(v, loc1, unloadTime)]
	return pddl

def isVehicleAtLocation(location, vehicleOriginMap):
	for v in vehicleOriginMap:
		if vehicleOriginMap[v] == location:
			return True
	return False

def determineTimeWindows(deliveryInfo, connectivityMap, vehicleOriginMap, travelTime, loadTime, unloadTime, tightness, sampleStartTime=True, sampleEndTime=True, useShortestPrePosition=True):
	pddl = []
	#Iterate through deliveries
	for c in deliveryInfo:
		origin = deliveryInfo[c][0]
		destination = deliveryInfo[c][1]
		#solve prePosition Problem
		isVehicleAtOrigin = isVehicleAtLocation(origin, vehicleOriginMap)
		prePositionTime = travelTime
		if isVehicleAtOrigin and useShortestPrePosition:
			prePositionTime = 0

		#Solve Delivery Problem
		#This includes load/unload times for cargo
		#exchange because of how the connectivity map is built
		#build network
		g = dijkstra.Graph()
		for l in connectivityMap:
			if g.get_vertex(l) == None:
				g.add_vertex(l)
			for d in connectivityMap[l]:
				if g.get_vertex(d) == None:
					g.add_vertex(d)
				#Add weights
				g.add_edge(l, d, connectivityMap[l][d])

		#Solve shortest path for cargo delivery
		dijkstra.dijkstra(g, g.get_vertex(origin), g.get_vertex(destination))
		target = g.get_vertex(destination)
		path = [target.get_id()]
		dijkstra.shortest(target, path)
		minWindow = target.get_distance()
		
		#Add time for pre-position
		#and for inital load and final unload
		minWindow += prePositionTime + loadTime + unloadTime
		
		#Determine time window
		windowStart = 0
		if sampleStartTime:
			windowStart = random.uniform(0, minWindow/2.0)
		windowEnd = windowStart+(tightness*minWindow)
		if sampleEndTime:
			windowEnd = random.uniform(windowStart+minWindow, windowStart+(tightness*minWindow))
		if windowStart == 0:
			pddl += ["(available %s)"%c]
		else:
			pddl += ["(at %f (available %s))"%(windowStart, c)]
		pddl += ["(at %f (not (available %s)))"%(windowEnd, c)]
	return pddl

def saveProblem(name, locations, vehicles, cargoes, pddl, goals):
	probName = name.split("/")[-1]
	fileName = "".join([name, ".pddl"])
	print fileName
	f = open(fileName, 'w')
	#Write header
	f.write("(define (problem %s)\n"%probName)
	f.write("\t(:domain multi-modal-cargo-routing)\n")
	f.write("\t(:objects\n")
	#Write vehicle objs
	f.write("\t\t")
	for v in vehicles:
		f.write("%s "%v)
	f.write("- VEHICLE\n")
	#Write location objs
	f.write("\t\t")
	for l in locations:
		f.write("%s "%l)
	f.write("- LOCATION\n")
	#Write cargo objs
	f.write("\t\t")
	for c in cargoes:
		f.write("%s "%c)
	f.write("- CARGO\n")
	f.write("\t)\n")
	#Write initial state
	f.write("\t(:init\n")
	for line in pddl:
		f.write("\t\t%s\n"%line)
	f.write("\t)\n")
	#write goal
	f.write("\t(:goal")
	if (len(goals) > 1):
		f.write(" (and\n")
	else:
		f.write("\n")
	for g in goals:
		f.write("\t\t%s\n"%g)
	if (len(goals) > 1):
		f.write("\t))\n")
	else:
		f.write("\t)\n")
	#Write metric
	f.write("\t(:metric minimize (total-cost))\n")
	f.write(")")
	f.close