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


class element_namer:
	
	def __init__(self, readable=False):
		self.readable = readable

	def get_name(self, readable_name):
		if (self.readable):
			return readable_name
		return random.choice(string.ascii_letters) + str(uuid.uuid1())

def create_time_window_TIL(goal_pred, time_window):
	return timed_initial_literal(
		time_window, 
		simple_effect(goal_pred, NEG))

def create_condition(time_spec, pred):
	if pred is None:
		return None
	else:
		return conj_goal(timed_goal(time_spec, pred))

def create_action(action_name, condition, effects, duration, namer):
		
	return durative_action(
		namer.get_name(action_name),
		[],
		duration,
		condition,
		conj_effect(*effects)
	)

def create_n_similar_actions(orig_name, num_actions, condition, effect, duration_mean, duration_variance, all_action_goals, namer):
	actions = []
	propositions = []
	goals = []
	for x in range(0, num_actions):
		action_name = "{name}-{num}".format(
			name=orig_name,
			num=str(x)
		)

		effects = [effect]
		if all_action_goals:
			action_goal = proposition("{n}-prop".format(
				n = action_name
			))
			propositions.append(action_goal)
			effects.append(timed_effect(AT_END, action_goal))
			goals.append(action_goal)

		act = create_action(
			action_name,
			condition,
			effects,
			round(random.uniform(duration_mean-duration_variance, duration_mean+duration_variance), 2),
			namer
		)
		actions.append(act)
	return actions, propositions, goals

def create_chain(time_window, chain_num, chain_len, num_rand_actions, all_action_goals, namer):
	
	#add a bit more to keep some planners happy
	#colin like planners fail when actions fit exactly inside the time window
	action_duration = round(time_window / (chain_len + 0.2), 2)
	actions = []
	propositions = []
	goals = []

	chain_init_prop = proposition("P-Init-{cn}".format(
		cn = chain_num
	))
	propositions.append(chain_init_prop)
	#Create chain of actions
	previous_support_prop = chain_init_prop
	for x in range(0, chain_len-1):
		action_name = "setup-action-{cl}-{cn}".format(
			cl = x,
			cn = chain_num
		)
		
		support_precond_pred = proposition("P-{cl}-{cn}".format(
			cl = x,
			cn = chain_num
		))
		propositions.append(support_precond_pred)
		next_action_support_effect = timed_effect(AT_END, support_precond_pred)
		effects = [next_action_support_effect]
		condition = create_condition(AT_START, previous_support_prop)
		if (all_action_goals):
			action_goal = proposition("{n}-prop".format(
				n = action_name
			))
			propositions.append(action_goal)
			effects.append(timed_effect(AT_END, action_goal))
			goals.append(action_goal)

		setup_action = create_action(
			action_name,
			condition,
			effects, 
			action_duration, 
			namer)
		actions.append(setup_action)

		#create n-trick actions to throw planners off
		n_actions, n_act_props, n_act_goals = create_n_similar_actions(
			"rand-actions-{cl}-{cn}".format(
				cl = x,
				cn = chain_num
			),
			num_rand_actions, 
			condition,
			next_action_support_effect,
			action_duration+1.2,
			0.5,
			all_action_goals,
			namer)
		actions.extend(n_actions)
		propositions.extend(n_act_props)
		goals.extend(n_act_goals)

		#update state for next cycle
		previous_support_prop = support_precond_pred
	
	goal = proposition("G-{cn}".format(
		cn = chain_num
	))
	propositions.append(goal)
	goals.append(goal)

	goal_action_timed_pred = proposition("T-{cn}".format(
		cn = chain_num
	))
	propositions.append(goal_action_timed_pred)
			
	#Create final action to achieve goal
	goal_action = create_action(
		"goal-action-{cn}".format(
			cn = chain_num
		), 
		conj_goal(timed_goal(
			AT_START,
			simple_goal(previous_support_prop)
		),
		timed_goal(
			AT_END,
			simple_goal(goal_action_timed_pred)
		)),
		[timed_goal(AT_END, goal)], 
		action_duration,
		namer)
	actions.append(goal_action)
	
	return actions, propositions, goal_action_timed_pred, goals, chain_init_prop

def create_problem_instance(domain_file, problem_file, time_window, num_chains, chain_length, num_rand_actions, all_action_goals, namer):

	dom = domain("action-{cn}-chains-{cl}-length-{ra}-racts{acg}".format(
		cn = num_chains,
		cl = chain_length,
		ra = num_rand_actions,
		acg = "" if not all_action_goals else "-aag"
	))

	reqs = [
		REQUIREMENTS[0], #strips
		REQUIREMENTS[1], #equality
		REQUIREMENTS[2], #typing
		REQUIREMENTS[4], #durative-actions
		REQUIREMENTS[5], #TILs
	]

	dom.requirements.extend(reqs)

	prob = problem("{n}-problem".format(
		n=dom.name), dom)
	
	prob.metric = metric(
		function("total-time")
	)

	#Create the chains here
	goals = []
	for chain_num in range(0, num_chains):
		
		action_chain, propositions, goal_pred, chain_goals, chain_init = create_chain(
			time_window, 
			chain_num, 
			chain_length, 
			num_rand_actions, 
			all_action_goals, 
			namer)

		#Add actions and propositions to domain
		dom.operators.extend(action_chain)
		dom.predicates.extend(propositions)
		#Add initial state and goals to problem

		#Create the time window for goal action
		time_window_start = simple_effect(goal_pred)
		time_window_end = create_time_window_TIL(goal_pred, time_window)
		prob.init.append(time_window_start)
		prob.init.append(time_window_end)
		prob.init.append(simple_effect(chain_init))
		#add goal to goal list for later
		for goal in chain_goals:
			goals.append(simple_goal(goal))
	
	#add goal list to problem
	prob.goal = conj_goal(*goals)

	#Randomise the domain operators to avoid 
	#fortunate selections by ordering in domain file
	random.shuffle(dom.operators)
	
	#Write domain and problem to disk
	write_domain(dom, open(domain_file, 'w'))
	write_problem(prob, open(problem_file, 'w'))

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
	parser.add_argument('--chain-length',
						'-c',
	                    metavar='2',
						type=int,
						nargs="?",
						default=2,
		                help='the number of actions the domain should have in total')
	parser.add_argument('--num-chains',
						'-n',
	                    metavar='1',
						type=int,
						nargs="?",
						default=1,
		                help='the number of action chains in the domain')
	parser.add_argument('--num-rand-actions',
						'-a',
	                    metavar='1',
						type=int,
						nargs="?",
						default=0,
		                help='the number of extra random actions to make per action per action chain')
	parser.add_argument('--duration',
						'-d',
	                    metavar='5',
						type=int,
						nargs="?",
						default=5,
		                help='the duration of the time window (this affects the duration of actions')
	parser.add_argument('--all-action-goals',
						'-g',
						action='store_true',
						default=False,
		                help='Whether all actions must be achieved in the goal state')
	parser.add_argument('--readable',
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

	namer = element_namer(args.readable)


	domain_file = args.domain
	problem_file = args.problem

	time_window = args.duration
	num_rand_actions = args.num_rand_actions
	chain_length = args.chain_length
	num_chains = args.num_chains
	all_action_goals = args.all_action_goals

	create_problem_instance(
		domain_file,
		problem_file,
		time_window,
		num_chains,
		chain_length,
		num_rand_actions,
		all_action_goals,
		namer
	)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)