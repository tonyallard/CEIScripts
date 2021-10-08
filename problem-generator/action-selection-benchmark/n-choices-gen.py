#!/usr/bin/python3
import sys
from pddl_common import *
from pddl_proposition import proposition
from pddl_function import function
from pddl_effects import *
from pddl_goals import *
from pddl_operators import durative_action
from pddl_metric import *
from pddl_domain import *
from pddl_problem import *
from pddl_file_writer import *


def main(args):
	
	dom = domain("n-choices")
	reqs = [
		REQUIREMENTS[0], #strips
		REQUIREMENTS[1], #equality
		REQUIREMENTS[2], #typing
		REQUIREMENTS[4], #durative-actions
		REQUIREMENTS[5], #TILs
	]
	dom.requirements.extend(reqs)
	preds = [
		proposition("A"),
		proposition("B"),
		proposition("C"),
		proposition("P"),
		proposition("Q")
	]
	dom.predicates.extend(preds)

	actions = [
		durative_action(
			"A",
			[],
			1,
			None,
			conj_effect(
				timed_effect(
					AT_END,
					simple_effect(proposition("A"))
				),
				timed_effect(
					AT_END,
					simple_effect(proposition("P"))
				)
			)
		),
		durative_action(
			"B",
			[],
			4,
			None,
			conj_effect(
				timed_effect(
					AT_END,
					simple_effect(proposition("B"))
				),
				timed_effect(
					AT_END,
					simple_effect(proposition("P"))
				)
			)
		),
		durative_action(
			"C",
			[],
			2,
			conj_goal(
				timed_goal(
					AT_START,
					simple_goal(proposition("P"))
				),
				timed_goal(
					AT_END,
					simple_effect(proposition("Q"))
				)
			),
			timed_effect(
				AT_END,
				simple_effect(proposition("C"))
			)
		)
	]
	dom.operators.extend(actions)

	prob = problem("Prob1", dom.name)
	prob.init = conj_effect(
		simple_effect(proposition("P")),
		timed_initial_literal(5, simple_effect("Q", NEG))
	)
	prob.goal = conj_goal(
		simple_goal(proposition("A")),
		simple_goal(proposition("B")),
		simple_goal(proposition("C"))
	)

	prob.metric = metric(
		function("total-time")
	)

	
	write_domain(dom, sys.stdout)
	write_problem(prob, sys.stdout)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)