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

def get_action_name():
	return random.choice(string.ascii_letters) + str(uuid.uuid1())

def create_time_window_TIL(goal_pred, time_window):
	return timed_initial_literal(
		time_window, 
		simple_effect(goal_pred, NEG))

def create_goal_achieving_action(precond_pred, goal_pred, duration):
	return durative_action(
		get_action_name(),
		[],
		duration,
		conj_goal(
			timed_goal(
				AT_END,
				simple_goal(precond_pred)
			)
		),
		timed_effect(
			AT_END,
			simple_effect(goal_pred)
		)
	)

def create_n_actions(num_actions, precond_pred, goal_pred, duration_mean, duration_variance):
	actions = []
	for x in range(0, num_actions):
		act = create_goal_achieving_action(
			precond_pred,
			goal_pred,
			random.uniform(duration_mean-duration_variance, duration_mean+duration_variance)
		)
		actions.append(act)

	return actions


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
	parser.add_argument('--num_actions',
						'-n',
	                    metavar='1',
						type=int,
						nargs="?",
						default=1,
		                help='the number of actions the domain should have in total')
	
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

	domain_file = args.domain
	problem_file = args.problem

	time_window = 5
	num_actions = args.num_actions

	goal_pred_name = "G"
	goal_pred = proposition(goal_pred_name)
	
	action_precond_pred_name = "P"
	action_precond_pred = proposition(action_precond_pred_name)

	time_window_TIL = create_time_window_TIL(action_precond_pred, time_window)
	goal_action = create_goal_achieving_action(action_precond_pred, goal_pred, time_window-1)
	n_actions = create_n_actions(num_actions-1, action_precond_pred, goal_pred, time_window+1, 1)
	

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
	dom.predicates = [
		goal_pred,
		action_precond_pred
	]
	
	dom.operators.append(goal_action)
	dom.operators.extend(n_actions)
	random.shuffle(dom.operators)

	prob = problem("action-{n}-choices-problem".format(n=num_actions), dom.name)
	prob.init = [
		action_precond_pred,
		time_window_TIL
	]
	prob.goal = conj_goal(
		simple_goal(goal_pred)
	)

	prob.metric = metric(
		function("total-time")
	)

	
	write_domain(dom, open(domain_file, 'w'))
	write_problem(prob, open(problem_file, 'w'))

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)