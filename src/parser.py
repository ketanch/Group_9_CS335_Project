from ctypes.wintypes import INT
import ply.yacc as yacc
from lexer import *
import sys
import pydot
from classes import *
from symbolTab import symbolTable,global_stack,global_node
import json

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
        p[0] = Node(name='primary_expression', value=p[1],idName=p[1])
        if (p[0].idName not in global_node["variables"] and p[0].idName not in symbolTable.keys()):
            print("Identifier %s not defined at line = %d" % (p[0].idName, p.lineno(0)))

    def p_primary_expression_2(self, p):
        '''primary_expression   : constant
                                | '(' expression ')'
        '''
        p[0] = Node(name='primary_expression')
        if(len(p) == 2):
            p[0]=p[1]
            p[0].type = p[1].type
        else:
            p[0].children = p[0].children+[p[2]]
        # to look again FUNC_NAME in CONST_String

    def p_constant_1(self, p):
        '''constant : CONST_INT 
        '''
        p[0] = Node(name='constant', value = p[1], type = 'INT')

    def p_constant_2(self, p):
        '''constant : CONST_CHAR
        '''
        p[0] = Node(name='constant', value = p[1], type = 'CHAR')
    
    def p_constant_3(self, p):
        '''constant : CONST_FLOAT
        '''
        p[0] = Node(name='constant', value = p[1], type = 'FLOAT')

    def p_constant_4(self, p):
        '''constant : CONST_HEX
        '''
        p[0] = Node(name='constant', value = p[1], type = 'CONST_HEX')
    
    def p_constant_5(self, p):
        '''constant : CONST_OCT 
        '''
        p[0] = Node(name='constant', value = p[1], type = 'CONST_OCT')

    def p_constant_6(self, p):
        '''constant : CONST_BIN
        '''
        p[0] = Node(name='constant', value = p[1], type = 'CONST_BIN')
    
    def p_constant_7(self, p):
        '''constant : TRUE
        '''
        p[0] = Node(name='constant', value = p[1], type = 'TRUE')
    
    def p_constant_8(self, p):
        '''constant : FALSE  
        '''
        p[0] = Node(name='constant', value = p[1], type = 'FALSE')

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
            p[0]=p[1]
            p[0].type = p[1].type
        elif(len(p) == 5):
            p[0].children = p[0].children+[p[1], p[3]]
        elif(len(p) == 4):
            p[0]=p[1]
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
            p[0].children =p[1]
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
            p[0]=p[1]
            p[0].type = p[1].type
            #print("In unary", p[0].type)
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
            p[0] = p[1]
            p[0].type = p[1].type
            #print("GG", p[1].type)
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_additive_expression(self, p):
        '''additive_expression  : multiplicative_expression
                                | additive_expression '+' multiplicative_expression
                                | additive_expression '-' multiplicative_expression
        '''
        p[0] = Node(name='additive_expression')
        if(len(p) == 2):
            p[0].type = p[1].type
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]
            if p[1].type != p[3].type:
                pass
                #print("Implicit type casting not allowed between %s and %s at line %d" % (p[1].type, p[3].type, p.lineno(0)))
            p[0].type = p[1].type
            #print(p[1].type, "dfdf",p[3].type)

    def p_shift_expression(self, p):
        '''shift_expression : additive_expression
                            | shift_expression BIT_LEFT additive_expression
                            | shift_expression BIT_RIGHT additive_expression
        '''
        p[0] = Node(name='shift_expression')
        if(len(p) == 2):
            p[0]=p[1]
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
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_equality_expression(self, p):
        '''equality_expression  : relational_expression 
                                | equality_expression COMP_EQUAL relational_expression
                                | equality_expression COMP_NEQUAL relational_expression
        '''
        p[0] = Node(name='equality_expression')
        if(len(p) == 2):
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_and_expression(self, p):
        '''and_expression   : equality_expression
                            | and_expression '&' equality_expression
        '''
        p[0] = Node(name='and_expression')
        if(len(p) == 2):
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_exclusive_or_expression(self, p):
        '''exclusive_or_expression  : and_expression
                                    | exclusive_or_expression '^' and_expression
        '''
        p[0] = Node(name='exclusive_or_expression')
        if(len(p) == 2):
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_inclusive_or_expression(self, p):
        '''inclusive_or_expression  : exclusive_or_expression
                                    | inclusive_or_expression '|' exclusive_or_expression
        '''
        p[0] = Node(name='inclusive_or_expression')
        if(len(p) == 2):
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_logical_and_expression(self, p):
        '''logical_and_expression   : inclusive_or_expression
                                    | logical_and_expression LOGIC_AND inclusive_or_expression
        '''
        p[0] = Node(name='logical_and_expression')
        if(len(p) == 2):
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_logical_or_expression(self, p):
        '''logical_or_expression    : logical_and_expression
                                    | logical_or_expression LOGIC_OR logical_and_expression
        '''
        p[0] = Node(name='logical_or_expression')
        if(len(p) == 2):
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_conditional_expression(self, p):
        '''conditional_expression   : logical_or_expression
                                    | logical_or_expression '?' expression ':' conditional_expression
        '''
        p[0] = Node(name='conditional_expression')
        if(len(p) == 2):
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3], p[4], p[5]]

    def p_assignment_expression(self, p):
        '''assignment_expression    : conditional_expression
                                    | unary_expression assignment_operator assignment_expression
        '''
        p[0] = Node(name='assignment_expression')
        if(len(p) == 2):
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]
            p[0].idName=p[1].idName
            p[0].value=p[3].value

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
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_constant_expression(self, p):
        '''constant_expression : conditional_expression'''
        p[0] = Node(name='constant_expression')
        if(len(p) == 2):
            p[0]=p[1]

    # def p_declaration(self, p):
    #     '''declaration  : declaration_specifiers ';'
    #                     | declaration_specifiers init_declarator_list ';'
    #     '''
    #     p[0] = Node(name='declaration',type=p[1].type)
    #     if(len(p) == 3):
    #         p[0] =p[1]
    #     else:
    #         p[0].children = p[0].children+[p[1], p[2]]
    #         p[0].value=p[2].value
    #         p[0].idName=p[2].idName
    def p_declaration(self, p):
        '''declaration  : declaration_specifiers ';'
                         | declaration_specifiers init_declarator_list ';'
        '''
        p[0] = Node(name='declaration',type=p[1].type)
        if(len(p) == 3):
            p[0] =p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]
            p[0].value=p[2].value
            p[0].idName=p[2].idName
        global global_node
        #print(p[0].type, p[2].type)
        # if p[0].type.lower() != p[2].type.lower():
        #     print("Type casting from %s to %s not allowed at line = %d" % (p[2].type.lower(), p[0].type.lower(), p.lineno(0)))
        
        if(len(global_stack)==0):
            if p[0].idName in global_node["global_variables"].keys():
                print("Variable redefined at line = %d" % (p.lineno(1)))
                raise SyntaxError
                exit(-1)
            global_node["global_variables"][p[0].idName]={}
            global_node["global_variables"][p[0].idName]["value"]=p[0].value
        else:
            if p[0].idName in global_node["variables"].keys():
                print("Variable redefined at line = %d" % (p.lineno(1)))
                raise SyntaxError
                exit(-1)
            global_node["variables"][p[0].idName]={}
            global_node["variables"][p[0].idName]["value"]=p[0].value

    def p_declaration_specifiers(self, p):
        '''declaration_specifiers   : type_specifier
                                    | type_qualifier
                                    | type_qualifier declaration_specifiers
        '''
        p[0] = Node(name='declaration_specifiers',type=p[1].type)
        if(len(p) == 2):
            # p[0].children = p[0].children+[p[1]]
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_init_declarator_list(self, p):
        '''init_declarator_list : init_declarator
                                | init_declarator_list ',' init_declarator
        '''
        p[0] = Node(name='init_declarator_list')
        if(len(p) == 2):
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_init_declarator(self, p):
        '''init_declarator  : declarator '='  initializer
                            | declarator 
        '''
        p[0] = Node(name='init_declarator')
        p[0].idName=p[1]
        if(len(p) == 2):
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1],p[2], p[3]]
            p[0].value=p[3].value
            p[0].idName=p[1].idName
            p[0].type = p[3].type
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
        p[0]=p[1]

    def p_struct_or_union_specifier(self, p):
        '''struct_or_union_specifier    : struct_or_union '{' struct_declaration_list '}'
                                        | struct_or_union ID '{' struct_declaration_list '}'
                                        | struct_or_union ID
        '''
        p[0] = Node(name='struct_or_union_specifier',type=p[1])
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
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_struct_declaration(self, p):
        '''struct_declaration   : specifier_qualifier_list ';'
                                | specifier_qualifier_list struct_declarator_list ';'
        '''
        p[0] = Node(name='struct_declaration')
        if(len(p) == 3):
            p[0]=p[1]
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
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_struct_declarator_list(self, p):
        '''struct_declarator_list   : struct_declarator
                                    | struct_declarator_list ',' struct_declarator
        '''
        p[0] = Node(name='struct_declarator_list')
        if(len(p) == 2):
            p[0]=p[1]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_struct_declarator(self, p):
        '''struct_declarator   : ':' constant_expression
                               |  declarator ':' constant_expression
                               |  declarator
        '''
        p[0] = Node(name='struct_declaration')
        if(len(p) == 2):
            p[0]=p[1]
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
            p[0]=p[1]
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
            p[0].idName=p[1]
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
        p[0] = Node(name='direct_declarator',idName=p[1].idName)
        if(len(p) == 4):
            p[0]=p[1]
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
            p[0]=p[1]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]

    def p_parameter_type_list(self, p):
        '''parameter_type_list  : parameter_list

        '''
        p[0] = Node(name='parameter_type_list')
        if(len(p) == 2):
            p[0]=p[1]
    #  parameter_list ',' ELLIPSIS

    def p_parameter_list(self, p):
        '''parameter_list   : parameter_declaration
                            | parameter_list ',' parameter_declaration
        '''
        p[0] = Node(name='parameter_list')
        if(len(p) == 2):
            p[0]=p[1]
        elif(len(p) == 4):
            p[0].children = p[0].children+[p[1], p[3]]

    def p_parameter_declaration(self, p):
        '''parameter_declaration    : declaration_specifiers declarator
                                    | declaration_specifiers abstract_declarator
                                    | declaration_specifiers
        '''
        p[0] = Node(name='parameter_declaration',type=p[1].type)
        if(len(p) == 2):
            p[0]=p[1]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]
            p[0].idName=p[2].idName

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
            p[0]=p[1]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]

    def p_abstract_declarator(self, p):
        '''abstract_declarator  : pointer direct_abstract_declarator
                                | pointer 
                                | direct_abstract_declarator
        '''
        p[0] = Node(name='abstract_declarator')
        if(len(p) == 2):
            p[0]=p[1]
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
            p[0]=p[1]

    def p_initializer(self, p):
        '''initializer  : '{' initializer_list '}'
                        | '{' initializer_list ',' '}'   
                        | assignment_expression                             
        '''
        p[0] = Node(name='initializer')
        if(len(p) == 4):
            p[0]=p[2]
        else:
            p[0]=p[1]

    def p_initializer_list(self, p):
        '''initializer_list : initializer
                            | initializer_list ',' initializer
        '''
        p[0] = Node(name='initializer_list')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[1], p[3]]
        else:
            p[0]=p[1]
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
        p[0]=p[1]

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
            p[0]=p[1]

    def p_block_item(self, p):
        '''block_item   :  declaration
                        |  statement
        '''
        p[0] = Node(name='block_item')
        p[0]=p[1]

    def p_expression_statement(self, p):
        '''expression_statement : ';'
                                | expression ';'
        '''
        p[0] = Node(name='expression_statement')
        if(len(p) == 3):
            p[0]=p[1]

    def p_selection_statement(self, p):
        '''selection_statement  : IF '(' expression ')' MARKER1 statement MARKER2 ELSE MARKER1 statement MARKER2
                                | IF '(' expression ')' MARKER1 statement MARKER2
                                | SWITCH '(' expression ')'  statement 
        '''
        p[0] = Node(name='selection_statement')
        if(len(p) == 6):
            p[0].children = p[0].children+[p[1], p[3], p[5]]
        elif(len(p)==8):
            p[0].children = p[0].children+[p[1], p[3], p[6]]
        else:
            p[0].children = p[0].children+[p[1], p[3], p[6],p[8],p[10]]

    def p_MARKER1(self,p):
        ''' MARKER1 : '''
        global global_node
        tmp="if"+str(len(global_stack))
        global_node[tmp]={"variables":{}}
        global_stack.append(global_node)
        global_node=global_node["if"+str(len(global_stack)-1)]

    def p_MARKER2(self,p):
        ''' MARKER2 : '''
        global global_node
        # global_node["if"+str(len(global_stack))]={}
        global_node=global_stack.pop()
        # global_node=global_node["if"+str(len(global_stack)-1)]
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

    def p_jump_statement_1(self, p):
        '''jump_statement   : GOTO ID ';'
                            | CONTINUE ';'
                            | BREAK ';'
                            | RETURN expression ';'
        '''
        p[0] = Node(name='jump_statement')
        if(len(p) == 3):
            p[0].value = p[1]
        elif len(p) == 4:
            p[0].children = p[0].children+[p[1], p[2]]
            ret_type = global_node["func_parameters"]["return_type"].lower()
            if p[2].type.lower() != ret_type:
                print("Return type mismatch at line %d. Function return type is %s whereas returning %s" % (p.lineno(0), ret_type, p[2].type.lower()))
        #else:
        #    p[0].children = p[0].children+[p[1], p[2]]

    def p_jump_statement_2(self, p):
        '''jump_statement   : RETURN ';'
        '''
        p[0] = Node(name='jump_statement')
        p[0].value = p[1]
        ret_type = global_node["func_parameters"]["return_type"].lower()
        if 'void' != ret_type:
            print("Return type mismatch at line %d. Function return type is %s whereas returning void" % (p.lineno(0), ret_type))

    def p_translation_unit(self, p):
        '''translation_unit : external_declaration
                            | translation_unit external_declaration
        '''
        p[0] = Node(name='translation_unit')
        if(len(p) == 2):
            p[0]=p[1]
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
            p[0]=p[1]
        elif(len(p) == 5):
            p[0].children = p[0].children+[p[1], p[2], p[3], p[4]]
            p[0].idName=p[3]
            try:
                p[0].value=p[4].value
            except:
                p[0].value=p[4]
            # print(type(p[0].value))
            symbolTable["global_variables"][p[0].idName]={
                "value":p[0].value,
                "type":'int',
                "scope":0,
                "line_no":0,
                "isMacro":1,
                "isConst":1
            }
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3], p[5], p[8]]
            p[0].idName=p[3]

    
    # See if declaration_list is required
    # def p_function_definition(self, p):
    #     '''function_definition  : declaration_specifiers declarator declaration_list compound_statement
    #                             | declaration_specifiers declarator compound_statement  

    #     '''
    #     p[0] = Node(name='function_definition')
    #     if(len(p) == 4):
    #         p[0].children = p[0].children+[p[1], p[2], p[3]]
    #     else:
    #         p[0].children = p[0].children+[p[1], p[2], p[3], p[4]]
    def p_function_definition_init(self,p):
        '''function_definition_init : declaration_specifiers declarator'''
        global global_node
        p[0] = Node(name='function_definition_init',type=p[1].type,idName=p[2].idName)
        
        # If there are arguments
        try:
            root=p[2].children[1]
            numberArgs=len(root.children)
            global_node[p[0].idName]={
                "func_parameters":{
                    "number_args":numberArgs,
                    "arguments":{},
                    "return_type":p[0].type,
                    "scope":0
                },
                "variables":{}
            }
            for child in root.children:
                symbolTable[p[0].idName]["func_parameters"]["arguments"][child.idName]=child.type
        except:
            #print(global_node)
            global_node[p[0].idName]={
                "func_parameters":{
                    "number_args":0,
                    "arguments":{},
                    "return_type":p[0].type,
                    "scope":0
                },
                "variables":{}
            }
        
        p[0].children = p[0].children+[p[1], p[2]]
        global_stack.append(global_node)
        global_node=global_node[p[0].idName]

    def p_function_definition(self, p):
        '''function_definition  : function_definition_init ';' MARKER2 
                                | function_definition_init compound_statement MARKER2  

        '''
        p[0] = Node(name='function_definition',type=p[1].type,idName=p[1].idName)
        p[0].children+=[p[1],p[2]]
        #print(symbolTable["func"])

    def p_declaration_list(self, p):
        '''declaration_list : declaration
                            | declaration_list declaration
        '''
        p[0] = Node(name='declaration_list')
        if(len(p) == 2):
            p[0] =p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    #def find_column(self, input, token):
    #    line_start = input.rfind('\n', 0, token.lexpos) + 1
    #    return (token.lexpos - line_start) + 1
    
    def p_error(self, p):
        if (p == None):
            print("EOF tokens.")
        print(p, type(p))
        # print(p.lineno, self.find_column(p.lexpos))
        print("Syntax error in input!")

    def build(self, **kwargs):
        self.parser = yacc.yacc(
            start='translation_unit', module=self, **kwargs)
    
    def dfs (self,node,dot_data_label,dot_data_translation,i):
        if(isinstance(node,str)):
            dot_data_label+=f'\t{i} [label="{node}" color=red];\n'
            parent_i=i
            i+=1
            # dot_data_label+=f'\t{i} [label="{node.value}"];\n'
            # dot_data_translation+=f'\t{parent_i}->{i};\n'
            return dot_data_label,dot_data_translation,i

        if(node==None):
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
        # print(symbolTable)

    def parse_inp(self, input):
        result = self.parser.parse(input, tracking = True)
        if "main" not in symbolTable.keys():
            print("'main' function not present.")
            exit(1)
        print("Parsing completed successfully")
        # print(result)
        self.generate_dot_ast(result)
        self.generate_dot()
        #print(json.dumps(symbolTable,indent=2))
        # print(symbolTable)

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
        #open('src/graph_file.dot', 'w').write(dot_data)
        #graphs = pydot.graph_from_dot_data(dot_data)
        #graph = graphs[0]
        #graph.write_png('graph.png')
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