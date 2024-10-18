import re

# Token types
TOKEN_TYPES = {
    'WHILE': r'while',
    'PRINT': r'print',
    'INPUT': r'input',
    'NUMBER': r'\d+',
    'STRING': r'\".*?\"',
    'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*',
    'ASSIGN': r'=',
    'PLUS': r'\+',
    'MINUS': r'-',
    'MULTIPLY': r'\*',
    'DIVIDE': r'/',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
    'LBRACE': r'\{',
    'RBRACE': r'\}',
    'LESS': r'<',
    'GREATER': r'>',
    'SEMICOLON': r';',
    'WHITESPACE': r'[ \t]+',
    'NEWLINE': r'\n',
}

# Lexer function (unchanged)
def tokenize(code):
    tokens = []
    while code:
        match = None
        for token_type, regex in TOKEN_TYPES.items():
            pattern = re.compile(regex)
            match = pattern.match(code)
            if match:
                value = match.group(0)
                if token_type not in ['WHITESPACE', 'NEWLINE']:  # Skip whitespace/newlines
                    tokens.append((token_type, value))
                code = code[len(value):]
                break
        if not match:
            raise SyntaxError(f"Unexpected character: {code[0]}")
    return tokens

# Parser class with fixes
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        token = self.peek()
        self.pos += 1
        return token

    def expect(self, expected_type):
        token = self.peek()
        if token and token[0] == expected_type:
            return self.advance()
        raise SyntaxError(f"Expected {expected_type}, but got {token}")

    def parse_number(self):
        token = self.expect('NUMBER')
        return ('number', int(token[1]))

    def parse_string(self):
        token = self.expect('STRING')
        return ('string', token[1][1:-1])  # Remove quotes

    def parse_identifier(self):
        token = self.expect('IDENTIFIER')
        return ('identifier', token[1])

    def parse_expression(self):
        left = self.parse_term()
        while self.peek() and self.peek()[0] in {'PLUS', 'MINUS'}:
            operator = self.advance()[0]
            right = self.parse_term()
            left = ('binary_op', operator, left, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.peek() and self.peek()[0] in {'MULTIPLY', 'DIVIDE'}:
            operator = self.advance()[0]
            right = self.parse_factor()
            left = ('binary_op', operator, left, right)
        return left

    def parse_factor(self):
        if self.peek()[0] == 'NUMBER':
            return self.parse_number()
        elif self.peek()[0] == 'IDENTIFIER':
            return self.parse_identifier()
        elif self.peek()[0] == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {self.peek()}")

    def parse_comparison(self):
        left = self.parse_expression()
        if self.peek() and self.peek()[0] in {'GREATER', 'LESS'}:
            operator = self.advance()[0]
            right = self.parse_expression()
            return ('binary_op', operator, left, right)
        return left

    def parse_assignment(self):
        var_name = self.parse_identifier()
        self.expect('ASSIGN')
        expr = self.parse_expression()
        return ('assign', var_name, expr)

    def parse_print(self):
        self.expect('PRINT')
        expr = self.parse_expression()
        return ('print', expr)

    def parse_input(self):
        self.expect('INPUT')
        var_name = self.parse_identifier()
        return ('input', var_name)

    def parse_while(self):
        self.expect('WHILE')
        condition = self.parse_comparison()
        self.expect('LBRACE')
        body = self.parse_statements()
        self.expect('RBRACE')
        return ('while', condition, body)

    def parse_statement(self):
        token = self.peek()
        if token[0] == 'IDENTIFIER':
            return self.parse_assignment()
        elif token[0] == 'PRINT':
            return self.parse_print()
        elif token[0] == 'INPUT':
            return self.parse_input()
        elif token[0] == 'WHILE':
            return self.parse_while()
        else:
            raise SyntaxError(f"Invalid statement: {token}")

    def parse_statements(self):
        statements = []
        while self.peek() and self.peek()[0] != 'RBRACE':
            statements.append(self.parse_statement())
            if self.peek() and self.peek()[0] == 'SEMICOLON':
                self.advance()
        return statements

    def parse(self):
        return self.parse_statements()

# Interpreter class (unchanged)
class Interpreter:
    def __init__(self):
        self.variables = {}

    def eval_expression(self, expr):
        if expr[0] == 'number':
            return expr[1]
        elif expr[0] == 'string':
            return expr[1]
        elif expr[0] == 'identifier':
            var_name = expr[1]
            if var_name in self.variables:
                return self.variables[var_name]
            else:
                raise NameError(f"Undefined variable: {var_name}")
        elif expr[0] == 'binary_op':
            _, operator, left, right = expr
            left_val = self.eval_expression(left)
            right_val = self.eval_expression(right)

            if operator == 'PLUS':
                return left_val + right_val
            elif operator == 'MINUS':
                return left_val - right_val
            elif operator == 'MULTIPLY':
                return left_val * right_val
            elif operator == 'DIVIDE':
                return left_val / right_val
            elif operator == 'GREATER':
                return left_val > right_val
            elif operator == 'LESS':
                return left_val < right_val
            else:
                raise ValueError(f"Unknown operator: {operator}")
        else:
            raise ValueError("Unknown expression")

    def exec_statement(self, statement):
        if statement[0] == 'assign':
            var_name = statement[1][1]
            value = self.eval_expression(statement[2])
            self.variables[var_name] = value
        elif statement[0] == 'print':
            value = self.eval_expression(statement[1])
            print(value)
        elif statement[0] == 'input':
            var_name = statement[1][1]
            self.variables[var_name] = input("Input: ")
        elif statement[0] == 'while':
            condition = statement[1]
            while self.eval_expression(condition):
                for stmt in statement[2]:
                    self.exec_statement(stmt)
        else:
            raise ValueError("Unknown statement")

    def exec(self, statements):
        for stmt in statements:
            self.exec_statement(stmt)

# Main execution code
if __name__ == '__main__':
    with open('main_script.txt', 'r') as f:
        code = f.read()

    # Step 1: Tokenize the input
    tokens = tokenize(code)
    print("Tokens:", tokens)

    # Step 2: Parse the tokens into an AST
    parser = Parser(tokens)
    ast = parser.parse()
    print("AST:", ast)

    # Step 3: Interpret the AST
    interpreter = Interpreter()
    interpreter.exec(ast)