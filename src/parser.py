import ply.yacc as yacc
from lexer import *
import sys

class CParser:

    tokens = CLexer.tokens
    literals = CLexer.literals
    reserved = CLexer.reserved

    def p_expression_plus(self, p):
        'expression : expression "+" term'
        p[0] = p[1] + p[3]

    def p_expression_minus(self, p):
        'expression : expression "-" term'
        p[0] = p[1] - p[3]

    def p_expression_term(self, p):
        'expression : term'
        p[0] = p[1]

    def p_term_times(self, p):
        'term : term \'*\' factor'
        p[0] = p[1] * p[3]

    def p_term_div(self, p):
        'term : term "/" factor'
        p[0] = p[1] / p[3]

    def p_term_factor(self, p):
        'term : factor'
        p[0] = p[1]

    def p_factor_num(self, p):
        'factor : CONST_INT'
        p[0] = p[1]

    def p_factor_expr(self, p):
        'factor : "(" expression ")"'
        p[0] = p[2]

    def p_error(self, p):
        print("Syntax error in input!")

    def build(self, **kwargs):
        self.parser = yacc.yacc(module = self, **kwargs)

    def parse_inp(self, input):
        result = self.parser.parse(input)
        print(result)

# Build the parser
parser = CParser()
parser.build()
l = CLexer()
l.build()
while True:
    try:
        s = input('calc > ')
    except EOFError:
        break
    if not s: continue
    parser.parse_inp(s)