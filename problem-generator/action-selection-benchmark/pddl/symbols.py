#!/usr/bin/python3

class symbol:
	def __init__(self, name):
		self.name = name

	def __str__(self):
		return self.name

	def __repr__(self):
		return 'symbol(name={self.name})'

class pddl_type(symbol):
	def __init__(self, name):
		super().__init__(name)

	def __repr__(self):
		return 'pddl_type(name={self.name})'

class pred_symbol(symbol):
	def __init__(self, name):
		super().__init__(name)

	def __repr__(self):
		return 'pred_symbol(name={self.name})'

class func_symbol(symbol):
	def __init__(self, name):
		super().__init__(name)

	def __repr__(self):
		return 'func_symbol(name={self.name})'

class operator_symbol(symbol):
	def __init__(self, name):
		super().__init__(name)

	def __repr__(self):
		return 'operator_symbol(name={self.name})'

class pddl_typed_symbol(symbol):
	def __init__(self, name, type : pddl_type):
		super().__init__(name)
		self.type = type

	def __str__(self):
		return "{self.name} - {self.type}"

	def __repr__(self):
		return 'pddl_typed_symbol(name={self.name}, type={self.type})'

class parameter_symbol(pddl_typed_symbol):
	def __init__(self, name, type):
		super().__init__(name, type)

	def __repr__(self):
		return 'parameter_symbol(name={self.name}, type={self.type})'


class var_symbol(parameter_symbol):
	def __init__(self, name, type):
		super().__init__(name, type)

	def __str__(self):
		return "?{self.name} - {self.type}"

	def __repr__(self):
		return 'var_symbol(name={self.name}, type={self.type})'

class const_symbol(parameter_symbol):
	def __init__(self, name, type):
		super().__init__(name, type)

	def __repr__(self):
		return 'const_symbol(name={self.name}, type={self.type})'