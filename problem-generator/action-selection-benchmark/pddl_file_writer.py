#!/usr/bin/python3

def write_domain(domain, file):
	file.write(domain.toString())
	
def write_problem(problem, file):
	file.write(problem.toString())