#! /usr/bin/python
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

def createSectors(numSectors, numLocations, maxCapactiy, sampleCapacity=True):
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
			lCap = maxCapactiy
			if sampleCapacity:
				#Add Sampled Capacity
				lCap = random.randint(1, maxCapactiy)
			pddl += ["(= (remaining-capacity %s) %i)" %(loc, lCap)]
		sectors += [sect]
	return sectors, locations, connectivityMap, pddl

def createVehicles(sectors, numVehicles, connectivityMap, maxCapactiy, travelTime, loadTime, unloadTime, cost, sampleCapacity=True):
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
			vCap = maxCapactiy
			if sampleCapacity:
				#Add Sampled Capacity
				vCap = random.randint(1, maxCapactiy)
			pddl += ["(= (remaining-capacity %s) %i)" %(veh, vCap)]
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

def getCargoLocations(cargoes, locations):
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

def getVehicleOrigin(vehicles, sectors):
	pddl = []
	for s in sectors:
		for v in s["veh"]:
			origin = random.choice(s["loc"])
			pddl += ["(at %s %s)"%(v, origin)]
	return pddl

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

def determineTimeWindows(deliveryInfo, connectivityMap, travelTime, tightness, sampleStartTime=True):
	pddl = []
	#Iterate through deliveries
	for c in deliveryInfo:
		origin = deliveryInfo[c][0]
		destination = deliveryInfo[c][1]

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
		#Add time for possible pre-position
		minWindow += travelTime
		#Determine time window
		windowStart = 0
		if sampleStartTime:
			windowStart = random.randint(0, minWindow/2)
		windowEnd = random.randint(windowStart+minWindow, windowStart+(tightness*minWindow))
		if windowStart == 0:
			pddl += ["(available %s)"%c]
		else:
			pddl += ["(at %i (available %s))"%(windowStart, c)]
		pddl += ["(at %i (not (available %s)))"%(windowEnd, c)]
	return pddl

def saveProblem(name, locations, vehicles, cargoes, pddl, goals):
	fileName = "".join([name, ".pddl"])
	f = open(fileName, 'w')
	#Write header
	f.write("(define (problem %s)\n"%name)
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

def main(args):
	DEFAULT_CAPACITY = 3
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

	#Create Sectors
	sectors, locations, connectivityMap, pddl = createSectors(params[0], params[1], DEFAULT_CAPACITY)
	output += pddl

	#Create Vehicles
	vehicles, pddl2 = createVehicles(sectors, params[2], connectivityMap, DEFAULT_CAPACITY, DEFAULT_TRAVEL_TIME, DEFAULT_LOAD_TIME,	DEFAULT_UNLOAD_TIME, DEFAULT_COST)
	pddl+=pddl2

	#Create Cargo
	cargoes, pddl2 = createCargo(params[3], DEFAULT_CARGO_SIZE)
	pddl += pddl2

	#randomly select vehicle origin
	pddl += getVehicleOrigin(vehicles, sectors)

	#randomly select origin and destination for for cargoes
	goals, deliveryInfo, pddl2 = getCargoLocations(cargoes, locations)
	pddl += pddl2

	#Need to pick random time windows

	print "\n".join(pddl)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)