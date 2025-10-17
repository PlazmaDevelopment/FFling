from ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_tok = self.tokens[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_tok = self.tokens[self.pos]
        else:
            self.current_tok = None

    def error(self, msg):
        raise SyntaxError(f"Syntax error: {msg} at token {self.current_tok}")

    def parse(self):
        statements = []
        while self.current_tok and self.current_tok.type != 'EOF':
            stmt = self.parse_statement()
            statements.append(stmt)
        return Program(statements)

    def parse_statement(self):
        if self.current_tok.type == 'LOCAL':
            return self.parse_assignment()
        elif self.current_tok.type == 'PRINTLINE':
            return self.parse_printline()
        elif self.current_tok.type == 'PRINTLINEF':
            return self.parse_printline()  # Same for now
        elif self.current_tok.type == 'IF':
            return self.parse_if()
        elif self.current_tok.type == 'FOR':
            return self.parse_for()
        elif self.current_tok.type == 'WHILE':
            return self.parse_while()
        elif self.current_tok.type == 'BREAK':
            self.advance()
            return Break()
        elif self.current_tok.type == 'CONTINUE':
            self.advance()
            return Continue()
        elif self.current_tok.type == 'FUNC':
            return self.parse_func()
        elif self.current_tok.type == 'RETURN':
            return self.parse_return()
        elif self.current_tok.type == 'TABLE':
            return self.parse_table()
        elif self.current_tok.type == 'IMPORT':
            return self.parse_import()
        else:
            # Function call or other
            return self.parse_expression()

    def parse_assignment(self):
        self.expect('LOCAL')
        name = self.expect('IDENTIFIER')
        self.expect('ASSIGN')
        value = self.parse_expression()
        return Assignment(name.value, value)

    def parse_printline(self):
        if self.current_tok.type == 'PRINTLINE':
            self.advance()
        elif self.current_tok.type == 'PRINTLINEF':
            self.advance()
        self.expect('LPAREN')
        args = []
        while self.current_tok.type != 'RPAREN':
            args.append(self.parse_expression())
            if self.current_tok.type == 'COMMA':
                self.advance()
        self.expect('RPAREN')
        return Printline(args)

    def parse_if(self):
        self.expect('IF')
        self.expect('LPAREN')  # Assume condition in parens
        condition = self.parse_expression()
        self.expect('RPAREN')
        self.expect('COLON')
        then_block = self.parse_block()
        elifs = []
        while self.current_tok and self.current_tok.type == 'ELIF':
            self.advance()
            self.expect('LPAREN')
            elif_condition = self.parse_expression()
            self.expect('RPAREN')
            self.expect('COLON')
            elif_block = self.parse_block()
            elifs.append(Elif(elif_condition, elif_block))
        else_block = None
        if self.current_tok and self.current_tok.type == 'ELSE':
            self.advance()
            self.expect('COLON')
            else_block = self.parse_block()
        return If(condition, then_block, elifs, else_block)

    def parse_for(self):
        self.expect('FOR')
        var = self.expect('IDENTIFIER')
        self.expect('IN')
        self.expect('RANGE')
        self.expect('LPAREN')
        range_arg = self.parse_expression()
        self.expect('RPAREN')
        self.expect('COLON')
        block = self.parse_block()
        return For(var.value, range_arg, block)

    def parse_while(self):
        self.expect('WHILE')
        self.expect('LPAREN')
        condition = self.parse_expression()
        self.expect('RPAREN')
        self.expect('COLON')
        block = self.parse_block()
        return While(condition, block)

    def parse_func(self):
        self.expect('FUNC')
        name = self.expect('IDENTIFIER')
        self.expect('LPAREN')
        params = []
        while self.current_tok.type != 'RPAREN':
            param = self.expect('IDENTIFIER')
            params.append(param.value)
            if self.current_tok.type == 'COMMA':
                self.advance()
        self.expect('RPAREN')
        self.expect('COLON')
        block = self.parse_block()
        return Func(name.value, params, block)

    def parse_return(self):
        self.expect('RETURN')
        value = None
        if self.current_tok and self.current_tok.type not in ('EOF',):  # Simple check
            value = self.parse_expression()
        return Return(value)

    def parse_table(self):
        self.expect('TABLE')
        name = self.expect('IDENTIFIER')
        self.expect('ASSIGN')
        self.expect('LBRACKET')
        pairs = {}
        while self.current_tok.type != 'RBRACKET':
            key = self.expect('STRING')
            self.expect('COLON')
            value = self.parse_expression()
            pairs[key.value] = value
            if self.current_tok.type == 'COMMA':
                self.advance()
        self.expect('RBRACKET')
        return Assignment(name.value, Table(pairs))

    def parse_import(self):
        self.expect('IMPORT')
        if self.current_tok.type == 'STRING':
            path = self.expect('STRING')
            return Import(path.value)
        else:
            # Assume identifier for library
            lib = self.expect('IDENTIFIER')
            return Import(lib.value)  # For simplicity, treat as string

    def parse_block(self):
        self.expect('INDENT')
        statements = []
        while self.current_tok and self.current_tok.type != 'DEDENT':
            stmt = self.parse_statement()
            statements.append(stmt)
        self.expect('DEDENT')
        return statements

    def parse_expression(self):
        return self.parse_logic()

    def parse_logic(self):
        left = self.parse_binop()
        while self.current_tok and self.current_tok.type in ('AND', 'OR'):
            op = self.current_tok.type
            self.advance()
            right = self.parse_binop()
            left = BinOp(left, op, right)
        return left

    def parse_binop(self):
        left = self.parse_term()
        while self.current_tok and self.current_tok.type in ('PLUS', 'MINUS', 'EQ', 'GT', 'LT', 'MUL', 'DIV', 'MOD'):
            op = self.current_tok.type
            self.advance()
            right = self.parse_term()
            left = BinOp(left, op, right)
        return left

    def parse_term(self):
        tok = self.current_tok
        if tok.type == 'NUMBER':
            self.advance()
            return Literal(tok.value)
        elif tok.type == 'STRING':
            self.advance()
            return Literal(tok.value)
        elif tok.type == 'IDENTIFIER':
            self.advance()
            if self.current_tok and self.current_tok.type == 'LPAREN':
                return self.parse_call(tok.value)
            else:
                return Variable(tok.value)
        elif tok.type in ('TRUE', 'FALSE'):
            self.advance()
            return Literal(tok.value == 'TRUE')
        elif tok.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        else:
            self.error("Expression expected")

    def parse_call(self, name):
        self.expect('LPAREN')
        args = []
        while self.current_tok.type != 'RPAREN':
            args.append(self.parse_expression())
            if self.current_tok.type == 'COMMA':
                self.advance()
        self.expect('RPAREN')
        return Call(name, args)

    def expect(self, tok_type):
        if self.current_tok and self.current_tok.type == tok_type:
            tok = self.current_tok
            self.advance()
            return tok
        else:
            self.error(f"Expected {tok_type}, got {self.current_tok}")
