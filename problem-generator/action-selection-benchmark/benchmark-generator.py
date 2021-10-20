#!/usr/bin/python3
import sys
import os
import argparse
import importlib  
n_chains = importlib.import_module("n-chains-l-length-a-racts")

ALL_ACTION_GOAL_PARAM = ['all', 'chains_only', 'both']
AAG_TRUE = [ALL_ACTION_GOAL_PARAM[0], ALL_ACTION_GOAL_PARAM[2]]
AAG_BOTH = ALL_ACTION_GOAL_PARAM[2]

class Job:
	def __init__(self, chain_num, chain_length, time_window, num_rand_actions=0, all_action_goals=True):
		self.chain_num = chain_num
		self.chain_length = chain_length
		self.time_window = time_window
		self.num_rand_actions = num_rand_actions
		self.all_action_goals = all_action_goals

	def getName(self, isdomain=True):
		return "P-{cn}-chains-{cl}-length{racts}{aag}-{d}.pddl".format(
			d = "domain" if isdomain else "problem",
			cn = self.chain_num,
			cl = self.chain_length,
			racts = "-{ra}-racts".format(ra = self.num_rand_actions) if self.num_rand_actions else "",
			aag = "" if not self.all_action_goals else "-aag"
		)

def addJob(queue, chain_num, chain_length, time_window, num_rand_actions, all_action_goals):
	aag = True if all_action_goals in AAG_TRUE else False
	queue.append(Job(chain_num, chain_length, time_window, num_rand_actions, aag))
	if (all_action_goals == AAG_BOTH):
		queue.append(Job(chain_num, chain_length, time_window, num_rand_actions, not aag))

def main(args):
	
	parser = argparse.ArgumentParser(description='Test harness to create a simple benchmark domain.')
	parser.add_argument('path',
	                    metavar='/path/to/folder',
						type=str,
		                help='the path to store pddl files')
	parser.add_argument('--chain-length-max',
						'-c',
	                    metavar='2',
						type=int,
						nargs="?",
						default=2,
		                help='the maximum number of actions the domain should have in total')
	parser.add_argument('--num-chains-max',
						'-n',
	                    metavar='1',
						type=int,
						nargs="?",
						default=1,
		                help='the maximum number of action chains in the domain')
	parser.add_argument('--rand-actions-max',
						'-a',
	                    metavar='1',
						type=int,
						nargs="?",
						default=0,
		                help='the maximum number of extra random actions to make per action per action chain')
	parser.add_argument('--duration',
						'-d',
	                    metavar='5',
						type=int,
						nargs="?",
						default=5,
		                help='the duration of the time window (this affects the duration of actions')
	parser.add_argument('--action-goals',
						'-g',
						choices=ALL_ACTION_GOAL_PARAM,
						default='all',
		                help='Which actions must be achieved in the goal state. Both creates the two problem variants.')
	parser.add_argument('--readable',
						action='store_true',
						default=False,
		                help='Whether to use std or readable action names')
	
	args = parser.parse_args()

	path = os.path.dirname(args.path)
	if (len(path) and not os.path.isdir(path)):
		print("Error: {p} is not a valid path.".format(
			p=path
		))
		sys.exit(-1)

	namer = n_chains.element_namer(args.readable)

	time_window = args.duration
	num_chains_max = args.num_chains_max
	chain_length_max = args.chain_length_max
	rand_actions_max = args.rand_actions_max
	action_goals = args.action_goals

	
	queue = []

	for chain in range(1, num_chains_max+1):
		for chain_length in range(1, chain_length_max+1):
			if not rand_actions_max:
				addJob(queue, chain, chain_length, time_window, 0, action_goals)
			else :
				for num_rand_actions in range (1, rand_actions_max+1):
					addJob(queue, chain, chain_length, time_window, num_rand_actions, action_goals)
			
	for job in queue:
		n_chains.create_problem_instance(
			os.path.join(path, job.getName()),
			os.path.join(path, job.getName(False)),
			job.time_window,
			job.chain_num,
			job.chain_length,
			job.num_rand_actions,
			job.all_action_goals,
			namer
		)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)