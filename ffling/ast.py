# AST Node classes

class Node:
    pass

class Program(Node):
    def __init__(self, statements):
        self.statements = statements

class Printline(Node):
    def __init__(self, args):
        self.args = args

class Assignment(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class If(Node):
    def __init__(self, condition, then_block, elifs=None, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.elifs = elifs or []
        self.else_block = else_block

class Elif(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

class For(Node):
    def __init__(self, var, range_expr, block):
        self.var = var
        self.range_expr = range_expr
        self.block = block

class While(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

class Break(Node):
    pass

class Continue(Node):
    pass

class Func(Node):
    def __init__(self, name, params, block):
        self.name = name
        self.params = params
        self.block = block

class Return(Node):
    def __init__(self, value=None):
        self.value = value

class Call(Node):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

class Variable(Node):
    def __init__(self, name):
        self.name = name

class Literal(Node):
    def __init__(self, value):
        self.value = value

class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Table(Node):
    def __init__(self, pairs):
        self.pairs = pairs

class Import(Node):
    def __init__(self, path):
        self.path = path
