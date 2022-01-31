import ply.lex as lex
import sys


class CLexer:

    # Adding keywords
    reserved = {
        # Data types
        'int': 'INT', 'float': 'FLOAT', 'double': 'DOUBLE', 'long': 'LONG', 'char': 'CHAR',
        # Other
        'short': 'SHORT',
        'signed': 'SIGNED',
        'unsigned': 'UNSIGNED',
        'bool': 'BOOL',
        'const': 'CONST',
        'volatile': 'VOLATILE',
        'printf': 'PRINTF',
        'scanf': 'SCANF',
        'fprintf': 'FPRINTF',
        'fscanf': 'FSCANF',
        'fopen': 'FOPEN',
        'fclose': 'FCLOSE',
        'main': 'MAIN',
        'true': 'TRUE',
        'false': 'FALSE',
        'FILE': 'FILE',

        # keywords for condtionals
        'if': 'IF', 'else': 'ELSE', 'break': 'BREAK', 'continue': 'CONTINUE',

        # keywords for switch
        'switch': 'SWITCH', 'default': 'DEFAULT', 'case': 'CASE',

        # keywords for loops
        'for': 'FOR', 'while': 'WHILE', 'do': 'DO',

        # keywords used in functions
        'void': 'VOID', 'return': 'RETURN', 'goto': 'GOTO',

        # user defined data types
        'struct': 'STRUCT', 'union': 'UNION',

        # Math functions
        'sqrt': 'SQRT', 'exp': 'EXP', 'floor': 'FLOOR', 'ceil': 'CEIL', 'abs': 'ABS', 'log': 'LOG', 'pow': 'POW', 'sizeof': 'SIZEOF',

        # define for macro
        'define': 'DEFINE'
    }

    # Adding tokens
    tokens = [
        'SEMICOLON', 'COLON',
        'ID',
        # Constant types
        'CONST_STRING', 'CONST_CHAR', 'CONST_FLOAT', 'CONST_HEX', 'CONST_OCT', 'CONST_BIN', 'CONST_INT',
        # Comparison Operators
        'COMP_EQUAL', 'COMP_NEQUAL', 'COMP_LT', 'COMP_GT', 'COMP_LTEQ', 'COMP_GTEQ',

        # Logical Operators
        'LOGIC_AND', 'LOGIC_OR', 'LOGIC_NOT',

        # Bit Shift operators
        'BIT_LEFT', 'BIT_RIGHT',

        # Bitwise Logical Operators
        'BIT_LOGIC_OR', 'BIT_LOGIC_NOT', 'BIT_LOGIC_XOR',

        # Assignment Operators
        'ASSIGN', 'ADD_ASSIGN', 'SUB_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN', 'MOD_ASSIGN', 'BIL_ASSIGN', 'BIR_ASSIGN', 'AND_ASSIGN', 'OR_ASSIGN', 'XOR_ASSIGN',

        # Unary_Operators
        'ADDU', 'SUBU',

        # Reference and dereference operators ( single and double pointers)
        'DOUBLE_POINT',

        # Member access Expressions
        'MEMB_ACCESS'


    ] + list(reserved.values())

    # Regular expressions for tokens

    t_SEMICOLON = r';'
    t_COLON = r':'

    t_ASSIGN = r'='
    t_ADD_ASSIGN = r'\+='
    t_SUB_ASSIGN = r'-='
    t_MUL_ASSIGN = r'\*='
    t_DIV_ASSIGN = r'/='
    t_MOD_ASSIGN = r'%='
    t_BIL_ASSIGN = r'<<='
    t_BIR_ASSIGN = r'>>='
    t_AND_ASSIGN = r'&='
    t_OR_ASSIGN = r'\|='
    t_XOR_ASSIGN = r'\^='

    t_ADDU = r'\+\+'
    t_SUBU = r'--'

    t_COMP_EQUAL = r'=='
    t_COMP_NEQUAL = r'!='
    t_COMP_LT = r'<'
    t_COMP_GT = r'>'
    t_COMP_LTEQ = r'<='
    t_COMP_GTEQ = r'>='

    t_LOGIC_AND = r'&&'
    t_LOGIC_OR = r'\|\|'
    t_LOGIC_NOT = r'!'

    t_BIT_LEFT = r'<<'
    t_BIT_RIGHT = r'>>'

    t_BIT_LOGIC_OR = r'\|'
    t_BIT_LOGIC_XOR = r'\^'
    t_BIT_LOGIC_NOT = r'~'

    # 3.1.8 - 3.1.10
    t_DOUBLE_POINT = r'\*\*'
    t_MEMB_ACCESS = r'->'

    literals = '+-*/%&,?\.\{\}\(\)#[]'

    def t_CONST_STRING(self, t):
        r'(\"(\\.|[^\\"])*?\")'
        return t

    def t_CONST_CHAR(self, t):
        r'\'([^\\]|\\.)\''
        t.value = t.value[1:-1]
        return t

    def t_CONST_FLOAT(self, t):
        r'(\d*([.]\d+)?([eE][+-]?\d+)) | (\d*[.])\d+ | (\d+[.])'
        return t

    def t_CONST_HEX(self, t):
        r'0[xX][0-9A-fa-f]+'
        t.value = int(t.value, 16)
        return t

    def t_CONST_OCT(self, t):
        r'0[0-7]+'
        t.value = int(t.value, 8)
        return t

    def t_CONST_BIN(self, t):
        r'0b[01]+'
        t.value = int(t.value, 2)
        return t

    def t_CONST_INT(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')    # Check for reserved words
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_COMMENT(self, t):
        r'(/\*(.|\n)*?\*/)|(//.*)'
        for c in t.value:
            if c == '\n':
                t.lexer.lineno += 1
        pass

    #t_ignore_COMMENT = r'(/\*(.|\n)*?\*/)|(//.*)'
    t_ignore = ' \t\v\r\f'

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def tokenize(self, data):
        self.lexer.input(data)
        print("Token".ljust(15, ' '), "Lexeme".ljust(15, ' '),
              "Line#".ljust(15, ' '), "Column#".ljust(15, ' '))
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok.type.ljust(15, ' '), str(tok.value).ljust(15, ' '), str(
                tok.lineno).ljust(15, ' '), str(tok.lexpos).ljust(15, ' '))


l = CLexer()
l.build()
l.tokenize(open(sys.argv[1], 'r').read())
