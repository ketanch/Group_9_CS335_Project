import ply.lex as lex
import sys

class CLexer:

    # Adding keywords
    reserved = {
        #Data types
        'int': 'INT', 'long': 'LONG', 'char': 'CHAR', 'float': 'float', 'double': 'DOUBLE',
        #Other
        'else': 'ELSE',
        'return': 'RETURN',
        'void': 'VOID',
        'struct': 'STRUCT'
    }

    # Adding tokens
    tokens = [
        'SEMICOLON',
        'ID',
        'DIGIT',
    ] + list(reserved.values())

    # Regular expressions for tokens
    t_SEMICOLON = r';'
    t_DIGIT = r'[0-9]+'
    literals = '\{\}\(\)+=.'

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')    # Check for reserved words
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ignore = ' \t'

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def tokenize(self, data):
        self.lexer.input(data)
        print("Token".ljust(15, ' '), "Lexeme".ljust(15, ' '), "Line#".ljust(15, ' '), "Column#".ljust(15, ' '))
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok.type.ljust(15, ' '), tok.value.ljust(15, ' '), str(tok.lineno).ljust(15, ' '), str(tok.lexpos).ljust(15, ' '))

l = CLexer()
l.build()
l.tokenize(open(sys.argv[1], 'r').read())