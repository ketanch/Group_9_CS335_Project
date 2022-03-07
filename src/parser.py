import ply.yacc as yacc
from lexer import *
import sys
import pydot
from classes import *


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

    def p_primary_expression_1(self, p):
        '''primary_expression   : ID
                                | CONST_STRING  
        '''
        p[0] = Node(name='primary_expression', value=p[1])

    def p_primary_expression_2(self, p):
        '''primary_expression   : constant
                                | '(' expression ')'
        '''
        p[0] = Node(name='primary_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[2]]
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
        p[0] = Node(name='constant', value=p[1])
        # p[0] = p[1]

    def p_postfix_expression_1(self, p):
        '''postfix_expression   : primary_expression
                                | postfix_expression '[' expression ']'
                                | postfix_expression '(' ')'
                                | postfix_expression '(' argument_expression_list ')'
                                | postfix_expression ADDU
                                | postfix_expression SUBU
                                | '(' type_name ')' '{' initializer_list '}'
                                | '(' type_name ')' '{' initializer_list ',' '}'
        '''
        p[0] = Node(name='postfix_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        elif(len(p) == 5):
            p[0].children = p[0].children+[p[1], p[3]]
        elif(len(p) == 4):
            p[0].children = p[0].children+[p[1]]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]
        elif(len(p) == 7):
            p[0].children = p[0].children+[p[2], p[5]]
        else:
            p[0].children = p[0].children+[p[2], p[5]]

    def p_postfix_expression_2(self, p):
        '''postfix_expression   : postfix_expression '.' ID
                                | postfix_expression MEMB_ACCESS ID
        '''
        p[0] = Node(name='postfix_expression')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_argument_expression_list(self, p):
        '''argument_expression_list : assignment_expression
                                    | argument_expression_list ',' assignment_expression
        '''
        p[0] = Node(name='argument_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_unary_expression(self, p):
        '''unary_expression : postfix_expression
                            | ADDU unary_expression
                            | SUBU unary_expression
                            | unary_operator unary_expression
                            | SIZEOF unary_expression
                            | SIZEOF '(' type_name ')'
        '''
        p[0] = Node(name='unary_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        elif((len(p) == 3)):
            p[0].children = p[0].children+[p[1], p[2]]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_unary_operator(self, p):
        '''unary_operator   : '&'
                            | '*'
                            | '+'
                            | '-'
                            | '~'
                            | '!'                      
        '''
        p[0] = Node(name='unary_operator', value=p[1])

    def p_multipicative_expression(self, p):
        '''multiplicative_expression    : unary_expression
                                        | multiplicative_expression '*' unary_expression
                                        | multiplicative_expression '/' unary_expression
                                        | multiplicative_expression '%' unary_expression
        '''
        p[0] = Node(name='multipicative_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_additive_expression(self, p):
        '''additive_expression  : multiplicative_expression
                                | additive_expression '+' multiplicative_expression
                                | additive_expression '-' multiplicative_expression
        '''
        p[0] = Node(name='additive_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_shift_expression(self, p):
        '''shift_expression : additive_expression
                            | shift_expression BIT_LEFT additive_expression
                            | shift_expression BIT_RIGHT additive_expression
        '''
        p[0] = Node(name='shift_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_relational_expression(self, p):
        '''relational_expression    : shift_expression
                                    | relational_expression '<' shift_expression
                                    | relational_expression '>' shift_expression
                                    | relational_expression COMP_LTEQ shift_expression
                                    | relational_expression COMP_GTEQ shift_expression
        '''
        p[0] = Node(name='relational_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_equality_expression(self, p):
        '''equality_expression  : relational_expression 
                                | equality_expression COMP_EQUAL relational_expression
                                | equality_expression COMP_NEQUAL relational_expression
        '''
        p[0] = Node(name='equality_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_and_expression(self, p):
        '''and_expression   : equality_expression
                            | and_expression '&' equality_expression
        '''
        p[0] = Node(name='and_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_exclusive_or_expression(self, p):
        '''exclusive_or_expression  : and_expression
                                    | exclusive_or_expression '^' and_expression
        '''
        p[0] = Node(name='exclusive_or_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_inclusive_or_expression(self, p):
        '''inclusive_or_expression  : exclusive_or_expression
                                    | inclusive_or_expression '|' exclusive_or_expression
        '''
        p[0] = Node(name='inclusive_or_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_logical_and_expression(self, p):
        '''logical_and_expression   : inclusive_or_expression
                                    | logical_and_expression LOGIC_AND inclusive_or_expression
        '''
        p[0] = Node(name='logical_and_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_logical_or_expression(self, p):
        '''logical_or_expression    : logical_and_expression
                                    | logical_or_expression LOGIC_OR logical_and_expression
        '''
        p[0] = Node(name='logical_or_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_conditional_expression(self, p):
        '''conditional_expression   : logical_or_expression
                                    | logical_or_expression '?' expression ':' conditional_expression
        '''
        p[0] = Node(name='conditional_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3], p[4], p[5]]

    def p_assignment_expression(self, p):
        '''assignment_expression    : conditional_expression
                                    | unary_expression assignment_operator assignment_expression
        '''
        p[0] = Node(name='assignment_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

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
        p[0] = Node(name='assignment_operator', value=p[1])

    def p_expression(self, p):
        '''expression   : assignment_expression
                        | expression ',' assignment_expression
        '''
        p[0] = Node(name='expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_constant_expression(self, p):
        '''constant_expression : conditional_expression'''
        p[0] = Node(name='constant_expression')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]

    def p_declaration(self, p):
        '''declaration  : declaration_specifiers ';'
                        | declaration_specifiers init_declarator_list ';'
        '''
        p[0] = Node(name='declaration')
        if(len(p) == 3):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_declaration_specifiers(self, p):
        '''declaration_specifiers   : type_specifier
                                    | type_specifier declaration_specifiers
                                    | type_qualifier
                                    | type_qualifier declaration_specifiers
        '''
        p[0] = Node(name='declaration_specifiers')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_init_declarator_list(self, p):
        '''init_declarator_list : init_declarator
                                | init_declarator_list ',' init_declarator
        '''
        p[0] = Node(name='init_declarator_list')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_init_declarator(self, p):
        '''init_declarator  : declarator '='  initializer
                            | declarator 
        '''
        p[0] = Node(name='init_declarator')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[3]]
        # print(p[3].children[0].children[0].children[0].children[0].children[0].children[0].children[0].children[0].children[0].children[0].children[0].children[0].children[0].children[0].children[0].children[0].value)

    def p_type_specifier_1(self, p):
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
        '''
        p[0] = Node(name='type_specifier', type=p[1],value=p[1])
    
    def p_type_specifier_2(self, p):
        '''type_specifier   : struct_or_union_specifier
        '''
        p[0] = Node(name='type_specifier')
        p[0].children=p[1]

    def p_struct_or_union_specifier(self, p):
        '''struct_or_union_specifier    : struct_or_union '{' struct_declaration_list '}'
                                        | struct_or_union ID '{' struct_declaration_list '}'
                                        | struct_or_union ID
        '''
        p[0] = Node(name='struct_or_union_specifier')
        if(len(p) == 5):
            p[0].children = p[0].children+[p[1], p[3]]
        elif(len(p) == 6):
            p[0].children = p[0].children+[p[1], p[2], p[4]]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_struct_or_union(self, p):
        '''struct_or_union  : STRUCT
                            | UNION
        '''
        p[0] = Node(name='struct_or_union', type=p[1],value=p[1])

    def p_struct_declaration_list(self, p):
        '''struct_declaration_list  : struct_declaration
                                    | struct_declaration_list struct_declaration
        '''
        p[0] = Node(name='struct_declaration_list')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_struct_declaration(self, p):
        '''struct_declaration   : specifier_qualifier_list ';'
                                | specifier_qualifier_list struct_declarator_list ';'
        '''
        p[0] = Node(name='struct_declaration')
        if(len(p) == 3):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_specifier_qualifier_list(self, p):
        '''specifier_qualifier_list   : type_specifier specifier_qualifier_list
                                      | type_specifier
                                      | type_qualifier specifier_qualifier_list
                                      | type_qualifier
        '''
        p[0] = Node(name='specifier_qualifier_list')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_struct_declarator_list(self, p):
        '''struct_declarator_list   : struct_declarator
                                    | struct_declarator_list ',' struct_declarator
        '''
        p[0] = Node(name='struct_declarator_list')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_struct_declarator(self, p):
        '''struct_declarator   : ':' constant_expression
                               |  declarator ':' constant_expression
                               |  declarator
        '''
        p[0] = Node(name='struct_declaration')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[2]]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_type_qualifier(self, p):
        '''type_qualifier   : CONST
                            | VOLATILE
        '''
        p[0] = Node(name='type_qualifier', value=p[1])

    def p_declarator(self, p):
        '''declarator   : pointer direct_declarator
                        | direct_declarator
        '''
        p[0] = Node(name='declarator')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_direct_declarator_1(self, p):
        '''direct_declarator    : MAIN
                                | ID
                                | '(' declarator ')'
        '''
        p[0] = Node(name='direct_declarator')
        if(len(p) == 2):
            p[0].value = p[1]
        if(len(p) == 4):
            p[0].children = p[0].children+[p[2]]

    # def p_direct_declarator_2(self, p):
    #     '''direct_declarator    : direct_declarator '[' ']'
    #                             | direct_declarator '[' '*' ']'
    #                             | direct_declarator '[' type_qualifier_list '*' ']'
    #                             | direct_declarator '[' type_qualifier_list assignment_expression ']'
    #                             | direct_declarator '[' type_qualifier_list ']'
    #                             | direct_declarator '[' assignment_expression ']'
    #                             | direct_declarator '(' parameter_type_list ')'
    #                             | direct_declarator '(' ')'
    #                             | direct_declarator '(' identifier_list ')'
    #     '''
    #     p[0] = Node(name='direct_declarator')
    #     if(len(p) == 4):
    #         p[0].children=p[0].children+[p[1]]
    def p_direct_declarator_2(self, p):
        '''direct_declarator    : direct_declarator '[' ']'
                                | direct_declarator '[' type_qualifier_list assignment_expression ']'
                                | direct_declarator '[' type_qualifier_list ']'
                                | direct_declarator '[' assignment_expression ']'
                                | direct_declarator '(' parameter_type_list ')'
                                | direct_declarator '(' ')'
                                | direct_declarator '(' identifier_list ')'
        '''
        p[0] = Node(name='direct_declarator')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[1]]
        elif(len(p) == 6):
            p[0].children = p[0].children+[p[1], p[2], p[4]]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_pointer(self, p):
        '''pointer  : '*' type_qualifier_list pointer
                    | '*' type_qualifier_list
                    | '*' pointer
                    | '*' 
        '''
        p[0] = Node(name='pointer')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[2], p[3]]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[2]]

    def p_type_qualifier_list(self, p):
        '''type_qualifier_list  : type_qualifier
                                | type_qualifier_list type_qualifier
        '''
        p[0] = Node(name='type_qualifier')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]

    def p_parameter_type_list(self, p):
        '''parameter_type_list  : parameter_list

        '''
        p[0] = Node(name='parameter_type_list')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
    #  parameter_list ',' ELLIPSIS

    def p_parameter_list(self, p):
        '''parameter_list   : parameter_declaration
                            | parameter_list ',' parameter_declaration
        '''
        p[0] = Node(name='parameter_list')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        elif(len(p) == 4):
            p[0].children = p[0].children+[p[1], p[3]]

    def p_parameter_declaration(self, p):
        '''parameter_declaration    : declaration_specifiers declarator
                                    | declaration_specifiers abstract_declarator
                                    | declaration_specifiers
        '''
        p[0] = Node(name='parameter_declaration')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]

    def p_identifier_list(self, p):
        '''identifier_list  : ID
                            | identifier_list ',' ID
        '''
        p[0] = Node(name='identifier_list')
        if(len(p) == 2):
            p[0].value = p[1]
        elif(len(p) == 4):
            p[0].children = p[0].children+[p[1], p[3]]

    def p_type_name(self, p):
        '''type_name    : specifier_qualifier_list abstract_declarator
                        | specifier_qualifier_list
        '''
        p[0] = Node(name='type_name')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]

    def p_abstract_declarator(self, p):
        '''abstract_declarator  : pointer direct_abstract_declarator
                                | pointer 
                                | direct_abstract_declarator
        '''
        p[0] = Node(name='abstract_declarator')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]

    # def p_direct_abstract_declarator(self, p):
    #     '''direct_abstract_declarator   : '(' abstract_declarator ')'
    #                                     | '[' ']'
    #                                     | '[' '*' ']'
    #                                     | '[' type_qualifier_list ']'
    #                                     | '[' assignment_expression ']'
    #                                     | direct_abstract_declarator '[' ']'
    #                                     | direct_abstract_declarator '[' '*' ']'
    #                                     | direct_abstract_declarator '[' type_qualifier_list assignment_expression ']'
    #                                     | direct_abstract_declarator '[' type_qualifier_list ']'
    #                                     | direct_abstract_declarator '(' constant_expression ')'
    #                                     | direct_abstract_declarator '[' assignment_expression ']'
    #                                     | '(' ')'
    #                                     | '(' parameter_type_list ')'
    #                                     | direct_abstract_declarator '(' ')'
    #                                     | direct_abstract_declarator '(' parameter_type_list ')'
    #     '''
    #     p[0] = Node(name='parameter_list')
    #     if(len(p) == 2):
    #         p[0].children = p[0].children+[p[1]]
    #     elif(len(p) == 4):
    #         p[0].children = p[0].children+[p[1],p[3]]

    def p_direct_abstract_declarator_1(self, p):
        '''direct_abstract_declarator   : '(' abstract_declarator ')'
                                        | '[' ']'
                                        | '[' type_qualifier_list ']'
                                        | '[' assignment_expression ']'
                                        | direct_abstract_declarator '[' type_qualifier_list assignment_expression ']'
                                        | direct_abstract_declarator '[' type_qualifier_list ']'
                                        | direct_abstract_declarator '(' constant_expression ')'
                                        | direct_abstract_declarator '[' assignment_expression ']' 
                                        | '(' ')'
                                        | '(' parameter_type_list ')'
                                        | direct_abstract_declarator '(' parameter_type_list ')'
        '''
        p[0] = Node(name='parameter_list')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[2]]
        elif(len(p) == 6):
            p[0].children = p[0].children+[p[1], p[3], p[4]]
        elif(len(p) == 5):
            p[0].children = p[0].children+[p[1], p[3]]

    def p_direct_abstract_declarator_2(self, p):
        '''direct_abstract_declarator   : direct_abstract_declarator '[' ']'
                                        | direct_abstract_declarator '(' ')'
        '''
        p[0] = Node(name='parameter_list')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[1]]

    def p_initializer(self, p):
        '''initializer  : '{' initializer_list '}'
                        | '{' initializer_list ',' '}'   
                        | assignment_expression                             
        '''
        p[0] = Node(name='initializer')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[2]]
        else:
            p[0].children = p[0].children+[p[1]]

    def p_initializer_list(self, p):
        '''initializer_list : initializer
                            | initializer_list ',' initializer
        '''
        p[0] = Node(name='initializer_list')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[1], p[3]]
        else:
            p[0].children = p[0].children+[p[1]]
    # we are not implementing designation list

    def p_statement(self, p):
        '''statement    : labeled_statement
                        | compound_statement
                        | expression_statement
                        | selection_statement
                        | iteration_statement
                        | jump_statement
        '''
        p[0] = Node(name='statement')
        p[0].children = p[0].children+[p[1]]

    def p_labeled_statement(self, p):
        '''labeled_statement    : ID ':' statement 
                                | CASE constant_expression ':' statement
                                | DEFAULT ':' statement
        '''
        p[0] = Node(name='labeled_statement')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[1], p[3]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[4]]

    def p_compound_statement(self, p):
        '''compound_statement   : '{' '}'
                                | '{' block_item_list '}'
        '''
        p[0] = Node(name='compound_statement')
        p[0].children = p[0].children+[p[2]]

    def p_block_item_list(self, p):
        '''block_item_list  : block_item
                            | block_item_list block_item
        '''
        p[0] = Node(name='block_item_list')
        if(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]
        else:
            p[0].children = p[0].children+[p[1]]

    def p_block_item(self, p):
        '''block_item   :  declaration
                        |  statement
        '''
        p[0] = Node(name='block_item')
        p[0].children = p[0].children+[p[1]]

    def p_expression_statement(self, p):
        '''expression_statement : ';'
                                | expression ';'
        '''
        p[0] = Node(name='expression_statement')
        if(len(p) == 3):
            p[0].children = p[0].children+[p[1]]

    def p_selection_statement(self, p):
        '''selection_statement  : IF '(' expression ')' statement ELSE statement
                                | IF '(' expression ')' statement
                                | SWITCH '(' expression ')' statement
        '''
        p[0] = Node(name='selection_statement')
        if(len(p) == 6):
            p[0].children = p[0].children+[p[1], p[3], p[5]]
        else:
            p[0].children = p[0].children+[p[1], p[3], p[5], p[6], p[7]]

    def p_iteration_statement_1(self, p):
        '''iteration_statement  : WHILE '(' expression ')' statement
                                | DO statement WHILE '(' expression ')' ';'
                                | FOR '(' expression_statement expression_statement ')' statement
                                | FOR '(' declaration expression_statement ')' statement
                                | FOR '(' declaration expression_statement expression ')' statement                                                
        '''
        p[0] = Node(name='iteration_statement')
        if(len(p) == 6):
            p[0].children = p[0].children+[p[1], p[3], p[5]]
        elif(len(p) == 8):
            p[0].children = p[0].children+[p[1], p[2], p[3], p[5]]
        elif(len(p) == 7):
            p[0].children = p[0].children+[p[1], p[3], p[4], p[6]]

    def p_iteration_statement_2(self, p):
        '''iteration_statement  : FOR '(' expression_statement expression_statement expression ')' statement                                                 
        '''
        p[0] = Node(name='iteration_statement')
        if(len(p) == 8):
            p[0].children = p[0].children+[p[1], p[3], p[4], p[5], p[7]]

    def p_jump_statement(self, p):
        '''jump_statement   : GOTO ID ';'
                            | CONTINUE ';'
                            | BREAK ';'
                            | RETURN ';'
                            | RETURN expression ';'
        '''
        p[0] = Node(name='jump_statement')
        if(len(p) == 3):
            p[0].value = p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_translation_unit(self, p):
        '''translation_unit : external_declaration
                            | translation_unit external_declaration
        '''
        p[0] = Node(name='translation_unit')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_external_declaration(self, p):
        '''external_declaration : function_definition
                                | declaration
                                | '#' DEFINE ID constant
                                | '#' DEFINE ID CONST_STRING
                                | '#' DEFINE ID '(' identifier_list ')' '(' expression ')'
        '''
        p[0] = Node(name='external_declaration')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        elif(len(p) == 5):
            p[0].children = p[0].children+[p[1], p[2], p[3], p[4]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3], p[5], p[8]]

    def p_function_definition(self, p):
        '''function_definition  : declaration_specifiers declarator declaration_list compound_statement
                                | declaration_specifiers declarator compound_statement  

        '''
        p[0] = Node(name='function_definition')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[1], p[2], p[3]]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3], p[4]]

    def p_declaration_list(self, p):
        '''declaration_list : declaration
                            | declaration_list declaration
        '''
        p[0] = Node(name='declaration_list')
        if(len(p) == 2):
            p[0].children = p[0].children+[p[1]]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_error(self, p):
        print("Syntax error in input!")

    def build(self, **kwargs):
        self.parser = yacc.yacc(
            start='translation_unit', module=self, **kwargs)
    
    def dfs (self,node,dot_data_label,dot_data_translation,i):
        print(type(node))
        if(isinstance(node,str)):
            dot_data_label+=f'\t{i} [label="{node}" color=red];\n'
            parent_i=i
            i+=1
            # dot_data_label+=f'\t{i} [label="{node.value}"];\n'
            # dot_data_translation+=f'\t{parent_i}->{i};\n'
            return dot_data_label,dot_data_translation,i


        dot_data_label+=f'\t{i} [label="{node.name}"];\n'
        parent_i=i
        i+=1
        if(len(node.children)==0):
            dot_data_label+=f'\t{i} [label="{node.value}" color=red];\n'
            dot_data_translation+=f'\t{parent_i}->{i};\n'
            i+=1
        for child in node.children:
            dot_data_translation+=f'\t{parent_i}->{i};\n'
            dot_data_label,dot_data_translation,i=self.dfs(child,dot_data_label,dot_data_translation,i)
            
        return dot_data_label,dot_data_translation,i

    def generate_dot_ast(self,root):
        dot_data_label = 'digraph DFA {\n'
        dot_data_translation=''
        dot_data_label,dot_data_translation,i=self.dfs(root,dot_data_label,dot_data_translation,0)
        final_dot=dot_data_label + dot_data_translation + '}\n'
        open('src/ast_graph_file.dot', 'w').write(final_dot)

    def parse_inp(self, input):
        result = self.parser.parse(input)
        print("Parsing completed successfully")
        print(result)
        self.generate_dot_ast(result)
        self.generate_dot()

    def generate_dot(self):
        dot_data = 'digraph DFA {\n'
        goto_t = self.parser.goto
        action_t = self.parser.action
        max_state = max(max(goto_t.keys()), max(action_t.keys()))
        for i in range(max_state):
            dot_data += f'\t{i} [label="I{i}"];\n'

        for state1, edges in goto_t.items():
            for label, state2 in edges.items():
                dot_data += f'\t{state1} -> {state2} [label="{label}" color=red];\n'

        for state1, edges in action_t.items():
            for label, state2 in edges.items():
                if state2 >= 0:
                    dot_data += f'\t{state1} -> {state2} [label="{label}" color=green];\n'

        dot_data += '}\n'
        # print(dot_data)
        open('src/graph_file.dot', 'w').write(dot_data)
        #graphs = pydot.graph_from_dot_data(dot_data)
        #graph = graphs[0]
        # graphs.write_png('graph.png')
        # print("DONE")
    
    
        



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
