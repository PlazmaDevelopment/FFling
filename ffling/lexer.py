import re

class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, line {self.line})'

class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
        self.tokens = []
        self.indent_stack = [0]  # Start with 0 indent

    def advance(self):
        self.pos += 1

    def peek(self):
        if self.pos < len(self.code):
            return self.code[self.pos]
        return None

    def tokenize(self):
        lines = self.code.splitlines(keepends=True)
        for line_num, line in enumerate(lines, 1):
            self.line = line_num
            stripped = line.rstrip('\r\n')
            indent_len = self.get_indent_len(stripped)
            dedents_needed = 0
            # Handle dedents
            while self.indent_stack and indent_len < self.indent_stack[-1]:
                self.indent_stack.pop()
                dedents_needed += 1
            # Handle indents
            if indent_len > self.indent_stack[-1]:
                self.tokens.append(Token('INDENT', '', self.line))
                self.indent_stack.append(indent_len)
            # Add dedents
            for _ in range(dedents_needed):
                self.tokens.append(Token('DEDENT', '', self.line))

            # Tokenize the stripped line, skipping initial spaces
            i = indent_len + (stripped[indent_len:] != '' and stripped[indent_len] == ' ')
            while i < len(stripped):
                char = stripped[i]
                if char.isspace():
                    i += 1
                    continue
                if char == '"':
                    start = i
                    i += 1
                    while i < len(stripped) and stripped[i] != '"':
                        i += 1
                    if i >= len(stripped):
                        raise SyntaxError(f"String not terminated, line {self.line}")
                    value = stripped[start+1:i]
                    self.tokens.append(Token('STRING', value, self.line))
                    i += 1
                    continue
                if char.isdigit():
                    start = i
                    while i < len(stripped) and stripped[i].isdigit():
                        i += 1
                    value = int(stripped[start:i])
                    self.tokens.append(Token('NUMBER', value, self.line))
                    continue
                if char.isalpha() or char == '_':
                    start = i
                    while i < len(stripped) and (stripped[i].isalnum() or stripped[i] == '_'):
                        i += 1
                    value = stripped[start:i]
                    keyword_tokens = {
                        'local': 'LOCAL',
                        'printline': 'PRINTLINE',
                        'printlinef': 'PRINTLINEF',
                        'import': 'IMPORT',
                        'for': 'FOR',
                        'in': 'IN',
                        'range': 'RANGE',
                        'if': 'IF',
                        'elif': 'ELIF',
                        'else': 'ELSE',
                        'while': 'WHILE',
                        'break': 'BREAK',
                        'continue': 'CONTINUE',
                        'func': 'FUNC',
                        'return': 'RETURN',
                        'True': 'TRUE',
                        'False': 'FALSE',
                        'table': 'TABLE',
                        'and': 'AND',
                        'or': 'OR',
                        'not': 'NOT',
                        'pass': 'PASS',
                        'const': 'CONST',
                        'try': 'TRY',
                        'catch': 'CATCH',
                        'class': 'CLASS',
                        'new': 'NEW',
                        'this': 'THIS',
                        'null': 'NULL',
                        'nil': 'NIL',
                        'assert': 'ASSERT'
                    }
                    token_type = keyword_tokens.get(value, 'IDENTIFIER')
                    self.tokens.append(Token(token_type, value, self.line))
                    continue
                # Operators and punctuation (single char for simplicity)
                ops = {'=': 'ASSIGN', '==': 'EQ', '>': 'GT', '<': 'LT', '+': 'PLUS', '-': 'MINUS', '*': 'MUL', '/': 'DIV', '%': 'MOD', '(': 'LPAREN', ')': 'RPAREN', ':': 'COLON', ',': 'COMMA', '{': 'LBRACKET', '}': 'RBRACKET', '[': 'LSQUARE', ']': 'RSQUARE', '.': 'DOT'}
                found = False
                for op_len in [2,1]:
                    if i + op_len <= len(stripped) and stripped[i:i+op_len] in ops:
                        tok = Token(ops[stripped[i:i+op_len]], stripped[i:i+op_len], self.line)
                        self.tokens.append(tok)
                        i += op_len
                        found = True
                        break
                if found:
                    continue
                raise SyntaxError(f"Unknown character '{char}', line {self.line}")
            # Newline implicit EOL, but since blocks, no need
        # Close all indents with dedents
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token('DEDENT', '', self.line))
        self.tokens.append(Token('EOF', None, self.line))
        return self.tokens

    def get_indent_len(self, line):
        i = 0
        while i < len(line) and line[i].isspace() and line[i] != '\t':  # Assume spaces only
            i += 1
        if '\t' in line[:i]:
            raise SyntaxError(f"Tabs not allowed, line {self.line}")
        return i
