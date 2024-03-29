#!/usr/bin/python3
from pddl.symbols import func_symbol, var_symbol
from pddl.common import ARG_VOCAB

class function:

	def __init__(self, name, argument_types=[]):
		self.name = func_symbol(name)
		self.arguments = self.__create_arguments(argument_types)

	def __create_arguments(self, argument_types):
		args = []
		for arg_type, arg in zip(argument_types, ARG_VOCAB):
			args.append(var_symbol(arg, arg_type))
		return args

	def toString(self, tab_depth=0):
		return "{t}({name}{sep}{args})".format(
			t="\t"*tab_depth,
			name=self.name,
			sep=" " if len(self.arguments) else "",
			args=" ".join(self.arguments))

	def __str__(self):
		return self.toString()
