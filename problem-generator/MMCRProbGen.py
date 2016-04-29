#! /usr/bin/python

#Provides all the helper methods for creating MMCR Problems

import sys
import random
import dijkstra
from RouteSearch import BreadthFirst

def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b

def parseArgs(args, argsDesc):
	if (len(args) != len(argsDesc)):
		print "Error: Incorrect number of arguments. Requires %i given %i."%(len(argsDesc), len(args))
		raise SyntaxError
	i = 0
	params = dict()
	for x in args:
		try:
			if isint(x):
				params[argsDesc[i]] = int(x)
			elif isfloat(x):
				params[argsDesc[i]] = float(x)
			else:
				params[argsDesc[i]] = str(x)
		except ValueError:
			print "Error reading parameter %i with value of %s" %(i, argName[i])
			raise SyntaxError
		i+=1
	return params

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
			sect["loc"].append(loc)
			locations.append(loc)
			connectivityMap[loc] = {}

		#Add sector to list
		sectors.append(sect)
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
			s["veh"].append(veh)
			vehicles.append(veh)
			#Add Cost
			pddl.append("(= (cost %s) %i)" %(veh, cost))
			#Make Available
			pddl.append("(available %s)" %veh)
			#Make Ready
			pddl.append("(ready-loading %s)" %veh)
			#Add to Sector
			i = 0
			for l in s["loc"]:
				#Add load / unload times
				pddl.append("(= (load-time %s %s) %i)" %(veh, l, loadTime))
				pddl.append("(= (unload-time %s %s) %i)" %(veh, l, unloadTime))
				#Add Travel Times
				for d in s["loc"][i+1:]:
					pddl += linkLocations(l, d, veh, connectivityMap, travelTime)
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
		cargoes.append(car)
		#Add Size
		pddl.append("(= (size %s) %i)" %(car, size))
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
		pddl.append("(at %s %s)"%(c, origin))
		goals.append("(at %s %s)"%(c, destination))
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
			pddl.append("(at %s %s)"%(v, origin))
	return pddl, vehicleOriginMap

def linkLocations (loc1, loc2, vehicle, connectivityMap, travelTime, bridge=False, loadTime=0, unloadTime=0):
	pddl = []
	pddl.append("(= (travel-time %s %s %s) %i)" %(vehicle, loc1, loc2, travelTime))
	pddl.append("(= (travel-time %s %s %s) %i)" %(vehicle, loc2, loc1, travelTime))
	#Add conectivity
	connectivityMap[loc1][loc2] = [travelTime]
	connectivityMap[loc2][loc1] = [travelTime]
	if (bridge):
		connectivityMap[loc1][loc2].append(loadTime)
		connectivityMap[loc1][loc2].append(unloadTime)
		connectivityMap[loc2][loc1].append(loadTime)
		connectivityMap[loc2][loc1].append(unloadTime)
	return pddl

def linkSectors(sect1, sect2, connectivityMap, travelTime, loadTime, unloadTime):
	pddl = []
	#Randomly select a location to link
	loc1 = random.choice(sect1["loc"])
	loc2 = random.choice(sect2["loc"])
	#link sectors
	for v in (sect1["veh"] + sect2["veh"]):
		pddl += linkLocations(loc1, loc2, v, connectivityMap, travelTime, True, loadTime, unloadTime)

	#add load and unload times
	for v in sect1["veh"]:
		pddl.append("(= (load-time %s %s) %i)" %(v, loc2, loadTime))
		pddl.append("(= (unload-time %s %s) %i)" %(v, loc2, unloadTime))
	for v in sect2["veh"]:
		pddl.append("(= (load-time %s %s) %i)" %(v, loc1, loadTime))
		pddl.append("(= (unload-time %s %s) %i)" %(v, loc1, unloadTime))
	return pddl

def isVehicleAtLocation(location, vehicleOriginMap):
	for v in vehicleOriginMap:
		if vehicleOriginMap[v] == location:
			return True
	return False

def isBridgeLocation(location, bridgeLocations):
	if location in bridgeLocations:
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
		route = BreadthFirst.search(origin, destination, connectivityMap)
		minWindow = route.cost
		#Remove supurfulous load/unload if traversed a bridge
		#in the final leg of the journey
		if route.fromBridge:
			minWindow -= loadTime + unloadTime
		
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
			pddl.append("(available %s)"%c)
		else:
			pddl.append("(at %f (available %s))"%(windowStart, c))
		pddl.append("(at %f (not (available %s)))"%(windowEnd, c))
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