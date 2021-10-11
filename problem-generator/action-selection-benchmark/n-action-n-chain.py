#!/usr/bin/python3
import sys
import os
import argparse
import random
import uuid
import string 
from pddl.common import *
from pddl.proposition import proposition
from pddl.function import function
from pddl.effects import *
from pddl.goals import *
from pddl.operators import durative_action
from pddl.metric import *
from pddl.domain import *
from pddl.problem import *
from pddl.pddl_file_writer import *


class action_namer:
	
	def __init__(self, readable_names):
		self.readable_names = readable_names

	def get_action_name(self, readable_name):
		if (self.readable_names):
			return readable_name
		return random.choice(string.ascii_letters) + str(uuid.uuid1())

def create_time_window_TIL(goal_pred, time_window):
	return timed_initial_literal(
		time_window, 
		simple_effect(goal_pred, NEG))

def create_setup_action(action_name, condition_proposition, effect_proposition, duration, an):
	return durative_action(
		an.get_action_name(action_name),
		[],
		duration,
		conj_goal(timed_goal(AT_START, condition_proposition)) if condition_proposition is not None else None,
		timed_effect(
			AT_END,
			simple_effect(effect_proposition)
		)
	)

def create_goal_achieving_action(action_name, conditions, goal_pred, duration, an):
	return durative_action(
		an.get_action_name(action_name),
		[],
		duration,
		conditions,
		timed_effect(
			AT_END,
			simple_effect(goal_pred)
		)
	)

def create_n_actions(action_name, num_actions, effect_proposition, duration_mean, duration_variance, an):
	actions = []
	for x in range(0, num_actions):
		act = create_setup_action(
			action_name + str(x),
			effect_proposition,
			random.uniform(duration_mean-duration_variance, duration_mean+duration_variance),
			an
		)
		actions.append(act)

	return actions

def create_chain(chain_num, chain_len, num_actions, time_window, an):
	
	#add a bit more to keep some planners happy
	#colin like planners fail when actions fit exactly inside the time window
	action_duration = time_window / (chain_len + 1) 
	action_chain = []
	propositions = []
	#Create chain of actions
	previous_support_prop = None
	for x in range(0, chain_len-1):
		support_precond_pred = proposition("P-{cl}-{cn}".format(
			cl = x,
			cn = chain_num
		))
		propositions.insert(support_precond_pred)
		setup_action = create_setup_action(
			"setup-action", 
			previous_support_prop,
			support_precond_pred, 
			action_duration, 
			an)
		action_chain.insert(setup_action)
		previous_support_prop = support_precond_pred
	
	goal = proposition("G-{cn}".format(
		cn = chain_num
	))
	propositions.insert(goal)
	
	goal_action_timed_pred = proposition("T-{cn}".format(
		cn = chain_num
	))
	propositions.insert(goal_action_timed_pred)
		
	#Create final action to achieve goal
	goal_action = create_goal_achieving_action(
		"goal-action",
		conj_goal(
			timed_goal(
				AT_START,
				simple_goal(previous_support_prop)
			),
			timed_goal(
				AT_END,
				simple_goal(goal_action_timed_pred)
			)
		),
		goal, 
		action_duration,
		an)
	action_chain.insert(goal_action)
	
	return action_chain, propositions, goal_action_timed_pred, goal
	#n_actions = create_n_actions("rand-actions", num_actions, goal_action_precond_pred, time_window+1-((time_window-1)/2), 1, an)
	

def main(args):
	
	parser = argparse.ArgumentParser(description='Test harness to create a simple benchmark domain.')
	parser.add_argument('domain',
	                    metavar='/path/to/domain.pddl',
						type=str,
		                help='the location and name of domain file')
	parser.add_argument('problem',
	                    metavar='/path/to/problem.pddl',
						type=str,
		                help='the location and name of problem file')
	parser.add_argument('--num-actions',
						'-n',
	                    metavar='1',
						type=int,
						nargs="?",
						default=0,
		                help='the number of extra actions the domain should have')
	parser.add_argument('--chain-length',
						'-c',
	                    metavar='2',
						type=int,
						nargs="?",
						default=2,
		                help='the number of actions the domain should have in total')
	parser.add_argument('--duration',
						'-d',
	                    metavar='5',
						type=int,
						nargs="?",
						default=5,
		                help='the duration of the time window (this affects the duration of actions')
	parser.add_argument('--readable-action-names',
						action='store_true',
						default=False,
		                help='Whether to use std or readable action names')
	
	args = parser.parse_args()

	domain_path = os.path.dirname(args.domain)
	if (len(domain_path) and not os.path.isdir(domain_path)):
		print("Error: {path} is not a valid path.".format(
			path=domain_path
		))
		sys.exit(-1)

	problem_path = os.path.dirname(args.problem)
	if (len(problem_path) and not os.path.isdir(problem_path)):
		print("Error: {path} is not a valid path.".format(
			path=problem_path
		))
		sys.exit(-1)

	an = action_namer(args.readable_action_names)

	domain_file = args.domain
	problem_file = args.problem

	time_window = args.duration
	num_actions = args.num_actions
	chain_length = args.chain_length
	num_chains = 1

	dom = domain("action-{n}-choices".format(
		n = num_actions
	))
	reqs = [
		REQUIREMENTS[0], #strips
		REQUIREMENTS[1], #equality
		REQUIREMENTS[2], #typing
		REQUIREMENTS[4], #durative-actions
		REQUIREMENTS[5], #TILs
	]

	dom.requirements.extend(reqs)

	prob = problem("action-{n}-choices-problem".format(n=num_actions), dom.name)
	
	prob.metric = metric(
		function("total-time")
	)

	#Create the chains here
	goals = []
	for chain_num in range(0, num_chains):
		action_chain, propositions, goal_pred, goal = create_chain(chain_num, chain_length, num_actions, time_window, an)
		#Add actions and propositions to domain
		dom.operators.extend(action_chain)
		dom.predicates.extend(propositions)
		#Add initial state and goals to problem

		#Create the time window for goal action
		time_window_start = simple_effect(goal_pred)
		time_window_end = create_time_window_TIL(goal_pred, time_window)
		prob.init.append(time_window_start)
		prob.init.append(time_window_end)
		#add goal to goal list for later
		goals.append(simple_goal(goal))
	
	#add goal list to problem
	prob.goal = conj_goal(
		goals
	)

	#Randomise the domain operators to avoid 
	#fortunate selections by ordering in domain file
	random.shuffle(dom.operators)

	#Write domain and problem to disk
	write_domain(dom, open(domain_file, 'w'))
	write_problem(prob, open(problem_file, 'w'))

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)