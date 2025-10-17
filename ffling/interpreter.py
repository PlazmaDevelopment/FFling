from ast import *

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined variable {name}")

    def set(self, name, value):
        self.vars[name] = value

class Interpreter:
    def __init__(self):
        self.glob_env = Environment()
        # Builtins
        self.glob_env.set('printline', lambda args: self.builtin_printline(args))
        self.glob_env.set('printlinef', lambda args: self.builtin_printline(args))  # Same for now
        self.glob_env.set('range', lambda args: self.builtin_range(args))
        self.glob_env.set('inputline', FFLibilFun(lambda args: input()))

    def execute(self, program):
        for stmt in program.statements:
            self.eval_stmt(stmt, self.glob_env)

    def eval_stmt(self, stmt, env):
        if isinstance(stmt, Printline):
            args = [self.eval_expr(arg, env) for arg in stmt.args]
            printline_func = self.glob_env.get('printline')
            printline_func(args)
        elif isinstance(stmt, Assignment):
            value = self.eval_expr(stmt.value, env)
            env.set(stmt.name, value)
        elif isinstance(stmt, If):
            if self.eval_expr(stmt.condition, env):
                self.exec_block(stmt.then_block, env)
            else:
                for elif_part in stmt.elifs:
                    if self.eval_expr(elif_part.condition, env):
                        self.exec_block(elif_part.block, env)
                        return
                if stmt.else_block:
                    self.exec_block(stmt.else_block, env)
        elif isinstance(stmt, For):
            range_arg = self.eval_expr(stmt.range_expr, env)
            for i in range(range_arg):
                local_env = Environment(env)
                local_env.set(stmt.var, i)
                try:
                    self.exec_block(stmt.block, local_env)
                except BreakException:
                    break
                except ContinueException:
                    continue
        elif isinstance(stmt, While):
            while self.eval_expr(stmt.condition, env):
                local_env = Environment(env)
                try:
                    self.exec_block(stmt.block, local_env)
                except BreakException:
                    break
                except ContinueException:
                    continue
        elif isinstance(stmt, Break):
            raise BreakException()
        elif isinstance(stmt, Continue):
            raise ContinueException()
        elif isinstance(stmt, Func):
            env.set(stmt.name, FuncDef(stmt.params, stmt.block))
        elif isinstance(stmt, Return):
            val = self.eval_expr(stmt.value, env) if stmt.value else None
            raise ReturnException(val)
        elif isinstance(stmt, Call):
            # Function call
            func = env.get(stmt.callee)
            args = [self.eval_expr(arg, env) for arg in stmt.args]
            if isinstance(func, FuncDef):
                local_env = Environment(env)
                for param, arg_val in zip(func.params, args):
                    local_env.set(param, arg_val)
                try:
                    self.exec_block(func.block, local_env)
                except ReturnException as e:
                    return e.value
            elif callable(func):
                return func(args)
            else:
                raise ValueError(f"{stmt.callee} is not callable")
        elif isinstance(stmt, Import):
            lib = stmt.path
            if lib == 'time':
                import time as pytime
                env.set('time_time', FFLibilFun(lambda args: pytime.time()))
                env.set('time_sleep', FFLibilFun(lambda args: pytime.sleep(args[0] if len(args) > 0 else 1)))
            # Add more libs
        else:
            # Expression statement
            self.eval_expr(stmt, env)

    def eval_expr(self, expr, env):
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Variable):
            return env.get(expr.name)
        elif isinstance(expr, BinOp):
            left = self.eval_expr(expr.left, env)
            right = self.eval_expr(expr.right, env)
            if expr.op == 'PLUS':
                return left + right
            elif expr.op == 'MINUS':
                return left - right
            elif expr.op == 'MUL':
                return left * right
            elif expr.op == 'DIV':
                return left / right
            elif expr.op == 'EQ':
                return left == right
            elif expr.op == 'GT':
                return left > right
            elif expr.op == 'LT':
                return left < right
            elif expr.op == 'AND':
                return left and right
            elif expr.op == 'OR':
                return left or right
            elif expr.op == 'MOD':
                return left % right
            else:
                raise ValueError(f"Unknown operator {expr.op}")
        elif isinstance(expr, Table):
            table = {}
            for k, v in expr.pairs.items():
                table[k] = self.eval_expr(v, env)
            return table
        elif isinstance(expr, Call):
            return self.eval_stmt(expr, env)  # Reuse
        else:
            raise ValueError(f"Unknown expression {expr}")

    def exec_block(self, block, env):
        for stmt in block:
            self.eval_stmt(stmt, env)

    def builtin_printline(self, args):
        for arg in args:
            print(arg, end=' ')
        print()

    def builtin_range(self, args):
        if len(args) == 1:
            return args[0]
        else:
            raise ValueError("range expects one argument")

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class FuncDef:
    def __init__(self, params, block):
        self.params = params
        self.block = block

class FFLibilFun:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
