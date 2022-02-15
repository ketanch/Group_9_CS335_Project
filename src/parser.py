import ply.yacc as yacc
from lexer import *
import sys


class CParser:

    tokens = CLexer.tokens
    literals = CLexer.literals
    #reserved = CLexer.reserved

    precedence = (
        ('left', 'LOGIC_OR'),
        ('left', 'LOGIC_AND'),
        ('left', '|'),
        ('left', '^'),
        ('left', '&'),
        ('left', 'COMP_EQUAL', 'COMP_NEQUAL'),
        ('left', '>', 'COMP_GTEQ', '<', 'COMP_LTEQ'),
        ('left', 'BIT_RIGHT', 'BIT_LEFT'),
        ('left', '+', '-'),
        ('left', '*', '/', '%')
    )

    def p_primary_expression(self, p):
        '''primary_expression   : ID
                                | constant
                                | CONST_STRING   
                                | '(' expression ')'
        '''
        if(len(p) == 2):
            p[0] = p[1]
        else:
            p[0] = p[2]
        # to look again FUNC_NAME in CONST_String

    def p_constant(self, p):
        '''constant : CONST_INT
                    | CONST_CHAR
                    | CONST_FLOAT
                    | CONST_HEX
                    | CONST_OCT
                    | CONST_BIN    
                    | TRUE
                    | FALSE  
        '''
        p[0] = p[1]

    def p_postfix_expression(self, p):
        '''postfix_expression   : primary_expression
                                | postfix_expression '[' expression ']'
                                | postfix_expression '(' ')'
                                | postfix_expression '(' argument_expression_list ')'
                                | postfix_expression '.' ID
                                | postfix_expression MEMB_ACCESS ID
                                | postfix_expression ADDU
                                | postfix_expression SUBU
                                | '(' type_name ')' '{' initializer_list '}'
                                | '(' type_name ')' '{' initializer_list ',' '}'
        '''
        

    def p_argument_expression_list(self, p):
        '''argument_expression_list : assignment_expression
                                    | argument_expression_list ',' assignment_expression
        '''

    def p_unary_expression(self, p):
        '''unary_expression : postfix_expression
                            | ADDU unary_expression
                            | SUBU unary_expression
                            | unary_operator unary_expression
                            | SIZEOF unary_expression
                            | SIZEOF '(' type_name ')'
        '''

    def p_unary_operator(self, p):
        '''unary_operator   : '&'
                            | '*'
                            | '+'
                            | '-'
                            | '~'
                            | '!'                      
        '''

    def p_multipicative_expression(self, p):
        '''multiplicative_expression    : unary_expression
                                        | multiplicative_expression '*' unary_expression
                                        | multiplicative_expression '/' unary_expression
                                        | multiplicative_expression '%' unary_expression
        '''

    def p_additive_expression(self, p):
        '''additive_expression  : multiplicative_expression
                                | additive_expression '+' multiplicative_expression
                                | additive_expression '-' multiplicative_expression
        '''

    def p_shift_expression(self, p):
        '''shift_expression : additive_expression
                            | shift_expression BIT_LEFT additive_expression
                            | shift_expression BIT_RIGHT additive_expression
        '''

    def p_relational_expression(self, p):
        '''relational_expression    : shift_expression
                                    | relational_expression '<' shift_expression
                                    | relational_expression '>' shift_expression
                                    | relational_expression COMP_LTEQ shift_expression
                                    | relational_expression COMP_GTEQ shift_expression
        '''

    def p_equality_expression(self, p):
        '''equality_expression  : relational_expression 
                                | equality_expression COMP_EQUAL relational_expression
                                | equality_expression COMP_NEQUAL relational_expression
        '''

    def p_and_expression(self, p):
        '''and_expression   : equality_expression
                            | and_expression '&' equality_expression
         '''

    def p_exclusive_or_expression(self, p):
        '''exclusive_or_expression  : and_expression
                                    | exclusive_or_expression '^' and_expression
        '''

    def p_inclusive_or_expression(self, p):
        '''inclusive_or_expression  : exclusive_or_expression
                                    | inclusive_or_expression '|' exclusive_or_expression
        '''

    def p_logical_and_expression(self, p):
        '''logical_and_expression   : inclusive_or_expression
                                    | logical_and_expression LOGIC_AND inclusive_or_expression
        '''

    def p_logical_or_expression(self, p):
        '''logical_or_expression    : logical_and_expression
                                    | logical_or_expression LOGIC_OR logical_and_expression
        '''

    def p_conditional_expression(self, p):
        '''conditional_expression   : logical_or_expression
                                    | logical_or_expression '?' expression ':' conditional_expression
        '''

    def p_assignment_expression(self, p):
        '''assignment_expression    : conditional_expression
                                    | unary_expression assignment_operator assignment_expression
        '''

    def p_assignment_operator(self, p):
        '''assignment_operator  : '='
                                | MUL_ASSIGN
                                | DIV_ASSIGN
                                | MOD_ASSIGN
                                | ADD_ASSIGN
                                | SUB_ASSIGN
                                | BIL_ASSIGN
                                | BIR_ASSIGN
                                | AND_ASSIGN
                                | XOR_ASSIGN
                                | OR_ASSIGN
        '''

    def p_expression(self, p):
        '''expression   : assignment_expression
                        | expression ',' assignment_expression
        '''

    def p_constant_expression(self, p):
        '''constant_expression : conditional_expression'''

    def p_declaration(self, p):
        '''declaration  : declaration_specifiers ';'
                        | declaration_specifiers init_declarator_list ';'
        '''

    def p_declaration_specifiers(self, p):
        '''declaration_specifiers   : type_specifier
                                    | type_specifier declaration_specifiers
                                    | type_qualifier
                                    | type_qualifier declaration_specifiers
        '''
        

    def p_init_declarator_list(self, p):
        '''init_declarator_list : init_declarator
                                | init_declarator_list ',' init_declarator
        '''

    def p_init_declarator(self, p):
        '''init_declarator  : declarator '='  initializer
                            | declarator 
        '''

    def p_type_specifier(self, p):
        '''type_specifier   : VOID
                            | INT
                            | FLOAT
                            | DOUBLE
                            | LONG
                            | CHAR
                            | SHORT
                            | SIGNED
                            | UNSIGNED
                            | BOOL
                            | struct_or_union_specifier
        '''
        

    def p_struct_or_union_specifier(self, p):
        '''struct_or_union_specifier    : struct_or_union '{' struct_declaration_list '}'
                                        | struct_or_union ID '{' struct_declaration_list '}'
                                        | struct_or_union ID
        '''

    def p_struct_or_union(self, p):
        '''struct_or_union  : STRUCT
                            | UNION
        '''

    def p_struct_declaration_list(self, p):
        '''struct_declaration_list  : struct_declaration
                                    | struct_declaration_list struct_declaration
     '''

    def p_struct_declaration(self, p):
        '''struct_declaration   : specifier_qualifier_list ';'
                                | specifier_qualifier_list struct_declarator_list ';'
        '''

    def p_specifier_qualifier_list(self, p):
        '''specifier_qualifier_list   : type_specifier specifier_qualifier_list
                                      | type_specifier
                                      | type_qualifier specifier_qualifier_list
                                      | type_qualifier
        '''

    def p_struct_declarator_list(self, p):
        '''struct_declarator_list   : struct_declarator
                                    | struct_declarator_list ',' struct_declarator
        '''

    def p_struct_declarator(self, p):
        '''struct_declarator   : ':' constant_expression
                               |  declarator ':' constant_expression
                               |  declarator
        '''

    def p_type_qualifier(self, p):
        '''type_qualifier   : CONST
                            | VOLATILE
        '''
        p[0] = p[1]

    def p_declarator(self, p):
        '''declarator   : pointer direct_declarator
                        | direct_declarator
        '''

    def p_direct_declarator(self, p):
        '''direct_declarator    : ID
                                | '(' declarator ')'
                                | direct_declarator '[' ']'
                                | direct_declarator '[' '*' ']'
                                | direct_declarator '[' type_qualifier_list '*' ']'
                                | direct_declarator '[' type_qualifier_list assignment_expression ']'
                                | direct_declarator '[' type_qualifier_list ']'
                                | direct_declarator '[' assignment_expression ']'
                                | direct_declarator '(' parameter_type_list ')'
                                | direct_declarator '(' ')'
                                | direct_declarator '(' identifier_list ')'
    '''

    def p_pointer(self, p):
        '''pointer  : '*' type_qualifier_list pointer
                    | '*' type_qualifier_list
                    | '*' pointer
                    | '*' 
        '''

    def p_type_qualifier_list(self, p):
        '''type_qualifier_list  : type_qualifier
                                | type_qualifier_list type_qualifier
        '''

    def p_parameter_type_list(self, p):
        '''parameter_type_list  : parameter_list

        '''
    #  parameter_list ',' ELLIPSIS

    def p_parameter_list(self, p):
        '''parameter_list   : parameter_declaration
                            | parameter_list ',' parameter_declaration
        '''

    def p_parameter_declaration(self, p):
        '''parameter_declaration    : declaration_specifiers declarator
                                    | declaration_specifiers abstract_declarator
                                    | declaration_specifiers
        '''

    def p_identifier_list(self, p):
        '''identifier_list  : ID
                            | identifier_list ',' ID
        '''

    def p_type_name(self, p):
        '''type_name    : specifier_qualifier_list abstract_declarator
                        | specifier_qualifier_list
        '''

    def p_abstract_declarator(self, p):
        '''abstract_declarator  : pointer direct_abstract_declarator
                                | pointer 
                                | direct_abstract_declarator
        '''

    def p_direct_abstract_declarator(self, p):
        '''direct_abstract_declarator   : '(' abstract_declarator ')'
                                        | '[' ']'
                                        | '[' '*' ']'
                                        | '[' type_qualifier_list ']'
                                        | '[' assignment_expression ']'
                                        | direct_abstract_declarator '[' ']'
                                        | direct_abstract_declarator '[' '*' ']'
                                        | direct_abstract_declarator '[' type_qualifier_list assignment_expression ']'
                                        | direct_abstract_declarator '[' type_qualifier_list ']'
                                        | direct_abstract_declarator '(' constant_expression ')'
                                        | direct_abstract_declarator '[' assignment_expression ']' 
                                        | '(' ')'
                                        | '(' parameter_type_list ')'
                                        | direct_abstract_declarator '(' ')'
                                        | direct_abstract_declarator '(' parameter_type_list ')'
        '''

    def p_initializer(self, p):
        '''initializer  : '{' initializer_list '}'
                        | '{' initializer_list ',' '}'   
                        | assignment_expression                             
        '''
        

    def p_initializer_list(self, p):
        '''initializer_list : initializer
                            | initializer_list ',' initializer
        '''
    # we are not implementing designation list

    def p_statement(self, p):
        '''statement    : labeled_statement
                        | compound_statement
                        | expression_statement
                        | selection_statement
                        | iteration_statement
                        | jump_statement
        '''

    def p_labeled_statement(self, p):
        '''labeled_statement    : ID ':' statement 
                                | CASE constant_expression ':' statement
                                | DEFAULT ':' statement
        '''

    def p_compound_statement(self, p):
        '''compound_statement   : '{' '}'
                                | '{' block_item_list '}'
        '''

    def p_block_item_list(self, p):
        '''block_item_list  : block_item
                            | block_item_list block_item
        '''

    def p_block_item(self, p):
        '''block_item   :  declaration
                        |  statement
        '''

    def p_expression_statement(self, p):
        '''expression_statement : ';'
                                | expression ';'
        '''

    def p_selection_statement(self, p):
        '''selection_statement  : IF '(' expression ')' statement ELSE statement
                                | IF '(' expression ')' statement
                                | SWITCH '(' expression ')' statement
        '''

    def p_iteration_statement(self, p):
        '''iteration_statement  : WHILE '(' expression ')' statement
                                | DO statement WHILE '(' expression ')' ';'
                                | FOR '(' expression_statement expression_statement ')' statement
                                | FOR '(' expression_statement expression_statement expression ')' statement  
                                | FOR '(' declaration expression_statement ')' statement
                                | FOR '(' declaration expression_statement expression ')' statement                                                
        '''

    def p_jump_statement(self, p):
        '''jump_statement   : GOTO ID ';'
                            | CONTINUE ';'
                            | BREAK ';'
                            | RETURN ';'
                            | RETURN expression ';'
        '''

    def p_translation_unit(self, p):
        '''translation_unit : external_declaration
                            | translation_unit external_declaration
        '''

    def p_external_declaration(self, p):
        '''external_declaration : function_definition
                                | declaration
                                | '#' DEFINE ID constant ';'
                                | '#' DEFINE ID CONST_STRING ';'
                                | '#' DEFINE ID '(' identifier_list ')' '(' expression ')' ';'
        '''
    
    def p_function_definition(self, p):
        '''function_definition  : declaration_specifiers declarator declaration_list compound_statement
                                | declaration_specifiers declarator compound_statement                                                                              
        '''

    def p_declaration_list(self, p):
        '''declaration_list : declaration
                            | declaration_list declaration
        '''

    def p_error(self, p):
        print("Syntax error in input!")

    def build(self, **kwargs):
        self.parser = yacc.yacc(
            start='translation_unit', module=self, **kwargs)

    def parse_inp(self, input):
        result = self.parser.parse(input)
        print(result)


# Build the parser
parser = CParser()
parser.build()
l = CLexer()
l.build()
for i in range(0, 1):
    try:
        s = open(sys.argv[1], 'r').read()
    except EOFError:
        break
    if not s:
        continue
    parser.parse_inp(s)
