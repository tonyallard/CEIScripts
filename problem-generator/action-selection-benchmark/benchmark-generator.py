#!/usr/bin/python3
import sys
import os
import argparse
import json
import importlib  
n_chains = importlib.import_module("n-chains-l-length-a-dacts")

ALL_ACTION_GOAL_PARAM = ['all', 'chains_only', 'both']
AAG_TRUE = [ALL_ACTION_GOAL_PARAM[0], ALL_ACTION_GOAL_PARAM[2]]
AAG_BOTH = ALL_ACTION_GOAL_PARAM[2]

TIME_WINDOW = "time-window"
NUM_CHAINS = "num-chains"
CHAIN_LENGTH = "chain-length"
NUM_DISTRACTING_ACTIONS = "num-distracting-actions"
ACTION_GOALS = "action-goals"
READABLE = "readable"

MIN = "min"
MAX = "max"


class Job:
	def __init__(self, chain_num, chain_length, time_window, num_distracting_actions=0, all_action_goals=True):
		self.chain_num = chain_num
		self.chain_length = chain_length
		self.time_window = time_window
		self.num_distracting_actions = num_distracting_actions
		self.all_action_goals = all_action_goals

	def getName(self, isdomain=True):
		return "P-{cn}-chains-{cl}-length{dacts}{aag}-{d}.pddl".format(
			d = "domain" if isdomain else "problem",
			cn = self.chain_num,
			cl = self.chain_length,
			dacts = "-{da}-dacts".format(da = self.num_distracting_actions) if self.num_distracting_actions else "",
			aag = "" if not self.all_action_goals else "-aag"
		)

def addJob(queue, chain_num, chain_length, time_window, num_distracting_actions, all_action_goals):
	aag = True if all_action_goals in AAG_TRUE else False
	queue.append(Job(chain_num, chain_length, time_window, num_distracting_actions, aag))
	if (all_action_goals == AAG_BOTH):
		queue.append(Job(chain_num, chain_length, time_window, num_distracting_actions, not aag))

def main(args):
	
	parser = argparse.ArgumentParser(description='Generator to create action chains benchmark problems.')
	parser.add_argument('path',
	                    metavar='/path/to/folder',
						type=str,
		                help='the path to store pddl files')
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
	
	
	time_window = config[TIME_WINDOW]
	num_chains_min = config[NUM_CHAINS][MIN]
	num_chains_max = config[NUM_CHAINS][MAX]
	chain_length_min = config[CHAIN_LENGTH][MIN]
	chain_length_max = config[CHAIN_LENGTH][MAX]	
	num_distracting_actions_min = config[NUM_DISTRACTING_ACTIONS][MIN]
	num_distracting_actions_max = config[NUM_DISTRACTING_ACTIONS][MAX]
	action_goals = config[ACTION_GOALS]
	readable = config[READABLE]

	print (action_goals)
	
	namer = n_chains.element_namer(readable)
	
	queue = []

	for chain in range(num_chains_min, num_chains_max+1):
		for chain_length in range(chain_length_min, chain_length_max+1):
			if not num_distracting_actions_max:
				addJob(queue, chain, chain_length, time_window, 0, action_goals)
			else :
				for num_distracting_actions in range (num_distracting_actions_min, num_distracting_actions_max+1):
					addJob(queue, chain, chain_length, time_window, num_distracting_actions, action_goals)
			
	for job in queue:
		n_chains.create_problem_instance(
			os.path.join(path, job.getName()),
			os.path.join(path, job.getName(False)),
			job.time_window,
			job.chain_num,
			job.chain_length,
			job.num_distracting_actions,
			job.all_action_goals,
			namer
		)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)
