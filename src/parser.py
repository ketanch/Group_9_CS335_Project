from pprint import pprint
from code_gen import gen_var_offset, generate_final_code, variable_optimize
import ply.yacc as yacc
from lexer import *
import sys
import pydot
from classes import *
from symbolTab import *
import json
from helper import *
var_cnt = 0
label_cnt = 0
switch_label = []
switch_expr = []
return_stack = []
break_label_stack = []
continue_label_stack=[]
struct_name="123"
unknown_struct_cnt=0
scope_count=0



def create_new_var():
    global var_cnt
    out = '__var_' + str(var_cnt)
    var_cnt += 1
    return out

def create_new_struct_name():
    global unknown_struct_cnt
    out = '__struct_' + str(unknown_struct_cnt)
    unknown_struct_cnt += 1
    return out

def create_new_label():
    global label_cnt
    out = '__label_' + str(label_cnt)
    label_cnt += 1
    return out


class CParser:

    tokens = CLexer.tokens
    literals = CLexer.literals
    #reserved = CLexer.reserved

    precedence = (
        # ('nonassoc','PID'),
        ('left', 'LOGIC_OR'),
        ('left', 'LOGIC_AND'),
        ('left', '|'),
        ('left', '^'),
        ('left', '&'),
        ('left', 'COMP_EQUAL', 'COMP_NEQUAL'),
        ('left', '>', 'COMP_GTEQ', '<', 'COMP_LTEQ'),
        ('left', 'BIT_RIGHT', 'BIT_LEFT'),
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
        # ('nonassoc','MAN')
    )

    def p_primary_expression_1(self, p):
        '''primary_expression   : ID
                               | CONST_STRING  
       '''
        p[0] = Node(name='primary_expression', value=p[1], idName=p[1])
        var_data = get_var_data(p[1], global_stack, global_node)
        if var_data != None:
            p[0].type = var_data["type"]
        

        if check_variable_not_def(p[0] if isinstance(p[0],str) else p[0].idName, global_stack, global_node) and  check_variable_func_conflict(p[0] if isinstance(p[0],str) else p[0].idName, symbolTable) and check_func_not_def(p[0] if isinstance(p[0],str) else p[0].idName):
            pr_error("Identifier %s not defined at line = %d" % (p[0] if isinstance(p[0],str) else p[0].idName, p.lineno(0)))
        else:
            p[0].type=get_var_type(p[1],global_stack,global_node)
        #if check_variable_func_conflict(p[0].idName, symbolTable):
        #    pr_error("Function name %s is being redefined as identifier at line = %d" % (p[0].idName, p.lineno(0)))

    def p_primary_expression_2(self, p):
        '''primary_expression   : constant
                               | '(' expression ')'
       '''
        p[0] = Node(name='primary_expression')
        if(len(p) == 2):
            p[0] = p[1]
            p[0].type = p[1].type
        else:
            p[0].type=p[2].type
            p[0].value=p[2].value
            p[0].idName=p[2].idName
            p[0].children=[p[2]]
        # to look again FUNC_NAME in CONST_String

    def p_constant_1(self, p):
        '''constant : CONST_INT
       '''
        p[0] = Node(name='constant', value=p[1], type='int')

    def p_constant_2(self, p):
        '''constant : CONST_CHAR
       '''
        p[0] = Node(name='constant', value=p[1], type='char')

    def p_constant_3(self, p):
        '''constant : CONST_FLOAT
       '''
        p[0] = Node(name='constant', value=p[1], type='float')

    def p_constant_4(self, p):
        '''constant : CONST_HEX
       '''
        p[0] = Node(name='constant', value=int(p[1], 16), type='int')

    def p_constant_5(self, p):
        '''constant : CONST_OCT
       '''
        p[0] = Node(name='constant', value=int(p[1], 8), type='int')

    def p_constant_6(self, p):
        '''constant : CONST_BIN
       '''
        p[0] = Node(name='constant', value=int(p[1], 2), type='int')

    def p_constant_7(self, p):
        '''constant : TRUE
       '''
        p[0] = Node(name='constant', value=p[1], type='bool')

    def p_constant_8(self, p):
        '''constant : FALSE  
       '''
        p[0] = Node(name='constant', value=p[1], type='bool')

    def p_postfix_expression_1(self, p):
        '''postfix_expression   : primary_expression
                               | postfix_expression '(' ')'
                               | postfix_expression '(' argument_expression_list ')'
                               | '(' type_name ')' '{' initializer_list '}'
                               | '(' type_name ')' '{' initializer_list ',' '}'
       '''
        p[0] = Node(name='postfix_expression')
        if(len(p) == 2):
            p[0] = p[1]

        elif(len(p) == 5):
            # label=create_new_label()
            if check_func_not_def(p[1].idName):
                pr_error("Function %s cannot be called as function is not defined at line %d" % (p[1].idName, p.lineno(1)))
            elif check_variable_func_conflict(p[1].idName, symbolTable):
                pr_error("Function %s not defined at line %d" % (p[1].idName, p.lineno(1)))
            p[0].children = p[0].children+[p[1], p[3]]
            
            # emit(dest=label,src1='',op='label',src2='')
            # return_stack.append(label)
            if(p[1] != '('):
                cond,n=True,0
                try:
                    cond,n=check_no_of_arguments_mismatch(symbolTable[p[1].idName]["func_parameters"]["number_args"],p[3])
                except:
                    return
                if cond :
                    pr_error('Expected no of arguments are %d but got %d in function %s at line no %d'%(symbolTable[p[1].idName]["func_parameters"]["number_args"],n,p[1].idName, p.lineno(1)))
                if not cond and check_arguments_type_mismatch(symbolTable[p[1].idName],p[3]):
                    pr_error("Type mismatch in function : %s at line : %d"%(p[1].idName, p.lineno(1)))
                try:
                    p[0].type=symbolTable[p[1].idName if p[1].idName!="" else p[1].value]["func_parameters"]["return_type"]
                except:
                    pass
            emit(dest=p[1].idName, src1='', op='gotofunc', src2='')
        elif(len(p) == 4):
            # label=create_new_label()
            if check_func_not_def(p[1].idName):
                pr_error("Function %s cannot be called as function is not defined at line %d" % (p[1].idName, p.lineno(1)))
            elif check_variable_func_conflict(p[1].idName, symbolTable):
                pr_error("Function %s not defined at line %d" % (p[1].idName, p.lineno(1)))
            p[0].children = p[0].children+[p[1], p[3]]
            cond,n=True,0
            try:
                cond,n=check_no_of_arguments_mismatch(symbolTable[p[1].idName]["func_parameters"]["number_args"],p[3])
            except:
                return
            if((symbolTable[p[1] if isinstance(p[1],str) else p[1].idName]["func_parameters"]["number_args"])):
                pr_error("Expected %d arguments for function : %s at line number : %d" % ((symbolTable[p[1] if isinstance(p[1],str) else p[1].idName]["func_parameters"]["number_args"]),p[1] if isinstance(p[1],str) else p[1].idName,p.lineno(1)))
            if check_func_not_def(p[1].idName):
                pr_error("Function %s cannot be called as function is not defined at line %d" % (p[1].idName, p.lineno(1)))
            elif check_variable_func_conflict(p[1].idName, symbolTable):
                pr_error("Function %s not defined at line %d" % (p[1].idName, p.lineno(1)))
            p[0] = p[1]
            emit(dest='__'+p[1] if isinstance(p[1],str) else '__'+p[1].idName, src1='', op='gotofunc', src2='')
            # emit(dest=label,src1='',op='label',src2='')
            # return_stack.append(label)
            try:
                p[0].type=symbolTable[p[1].idName if p[1].idName!="" else p[1].value]["func_parameters"]["return_type"]
            except:
                pass

        elif(len(p) == 7):
            p[0].children = p[0].children+[p[2], p[5]]

        else:
            p[0].children = p[0].children+[p[2], p[5]]

    def p_postfix_expression_2(self, p):
        '''postfix_expression   : postfix_expression SUBU
       '''
        p[0] = Node(name='postfix_expression')
        p[0].type = p[1].type
        p[0].children = p[0].children+[p[1], p[2]]
        tmp_var1 = create_new_var()
        tmp_var2 = create_new_var()
        gvar = get_var_data(p[1].idName, global_stack, global_node)
        if gvar == None:
            pr_error("Invalid decrement operation at line = %d" % (p.lineno(1)))
            return
        gvar = gvar["global_var"]
        emit(tmp_var1, gvar, '', '')
        emit(tmp_var2, gvar, '-' + str(p[1].type), '1')
        p[0].type=p[1].type
        emit(gvar, tmp_var2, '', '')
        p[0].idName = tmp_var1

    def p_postfix_expression_3(self, p):
        '''postfix_expression   : postfix_expression ADDU
       '''
        p[0] = Node(name='postfix_expression')
        p[0].type = p[1].type
        p[0].children = p[0].children+[p[1], p[2]]
        tmp_var1 = create_new_var()
        tmp_var2 = create_new_var()
        gvar = get_var_data(p[1].idName, global_stack, global_node)
        if gvar == None:
            pr_error("Invalid increment operation at line = %d" % (p.lineno(1)))
            return
        gvar = gvar["global_var"]
        emit(tmp_var1, gvar, '', '')
        emit(tmp_var2, gvar, '+' + str(p[1].type), '1')
        p[0].type=p[1].type
        emit(gvar, tmp_var2, '', '')
        p[0].idName = tmp_var1

    def p_postfix_expression_4(self, p):
        '''postfix_expression   : postfix_expression '.' ID
                               | postfix_expression MEMB_ACCESS ID
       '''
        p[0] = Node(name='postfix_expression')
        p[0].children = p[0].children+[p[1], p[2], p[3]]
        flg=0
        if not check_is_element_of_struct(p[1].idName,p[3],global_node,global_stack):
            pr_error("%s not a member of %s at line no. %d"%(p[3],p[1].idName,p.lineno(1)))
            flg=1
        t=get_var_type(p[1].idName,global_stack,global_node)
        if(p[2]=='.' and t[-4:]=='0ptr'):
            pr_error('%s is a pointer; did you mean to use "->" ? in line number %d' % (p[1].idName, p.lineno(1)))
        if(p[2]=='->' and t[-4:]!='0ptr'):
            pr_error('%s is not a pointer; did you mean to use "." ? in line number %d' % (p[1].idName, p.lineno(1)))
        if p[2] == '.':
            tmp_var = create_new_var()
            gvar = glo_subs(p[1].idName, global_stack, global_node)
            offset=0
            if not flg:
                offset = program_variables[gvar]["elements"][p[3]]["offset"]
            emit(tmp_var, gvar, '+', str(offset))
            p[0].idName = tmp_var
        type_element=get_var_type_struct_element(p[1].idName,p[3],global_stack,global_node)
        p[0].idName=p[1].idName+p[2]+p[3]
        p[0].type=type_element
        


    def p_postfix_expression_5(self, p):
        '''postfix_expression   : postfix_expression '[' constant ']'
        '''
        p[0] = Node(name='postfix_expression')
        p[0].children = p[0].children+[p[1], p[3]]
        tmp_var1 = create_new_var()
        var_data = get_var_data(p[1].idName, global_stack, global_node)
        size=0
        if var_data==None:
            size=p[1].type
        else:
            size=var_data["type"]
        type_size = get_data_type_size(size, global_node, global_stack)
        emit(tmp_var1, p[3].value, '*', str(type_size))
        tmp_var2 = create_new_var()
        gvar = glo_subs(p[1].idName, global_stack, global_node)
        emit(tmp_var2, gvar, '+', tmp_var1)
        p[0].idName = tmp_var2
        try:
            p[0].type=get_var_type(p[1].idName,global_stack,global_node)
        except:
            pass

    def p_postfix_expression_6(self, p):
        '''postfix_expression   : PRINTF '(' ID ')'
                                | SCANF '(' ID ')'
                                | PRINTF '(' constant ')'
        '''
        p[0] = Node(name='postfix_expression')
        p[0].children = p[0].children+[p[1], p[3]]
        if(not isinstance(p[3],str)):
            emit(dest='', src1=p[3].idName if p[3].idName!='' else p[3].value, op=p[1], src2=p[3].type)
        else:
            if check_variable_not_def(p[3],global_stack,global_node):
                pr_error("Variable %s not defined at line no. %d"%(p[3],p.lineno(1)))
            type=get_var_type(p[3],global_stack,global_node)
            emit(dest='', src1=p[3], op=p[1], src2=type)


    def p_argument_expression_list(self, p):
        '''argument_expression_list : assignment_expression
                                   | argument_expression_list ',' assignment_expression
       '''
        p[0] = Node(name='argument_expression_list')
        if(len(p) == 2):
            p[0] = p[1]
            
        else:
            p[0].children = p[0].children+[p[1], p[3]]
            

    def p_unary_expression_1(self, p):
        '''unary_expression : postfix_expression
                           | ADDU unary_expression
       '''
        p[0] = Node(name='unary_expression')
        if(len(p) == 2):
            p[0] = p[1]
        elif((len(p) == 3)):
            p[0].idName = p[2].idName
            tmp_var = create_new_var()
            gvar = get_var_data(p[2].idName, global_stack, global_node)
            if gvar == None:
                pr_error("Invalid increment operation at line = %d" % (p.lineno(2)))
                return
            gvar = gvar["global_var"]
            if(check_is_struct(p[2].idName,global_node,global_stack) ):
                pr_error("%s on struct is not allowed"%(p[1]))
            if(check_is_array(p[2].idName,global_node,global_stack) ):
                pr_error("%s on array is not allowed"%(p[1]))
            emit(tmp_var, gvar, '+' + str(p[2].type), '1')
            p[0].type=p[2].type
            emit(gvar, tmp_var, '', '')
            p[0].children = p[0].children+[p[1], p[2]]

    def p_unary_expression_2(self, p):
        '''unary_expression : SUBU unary_expression
       '''
        p[0] = Node(name='unary_expression')
        p[0].idName = p[2].idName
        tmp_var = create_new_var()
        gvar = get_var_data(p[2].idName, global_stack, global_node)
        if gvar == None:
            pr_error("Invalid decrement operation at line = %d" % (p.lineno(2)))
            return
        gvar = gvar["global_var"]
        if(check_is_struct(p[2].idName,global_node,global_stack) ):
                pr_error("%s on struct is not allowed"%(p[1]))
        if(check_is_array(p[2].idName,global_node,global_stack) ):
                pr_error("%s on array is not allowed"%(p[1]))
        emit(tmp_var, gvar, '-' + str(p[2].type), '1')
        p[0].type=p[2].type
        emit(gvar, tmp_var, '', '')
        p[0].children = p[0].children+[p[1], p[2]]

    def p_unary_expression_3(self, p):
        '''unary_expression : unary_operator unary_expression
       '''
        p[0] = Node(name='unary_expression')
        tmp_var = create_new_var()
        var=p[1].value
        if p[1].value == '&':
            var = 'mem'
        elif p[1].value == '*':
            var = 'deref'
        if(check_is_struct(p[2].idName,global_node,global_stack) ):
                pr_error("%s on struct is not allowed"%(p[1]))
        if(check_is_array(p[2].idName,global_node,global_stack) ):
                pr_error("%s on array is not allowed"%(p[1] if isinstance(p[1],str) else p[1].idName))
        gvar = glo_subs(p[2].idName, global_stack, global_node)
        emit(tmp_var, gvar, var, '')
        p[0].children = p[0].children+[p[1], p[2]]
        p[0].idName = tmp_var
        p[0].value=p[2].idName

    def p_unary_expression_4(self, p):
        '''unary_expression : SIZEOF '(' ID ')'
       '''
        p[0] = Node(name='unary_expression',type='int')
        id_type=get_var_type(p[3],global_stack,global_node)
        p[0].value=get_data_type_size(id_type,global_node,global_stack)
        p[0].idName=p[0].value
        print(p[0].value)
        p[0].children = p[0].children+[p[1], p[3]]

    def p_unary_operator(self, p):
        '''unary_operator   : '&'
                           | '*'
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
        else:
            tmp_var = create_new_var()
            if(check_type_mismatch(p[1].type,p[3].type)):
                pr_error("Type mismatch in line %d"%(p.lineno(1)))
            if(check_is_struct(p[1].idName,global_node,global_stack) or check_is_struct(p[3].idName,global_node,global_stack)):
                pr_error("%s on struct is not allowed"%(p[2]))
            if(check_is_array(p[1].idName,global_node,global_stack) or check_is_array(p[3].idName,global_node,global_stack)):
                pr_error("%s on array is not allowed"%(p[2]))
            
            gvar1 = None
            gvar2 = None
            if p[1].idName != "":
                gvar1 = glo_subs(p[1].idName, global_stack, global_node)
            else:
                gvar1 = p[1].value

            if p[3].idName != "":
                gvar2 = glo_subs(p[3].idName, global_stack, global_node)
            else:
                gvar2 = p[3].value

            emit(tmp_var, gvar1, p[2] + str(p[1].type), gvar2)
            p[0].idName = tmp_var
            p[0].type=p[1].type
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_additive_expression(self, p):
        '''additive_expression  : multiplicative_expression
                               | additive_expression '+' multiplicative_expression
                               | additive_expression '-' multiplicative_expression
       '''
        p[0] = Node(name='additive_expression')
        if(len(p) == 2):
            p[0] = p[1]
        else:
            tmp_var = create_new_var()
            if(check_type_mismatch(p[1].type,p[3].type)):
                pr_error("Type mismatch in line %d"%(p.lineno(1)))
                
            if(check_is_struct(p[1].idName,global_node,global_stack) or check_is_struct(p[3].idName,global_node,global_stack)):
                pr_error("%s on struct is not allowed"%(p[2]))
            if(check_is_array(p[1].idName,global_node,global_stack) or check_is_array(p[3].idName,global_node,global_stack)):
                pr_error("%s on array is not allowed"%(p[2]))
            
            gvar1 = None
            gvar2 = None
            if p[1].idName != "":
                gvar1 = glo_subs(p[1].idName, global_stack, global_node)
            else:
                gvar1 = p[1].value
                p[1].idName = p[1].value

            if p[3].idName != "":
                gvar2 = glo_subs(p[3].idName, global_stack, global_node)
            else:
                gvar2 = str(p[3].value)
                p[3].idName = p[3].value

            emit(tmp_var, gvar1, p[2] + str(p[1].type), gvar2)
            p[0].idName = tmp_var
            p[0].type=p[1].type
            p[0].children = p[0].children+[p[1], p[2], p[3]]
            if p[1].type != p[3].type:
                pass
                #print("Implicit type casting not allowed between %s and %s at line %d" % (p[1].type, p[3].type, p.lineno(0)))
            p[0].type = p[1].type
            # p[0].value = tmp_var

    def p_shift_expression(self, p):
        '''shift_expression : additive_expression
                           | shift_expression BIT_LEFT additive_expression
                           | shift_expression BIT_RIGHT additive_expression
       '''
        p[0] = Node(name='shift_expression')
        if(len(p) == 2):
            p[0] = p[1]
        else:
            tmp_var = create_new_var()
            gvar1 = glo_subs(p[1].idName)
            gvar2 = glo_subs(p[3].idName)
            if(p[3].type!='int'):
                pr_error("Only integer allowed in shift operations at line no. %d"%(p.lineno(1)))
            if(p[1].type!='int'):
                pr_error("Only integer allowed in shift operations at line no. %d"%(p.lineno(1)))
            
            if(check_is_struct(p[1].idName,global_node,global_stack) or check_is_struct(p[3].idName,global_node,global_stack)):
                pr_error("%s on struct is not allowed"%(p[2]))
            if(check_is_array(p[1].idName,global_node,global_stack) or check_is_array(p[3].idName,global_node,global_stack)):
                pr_error("%s on array is not allowed"%(p[2]))
            emit(tmp_var, gvar1, p[2] + str(p[1].type), gvar2)
            p[0].idName = tmp_var
            p[0].type=p[1].type
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
            p[0] = p[1]
        else:
            tmp_var = create_new_var()
            tmp = ""
            if(p[3].idName):
                tmp = glo_subs(p[3].idName,global_stack,global_node)
            else:
                tmp = p[3].value
            
            if(check_type_mismatch(p[1].type,p[3].type)):
                pr_error("Type mismatch in line %d"%(p.lineno(1)))
            
            gvar1 = glo_subs(p[1].idName,global_stack,global_node)
            if(check_is_struct(p[1].idName,global_node,global_stack) or check_is_struct(p[3].idName,global_node,global_stack)):
                pr_error("%s on struct is not allowed"%(p[2]))
            if(check_is_array(p[1].idName,global_node,global_stack) or check_is_array(p[3].idName,global_node,global_stack)):
                pr_error("%s on array is not allowed"%(p[2]))
            emit(tmp_var, gvar1, p[2] + str(p[1].type), tmp)
            p[0].type=p[1].type
            p[0].idName = tmp_var
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_equality_expression(self, p):
        '''equality_expression  : relational_expression
                               | equality_expression COMP_EQUAL relational_expression
                               | equality_expression COMP_NEQUAL relational_expression
       '''
        p[0] = Node(name='equality_expression')
        if(len(p) == 2):
            p[0] = p[1]
        else:
            tmp_var = create_new_var()

            gvar1 = glo_subs(p[1].idName)
            gvar2 = glo_subs(p[3].idName)
            if(check_type_mismatch(p[1].type,p[3].type)):
                pr_error("Type mismatch in line %d"%(p.lineno(1)))
            if(check_is_struct(p[1].idName,global_node,global_stack) or check_is_struct(p[3].idName,global_node,global_stack)):
                pr_error("%s on struct is not allowed"%(p[2]))
            if(check_is_array(p[1].idName,global_node,global_stack) or check_is_array(p[3].idName,global_node,global_stack)):
                pr_error("%s on array is not allowed"%(p[2]))
            emit(tmp_var, gvar1, p[2] + str(p[1].type), gvar2)
            p[0].type=p[1].type
            p[0].idName = tmp_var
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_and_expression(self, p):
        '''and_expression   : equality_expression
                           | and_expression '&' equality_expression
       '''
        p[0] = Node(name='and_expression')
        if(len(p) == 2):
            p[0] = p[1]
        else:
            tmp_var = create_new_var()
            if(check_type_mismatch(p[1].type,p[3].type)):
                pr_error("Type mismatch in line %d"%(p.lineno(1)))
            if(check_is_struct(p[1].idName,global_node,global_stack) or check_is_struct(p[3].idName,global_node,global_stack)):
                pr_error("%s on struct is not allowed"%(p[2]))
            if(check_is_array(p[1].idName,global_node,global_stack) or check_is_array(p[3].idName,global_node,global_stack)):
                pr_error("%s on array is not allowed"%(p[2]))
            gvar1 = glo_subs(p[1].idName)
            gvar2 = glo_subs(p[3].idName)

            emit(tmp_var, gvar1, p[2] + str(p[1].type), gvar2)
            p[0].type=p[1].type
            p[0].idName = tmp_var
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_exclusive_or_expression(self, p):
        '''exclusive_or_expression  : and_expression
                                   | exclusive_or_expression '^' and_expression
       '''
        p[0] = Node(name='exclusive_or_expression')
        if(len(p) == 2):
            p[0] = p[1]
            
        else:
            tmp_var = create_new_var()

            gvar1 = glo_subs(p[1].idName)
            gvar2 = glo_subs(p[3].idName)
            if(check_type_mismatch(p[1].type,p[3].type)):
                pr_error("Type mismatch in line %d"%(p.lineno(1)))
            if(check_is_struct(p[1].idName,global_node,global_stack) or check_is_struct(p[3].idName,global_node,global_stack)):
                pr_error("%s on struct is not allowed"%(p[2]))
            if(check_is_array(p[1].idName,global_node,global_stack) or check_is_array(p[3].idName,global_node,global_stack)):
                pr_error("%s on array is not allowed"%(p[2]))  
            emit(tmp_var, gvar1, p[2] + str(p[1].type), gvar2)
            p[0].type=p[1].type
            p[0].idName = tmp_var
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_inclusive_or_expression(self, p):
        '''inclusive_or_expression  : exclusive_or_expression
                                   | inclusive_or_expression '|' exclusive_or_expression
       '''
        p[0] = Node(name='inclusive_or_expression')
        if(len(p) == 2):
            p[0] = p[1]
        else:
            tmp_var = create_new_var()

            gvar1 = glo_subs(p[1].idName)
            gvar2 = glo_subs(p[3].idName)
            if(check_type_mismatch(p[1].type,p[3].type)):
                pr_error("Type mismatch in line %d"%(p.lineno(1)))
            if(check_is_struct(p[1].idName,global_node,global_stack) or check_is_struct(p[3].idName,global_node,global_stack)):
                pr_error("%s on struct is not allowed"%(p[2]))
            if(check_is_array(p[1].idName,global_node,global_stack) or check_is_array(p[3].idName,global_node,global_stack)):
                pr_error("%s on array is not allowed"%(p[2]))
            emit(tmp_var, gvar1, p[2] + str(p[1].type), gvar2)
            p[0].type=p[1].type
            p[0].idName = tmp_var
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_logical_and_expression(self, p):
        '''logical_and_expression   : inclusive_or_expression
                                   | logical_and_expression LOGIC_AND inclusive_or_expression
       '''
        p[0] = Node(name='logical_and_expression')
        if(len(p) == 2):
            p[0] = p[1]
        else:
            tmp_var = create_new_var()
            if(check_type_mismatch(p[1].type,p[3].type)):
                pr_error("Type mismatch in line %d"%(p.lineno(1)))
            if(check_is_struct(p[1].idName,global_node,global_stack) or check_is_struct(p[3].idName,global_node,global_stack)):
                pr_error("%s on struct is not allowed"%(p[2]))
            if(check_is_array(p[1].idName,global_node,global_stack) or check_is_array(p[3].idName,global_node,global_stack)):
                pr_error("%s on array is not allowed"%(p[2]))
            gvar1 = glo_subs(p[1].idName)
            gvar2 = glo_subs(p[3].idName)

            emit(tmp_var, gvar1, p[2] + str(p[1].type), gvar2)
            p[0].type=p[1].type
            p[0].idName = tmp_var
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_logical_or_expression(self, p):
        '''logical_or_expression    : logical_and_expression
                                   | logical_or_expression LOGIC_OR logical_and_expression
       '''
        p[0] = Node(name='logical_or_expression')
        if(len(p) == 2):
            p[0] = p[1]
        else:
            tmp_var = create_new_var()
            if(check_type_mismatch(p[1].type,p[3].type)):
                pr_error("Type mismatch in line %d"%(p.lineno(1)))
            if(check_is_struct(p[1].idName,global_node,global_stack) or check_is_struct(p[3].idName,global_node,global_stack)):
                pr_error("%s on struct is not allowed"%(p[2]))
            if(check_is_array(p[1].idName,global_node,global_stack) or check_is_array(p[3].idName,global_node,global_stack)):
                pr_error("%s on array is not allowed"%(p[2]))
            gvar1 = glo_subs(p[1].idName)
            gvar2 = glo_subs(p[3].idName)

            emit(tmp_var, gvar1, p[2] + str(p[1].type), gvar2)
            p[0].type=p[1].type
            p[0].idName = tmp_var
            p[0].children = p[0].children+[p[1], p[2], p[3]]

    def p_conditional_expression(self, p):
        '''conditional_expression   : logical_or_expression
                                   | logical_or_expression '?' expression ':' conditional_expression
       '''
        p[0] = Node(name='conditional_expression')
        if(len(p) == 2):
            p[0] = p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3], p[4], p[5]]

    def p_assignment_expression(self, p):
        '''assignment_expression    : conditional_expression
                                   | unary_expression assignment_operator assignment_expression
       '''
        p[0] = Node(name='assignment_expression')
        if(len(p) == 2):
            p[0] = p[1]
            
        else:
            if check_type_mismatch(p[1].type,p[3].type):
                pr_error("Type mismatch at line no. %d"%(p.lineno(1)))
            if check_if_const_changed(p[1] if isinstance(p[1],str) else p[1].idName, global_node ,global_stack):
                pr_error("Tried to change constant %s at line = %d" % (p[1].idName, p.lineno(0)))
            p[0].children = p[0].children+[p[1], p[2], p[3]]
            p[0].idName = p[1] if isinstance(p[1],str) else p[1].idName
            p[0].value = p[3].value
            gvar1 = glo_subs(p[1] if isinstance(p[1],str) else p[1].idName, global_stack, global_node)
            gvar2 = glo_subs(p[3].idName, global_stack, global_node)
            emit(gvar1, gvar2 if p[3].idName!='' else p[3].value, "store", "")

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
            p[0] = p[1]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_constant_expression(self, p):
        '''constant_expression : conditional_expression'''
        p[0] = Node(name='constant_expression')
        if(len(p) == 2):
            p[0] = p[1]

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
    # def p_DECLMARKER(self,p):
    #     '''DECLMARKER : '''

    def p_declaration(self, p):
        '''declaration  : declaration_specifiers ';'
                       | declaration_specifiers init_declarator_list ';'
        '''
        p[0] = Node(name='declaration', type=p[1].type)
        global global_node
        if(len(p) == 3):
            p[0] = p[1]
        else:
            # if check_variable_func_conflict(p[2].idName, symbolTable):
            #     pr_error("Function name %s is being redefined as identifier at line = %d" % (p[0].idName, p.lineno(0)))
            # if check_variable_dataType_conflict(p[2].idName, global_node,global_stack):
                # pr_error("Struct/Union name %s is being redefined as identifier at line = %d" % (p[0].idName, p.lineno(0)))
            p[0].children = p[0].children+[p[1], p[2]]
            p[0].value = p[2].value
            p[0].idName = p[2].idName
        
            if( not p[0].type.startswith("struct") and not p[0].type.startswith("union")):
                # if check_variable_redefined(p[0].idName,global_node):
                #     pr_error("Variable redefined at line = %d" % (p.lineno(1)))
                # if check_data_type_not_def(p[0])
                # adding variables to symbol table
                add_var(p,tmp_node=p[2],type=p[1].type,qualifier_list=p[1].qualifier_list,global_node=global_node,isStruct=0,global_stack=global_stack)
            else:
                add_var(p,tmp_node=p[2],type=p[1].type,qualifier_list=p[1].qualifier_list,global_node=global_node,isStruct=1,global_stack=global_stack)
                struct_name=p[0].type[6:]
                if(struct_name[-4:]=='0ptr'):
                    struct_name=struct_name[:-4]
                if check_data_type_not_def(struct_name,global_stack,global_node):
                    pr_error("Type : %s not defined at line no. %d"%(struct_name,p.lineno(1)))

    
    def p_declaration_specifiers_1(self, p):
        '''declaration_specifiers   : type_specifier
                                   | type_qualifier
                                   | type_qualifier declaration_specifiers
        '''
    #| type_specifier declaration_specifiers'''
        p[0] = Node(name='declaration_specifiers', type=p[1].type)
        if(len(p) == 2):
            p[0] = p[1]
            
        else:
            p[0].children = p[0].children+[p[1], p[2]]
            p[0].type=p[1].type if p[1].name=="type_specifier" else p[2].type
            if(p[1].name=="type_qualifier"):
                p[0].qualifier_list=p[2].qualifier_list
                p[0].qualifier_list.append(p[1].value)

    def p_declaration_specifiers_2(self, p):
        '''declaration_specifiers   : type_specifier declaration_specifiers
        '''
        pr_error("two or more data types in declaration specifiers at line %d" % (p.lineno(0)))
        raise SyntaxError

    def p_init_declarator_list(self, p):
        '''init_declarator_list : init_declarator
                               | init_declarator_list ',' init_declarator
       '''
        p[0] = Node(name='init_declarator_list')
        if(len(p) == 2):
            p[0] = p[1]
            
        else:
            p[0].children = p[0].children+[p[1], p[3]]
            

    def p_init_declarator(self, p):
        '''init_declarator  : declarator '='  initializer
                           | declarator
       '''
        p[0] = Node(name='init_declarator')
        p[0].idName = p[1]
        if(len(p) == 2):
            p[0] = p[1]
            gvar1 = glo_subs(p[1].idName, global_stack, global_node)
            emit(gvar1, p[1].value if p[1].value != '' else gvar1, "", "")
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3]]
            p[0].value = p[3].value
            p[0].idName = p[1].idName
            p[0].type = p[3].type
            p[0].array_list=p[3].array_list
            gvar1 = glo_subs(p[1].idName if p[1].idName!="" else p[1].value, global_stack, global_node)
            gvar2 = glo_subs(p[3].idName if p[3].idName!="" else p[3].value, global_stack, global_node)
            # if(check_type_mismatch(p[1].type,p[3].type)):
            #     pr_error("Type mismatch in line %d"%(p.lineno(1)))
            emit(gvar1,gvar2, "store", "")
            if len(global_stack)==0 and p[3].name!='constant':
                pr_error("Only constants allowed in global declaration")
          
    def p_type_specifier_1(self, p):
        '''type_specifier   : VOID
                           | INT
                           | FLOAT
                           | DOUBLE
                           | LONG
                           | CHAR
                           | SHORT
                           | BOOL
                           | LONG_LONG
       '''
        p[0] = Node(name='type_specifier', type=p[1], value=p[1])

    def p_type_specifier_2(self, p):
        '''type_specifier   : struct_or_union_specifier
       '''
        p[0] = Node(name='type_specifier')
        p[0] = p[1]

    def p_STRUCTMARKER1(self,p):
        '''STRUCTMARKER1 : '''
        global struct_name
        if(isinstance(p[-1],str)):
            global_node["dataTypes"][p[-1]] = {"1type": p[-2].type}
            struct_name=p[-1]
            # if check_struct_redefined(p[-1],global_node["dataTypes"]):
            #     pr_error("Struct redefined")
        else:
            struct_name=create_new_struct_name()
            global_node["dataTypes"][struct_name] = {"1type": p[-1].type}
        global_node["dataTypes"][struct_name]["1size"] = 0
            
    def p_STRUCTMARKER2(self,p):
        '''STRUCTMARKER2 : '''
        global struct_name
        max_len = 0
        ele_arr = list(global_node["dataTypes"][struct_name].keys())
        ele_arr.remove("1type")
        ele_arr.remove("1size")
        for i in ele_arr:
            var_data = global_node["dataTypes"][struct_name][i]
            tlen = None
            if var_data["type"].endswith("0ptr"):
                tlen = 8
            else:
                tlen = get_data_type_size(var_data["type"], global_node, global_stack)
            if tlen > max_len:
                max_len = tlen
        offset = global_node["dataTypes"][struct_name]["1size"]
        global_node["dataTypes"][struct_name]["1size"] += (max_len - offset) % max_len


    def p_struct_or_union_specifier(self, p):
        '''struct_or_union_specifier    : struct_or_union ID STRUCTMARKER1 '{' struct_declaration_list '}' STRUCTMARKER2
                                       | struct_or_union ID
       '''
        p[0] = Node(name='struct_or_union_specifier', type=p[1].type)
        global global_node
        if(len(p) == 7):
            p[0].children = p[0].children+[p[1], p[4]]
        elif(len(p) == 8):
            p[0].children = p[0].children+[p[1], p[2], p[5]]
        else:
            p[0].children+=[p[1],p[2]]
            p[0].type=p[1].type+p[2]


    def p_struct_or_union(self, p):
        '''struct_or_union  : STRUCT
                           | UNION
       '''
        p[0] = Node(name='struct_or_union', type=p[1], value=p[1])

    def p_struct_declaration_list(self, p):
        '''struct_declaration_list  : struct_declaration
                                   | struct_declaration_list struct_declaration
       '''
        p[0] = Node(name='struct_declaration_list')
        if(len(p) == 2):
            p[0] = p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]
        

    def p_struct_declaration(self, p):
        '''struct_declaration   : specifier_qualifier_list ';'
                               | specifier_qualifier_list struct_declarator_list ';'
       '''
        p[0] = Node(name='struct_declaration', type=p[1].type)
        global global_node
        if(len(p) == 3):
            p[0] = p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]
            p[0].idName = p[2].idName
            # if check_variable_redefined_struct(p[0].idName,global_node["dataTypes"][struct_name]):
            #     pr_error("Struct element redefined at line = %d" % (p.lineno(1)))
            add_struct_element(p,struct_name= struct_name,tmp_node=p[2],type=p[1].type,qualifier_list=p[1].qualifier_list,global_node=global_node)
            
            

    def p_specifier_qualifier_list(self, p):
        '''specifier_qualifier_list   : type_specifier specifier_qualifier_list
                                     | type_specifier
                                     | type_qualifier specifier_qualifier_list
                                     | type_qualifier
       '''
        p[0] = Node(name='specifier_qualifier_list', type=p[1].type)
        if(len(p) == 2):
            p[0] = p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_struct_declarator_list(self, p):
        '''struct_declarator_list   : struct_declarator
                                   | struct_declarator_list ',' struct_declarator
       '''
        p[0] = Node(name='struct_declarator_list')
        if(len(p) == 2):
            p[0] = p[1]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_struct_declarator(self, p):
        '''struct_declarator   : ':' constant_expression
                              |  declarator ':' constant_expression
                              |  declarator
       '''
        p[0] = Node(name='struct_declaration')
        if(len(p) == 2):
            p[0] = p[1]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[2]]
        else:
            p[0].children = p[0].children+[p[1], p[3]]

    def p_type_qualifier(self, p):
        '''type_qualifier   : CONST
                           | VOLATILE
                           | UNSIGNED
                           | SIGNED
       '''
        p[0] = Node(name='type_qualifier', value=p[1])

    def p_declarator(self, p):
        '''declarator   : pointer direct_declarator
                       | direct_declarator
       '''
        p[0] = Node(name='declarator', type = "")
        if(len(p) == 2):
            p[0] = p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]
            p[0].idName = p[2].idName
            p[0].type = 'ptr'
    def p_func_declarator(self, p):
        '''func_declarator : pointer direct_declarator
                            | func_direct_declarator
       '''
        p[0] = Node(name='declarator', type = "")
        if(len(p) == 2):
            p[0] = p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]
            p[0].idName = p[2].idName
            p[0].type = 'ptr'
    def p_func_direct_declarator_init(self, p):
        '''func_direct_declarator_init : MAIN
                               | ID
                               | '(' declarator ')'
       '''
        p[0] = Node(name='func_direct_declarator_init')
        if(len(p) == 2):
            p[0].value = p[1]
            p[0].idName = p[1]
        if(len(p) == 4):
            p[0].children = p[0].children+[p[2]]

    def p_func_direct_declarator(self, p):
        '''func_direct_declarator    : func_direct_declarator_init '(' parameter_type_list ')'
                               | func_direct_declarator_init '(' ')'
                               | func_direct_declarator_init '(' identifier_list ')'
       '''
        p[0] = Node(name='func_direct_declarator', idName=p[1].idName)
        if(len(p) == 4):
            p[0] = p[1]
            #if p[2] == '[':
            #    pr_error("JODD ho kya")
        elif(len(p) == 6):
            p[0].children = p[0].children+[p[1], p[2], p[4]]
        else:
            p[0].children = p[0].children+[p[1], p[3]]
            

    def p_direct_declarator_1(self, p):
        '''direct_declarator    : ID
                               | '(' declarator ')'
       '''
        p[0] = Node(name='direct_declarator')
        if(len(p) == 2):
            p[0].value = p[1]
            p[0].idName = p[1]
        if(len(p) == 4):
            p[0].children = p[0].children+[p[2]]

    def p_direct_declarator_2(self, p):
        '''direct_declarator    : direct_declarator '[' ']'
                               | direct_declarator '[' constant ']'
                               | direct_declarator '(' parameter_type_list ')'
                               | direct_declarator '(' ')'
                               | direct_declarator '(' identifier_list ')'
       '''
        p[0] = Node(name='direct_declarator', idName=p[1].idName)
        if(len(p) == 4):
            p[0] = p[1]
            #if p[2] == '[':
            #    pr_error("JODD ho kya")
        elif(len(p) == 6):
            p[0].children = p[0].children+[p[1], p[2], p[4]]
        else:
            p[0].value=p[3].value
            p[0].children = p[0].children+[p[1], p[3]]

    def p_pointer(self, p):
        '''pointer  : '*' type_qualifier_list pointer
                   | '*' type_qualifier_list
                   | '*' pointer
                   | '*'
       '''
        p[0] = Node(name='pointer')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[1],p[2], p[3]]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1],p[2]]
        else:
            p[0].value=p[1]
            p[0].idName=p[1]

    def p_type_qualifier_list(self, p):
        '''type_qualifier_list  : type_qualifier
                               | type_qualifier_list type_qualifier
       '''
        p[0] = Node(name='type_qualifier')
        if(len(p) == 2):
            p[0] = p[1]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]

    def p_parameter_type_list(self, p):
        '''parameter_type_list  : parameter_list

       '''
        p[0] = Node(name='parameter_type_list')
        if(len(p) == 2):
            p[0] = p[1]
    #  parameter_list ',' ELLIPSIS

    def p_parameter_list(self, p):
        '''parameter_list   : parameter_declaration
                           | parameter_list ',' parameter_declaration
       '''
        p[0] = Node(name='parameter_list')
        if(len(p) == 2):
            p[0] = p[1]
        elif(len(p) == 4):
            p[0].children = p[0].children+[p[1], p[3]]

    def p_parameter_declaration(self, p):
        '''parameter_declaration    : declaration_specifiers declarator
                                   | declaration_specifiers abstract_declarator
                                   | declaration_specifiers
       '''
        p[0] = Node(name='parameter_declaration', type=p[1].type)
        if(len(p) == 2):
            p[0] = p[1]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]
            p[0].idName = p[2].idName
        
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
            p[0] = p[1]
        elif(len(p) == 3):
            p[0].children = p[0].children+[p[1], p[2]]

    def p_abstract_declarator(self, p):
        '''abstract_declarator  : pointer direct_abstract_declarator
                               | pointer
                               | direct_abstract_declarator
       '''
        p[0] = Node(name='abstract_declarator')
        if(len(p) == 2):
            p[0] = p[1]
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
            p[0] = p[1]

    def p_initializer_1(self, p):
        '''initializer  : '{' initializer_list '}'
                       | '{' initializer_list ',' '}'  
                       | assignment_expression                            
       '''
        p[0] = Node(name='initializer')
        if(len(p) == 4):
            # p[0].children+=[p[1],p[2],p[3]]
            p[0].array_list=p[2].array_list
            p[0].children=[p[2],p[3]]
        elif len(p)==5:
            # p[0].children+=[p[1],p[2],p[4]]
            p[0]=p[2]
        else:
            p[0] = p[1]

    # def p_initializer_2(self, p):
    #     '''initializer  : '{' '}' '''
    #     p[0] = Node(name='initializer')

    def p_initializer_list(self, p):
        '''initializer_list : initializer
                           | initializer_list ',' initializer
       '''
        p[0] = Node(name='initializer_list')
        if(len(p) == 4):
            p[0].children = p[0].children+[p[1], p[3]]
            p[0].array_list=p[1].array_list
            p[0].array_list.append(p[3].value)
        else:
            p[0] = p[1]
            p[0].array_list.append(p[1].value)
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
        p[0] = p[1]

    def p_labeled_statement_1(self, p):
        '''labeled_statement    : ID ':' statement
       '''
        p[0] = Node(name='labeled_statement')
        p[0].children = p[0].children+[p[1], p[3]]

    def p_labeled_statement_2(self, p):
        '''labeled_statement    : CASE SMARKER constant_expression ':' statement
                               | DEFAULT SMARKER ':' statement
       '''
        p[0] = Node(name='labeled_statement')
        switch_label.append(p[2])
        global break_label_stack
        if(len(p) == 5):
            p[0].children = p[0].children+[p[1], p[4]]
            switch_expr.append('')
        else:
            p[0].children = p[0].children+[p[1], p[3], p[5]]
            switch_expr.append(p[3].value)

    def p_SMARKER(self, p):
        '''SMARKER : '''
        label = create_new_label()
        emit(dest=label, src1='', op='label', src2='')
        p[0] = label

    def p_compound_statement(self, p):
        '''compound_statement   : '{' block_item_list '}'
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
            p[0] = p[1]

    def p_block_item(self, p):
        '''block_item   :  declaration
                       |  statement
       '''
        p[0] = Node(name='block_item')
        p[0] = p[1]

    def p_expression_statement(self, p):
        '''expression_statement : ';'
                               | expression ';'
       '''
        p[0] = Node(name='expression_statement')
        if(len(p) == 3):
            p[0] = p[1]

    def p_selection_statement(self, p):
        '''selection_statement  : IF '(' expression ')' MARKER1 statement MARKER2 ELSE MARKER1 statement MARKER21
                               | IF '(' expression ')' MARKER1 statement MARKER22
                               | SWITCH '(' expression ')' SMARKER2 statement SMARKER3
       '''
        p[0] = Node(name='selection_statement')
        if(len(p) == 7):
            p[0].children = p[0].children+[p[1], p[3], p[6]]

        elif(len(p) == 8):
            p[0].children = p[0].children+[p[1], p[3], p[6]]
        else:
            p[0].children = p[0].children+[p[1], p[3], p[6], p[8], p[10]]

    def p_SMARKER2(self, p):
        '''
           SMARKER2 :
       '''
        label1 = create_new_label()
        label2 = create_new_label()
        emit(dest=label1, src1='', src2='', op='goto')
        p[0] = [label1, label2]
        global break_label_stack
        break_label_stack.append(label2)

    def p_SMARKER3(self, p):
        '''SMARKER3 :
       '''
        emit(dest=p[-2][1], src1='', src2='', op='goto')
        emit(dest=p[-2][0], src1='', src2='', op='label')
        flg = -1
        for i in range(len(switch_label)):
            label = switch_label[i]
            expr = switch_expr[i]
            if(expr == ''):
                flg = i
            else:
                emit(dest=label, src1=expr+'eq', op='goto', src2=p[-4].idName)
        if flg >= 0:
            emit(dest=switch_label[flg], src1='', op='goto', src2='')
        emit(dest=p[-2][1], src1='', op='label', src2='')
        break_label_stack.pop()

    def p_MARKER1(self, p):
        ''' MARKER1 : '''
        global global_node,scope_count
        tmp = "scope"+str(scope_count)
        
        global_node[tmp] = {"variables": {}, "dataTypes": {}}
        global_stack.append(global_node)
        global_node = global_node["scope"+str(scope_count)]
        if(p[-1] != 'else'):
            label1 = create_new_label()
            label2 = create_new_label()
            p[0] = [label1, label2]
            emit(dest=label1, src1=p[-2].idName if p[-2].idName!="" else p[-2].value, op='goto', src2='eq 0')
        else:
            emit(dest=p[-4][1], src1='', op='goto', src2='')
            emit(dest=p[-4][0], src1='', op='label', src2='')
            p[0] = p[-4]
        scope_count+=1

    def p_MARKER2(self, p):
        ''' MARKER2 : '''
        global global_node
        global_node = global_stack.pop()

    def p_MARKER21(self, p):
        ''' MARKER21 : '''
        global global_node
        global_node = global_stack.pop()
        emit(dest=p[-2][1], src1='', op='label', src2='')

    def p_MARKER22(self, p):
        ''' MARKER22 : '''
        global global_node
        global_node = global_stack.pop()
        emit(dest=p[-2][0], src1='', op='label', src2='')

    def p_MARKER3(self, p):
        ''' MARKER3 : '''
        global global_node
        tmp = "scope"+str(len(global_stack))
        global_node[tmp] = {"variables": {}, "dataTypes": {}}
        global_stack.append(global_node)
        global_node = global_node["scope"+str(len(global_stack)-1)]

    def p_WHILE_MARKER1(self, p):
        ''' WHILE_MARKER1 : '''
        global global_node
        tmp = "scope"+str(len(global_stack))
        global_node[tmp] = {"variables": {}, "dataTypes": {}}
        global_stack.append(global_node)
        global_node = global_node["scope"+str(len(global_stack)-1)]
        label = create_new_label()
        emit(dest=label, src1='', op='label', src2='')
        p[0] = label
        continue_label_stack.append(label)

    def p_WHILE_MARKER2(self, p):
        ''' WHILE_MARKER2 : '''
        label = create_new_label()
        emit(dest=label, src1=p[-2].idName if p[-2].idName!="" else p[-2].value, op='goto', src2='eq 0')
        p[0] = label
        break_label_stack.append(label)

    def p_WHILE_MARKER3(self, p):
        ''' WHILE_MARKER3 : '''
        emit(dest=p[-6], src1='', op='goto', src2='')
        emit(dest=p[-2], src1='', op='label', src2='')
        break_label_stack.pop()
        continue_label_stack.pop()

    def p_iteration_statement_1(self, p):
        '''iteration_statement  : WHILE WHILE_MARKER1 '(' expression ')' WHILE_MARKER2 statement WHILE_MARKER3
       '''
        # FOR MARKER3 '(' declaration expression_statement ')'  statement
        # | FOR MARKER3 '(' expression_statement FOR_MARKER1 expression_statement FOR_MARKER2 expression FOR_MARKER3 ')' FOR_MARKER4 statement FOR_MARKER5
        #                         | FOR MARKER3 '(' declaration expression_statement expression ')' statement
        p[0] = Node(name='iteration_statement')
        p[0].children = p[0].children+[p[1], p[4], p[7]]

    def p_iteration_statement_2(self, p):
        '''iteration_statement : FOR MARKER3 '(' expression_statement FOR_MARKER1 expression_statement FOR_MARKER2 expression FOR_MARKER3 ')' FOR_MARKER4 statement FOR_MARKER5'''
        p[0] = Node(name='iteration_statement')
        p[0].children = p[0].children+[p[1], p[4], p[6], p[8], p[12]]

    def p_iteration_statement_3(self, p):
        '''iteration_statement : DO DO_MARKER1 statement WHILE DO_MARKER2 '(' expression ')' DO_MARKER3 ';'
       '''
        p[0] = Node(name='iteration_statement')
        p[0].children = p[0].children+[p[1], p[3], p[4], p[7]]

    def p_DO_MARKER1(self, p):
        ''' DO_MARKER1 :
       '''
        global global_node
        tmp = "scope"+str(len(global_stack))
        global_node[tmp] = {"variables": {}, "dataTypes": {}}
        global_stack.append(global_node)
        global_node = global_node["scope"+str(len(global_stack)-1)]
        label1 = create_new_label()
        label2 = create_new_label()
        label3 = create_new_label()
        emit(dest=label1, src1='', op='label', src2='')
        p[0] = [label1,label2,label3]
        break_label_stack.append(label3)
        continue_label_stack.append(label2)
    
    def p_DO_MARKER2(self, p):
        ''' DO_MARKER2 :
       '''
        emit(dest=p[-3][1],src1='',op='label',src2='')

    def p_DO_MARKER3(self, p):
        ''' DO_MARKER3 :
       '''
        emit(dest=p[-7][2], src1=p[-2].idName, op='goto', src2='eq 0')
        emit(dest=p[-7][0], src1='', op='goto', src2='')
        emit(dest=p[-7][2], src1='', op='label', src2='')
        break_label_stack.pop()
        continue_label_stack.pop()

    def p_FOR_MARKER1(self, p):
        '''
       FOR_MARKER1 :
       '''
        label = create_new_label()
        emit(dest=label, src1='', op='label', src2='')
        p[0] = label
        continue_label_stack.append(label)

    def p_FOR_MARKER2(self, p):
        '''FOR_MARKER2 : '''
        label1 = create_new_label()
        if(p[-1].idName):
            emit(dest=label1, src1=p[-1].idName, op='goto', src2='eq 0')
        label2 = create_new_label()
        emit(dest=label2, src1='', op='goto', src2='')
        label3 = create_new_label()
        emit(dest=label3, src1='', op='label', src2='')
        p[0] = [label1, label2, label3]
        break_label_stack.append(label1)

    def p_FOR_MARKER3(self, p):
        '''FOR_MARKER3 : '''
        label = create_new_label()
        emit(dest=p[-4], src1='', op='goto', src2='')

    def p_FOR_MARKER4(self, p):
        '''FOR_MARKER4 : '''
        label = create_new_label()
        emit(dest=p[-4][1], src1='', op='label', src2='')

    def p_FOR_MARKER5(self, p):
        '''FOR_MARKER5 : '''
        global global_node, global_stack
        label = create_new_label()
        emit(dest=p[-6][2], src1='', op='goto', src2='')
        emit(dest=p[-6][0], src1='', op='label', src2='')
        break_label_stack.pop()
        continue_label_stack.pop()
        global_node = global_stack.pop()

    def p_jump_statement_1(self, p):
        '''jump_statement   : GOTO ID ';'
                           | CONTINUE ';'
                           | BREAK ';'
                           | RETURN expression ';'
       '''
        p[0] = Node(name='jump_statement')
        if(len(p) == 3):
            p[0] = p[1]
            if(p[1]=="break"):
                emit(dest=break_label_stack[-1], src1='', op='goto', src2='')
            else:
                emit(dest=continue_label_stack[-1], src1='', op='goto', src2='')
        elif len(p) == 4:
            p[0].children = p[0].children+[p[1], p[2]]
            # ret_type = global_node["func_parameters"]["return_type"].lower()
            # if ret_type.upper() not in ret_type_check[p[2].type.upper()]:
                # pr_error("Return type mismatch at line %d. Function return type is %s whereas returning %s" % (p.lineno(0), ret_type, p[2].type.lower()))
            #label=return_stack.pop()
            tmp = glo_subs(p[2].idName, global_stack, global_node)
            if(p[2].idName == ''):
                tmp = p[2].value
            emit(dest='', src1=tmp, op='return', src2='')

    def p_jump_statement_2(self, p):
        '''jump_statement   : RETURN ';'
       '''
        p[0] = Node(name='jump_statement')
        p[0].value = p[1]
        ret_type = global_node["func_parameters"]["return_type"].lower()
        if 'void' != ret_type:
            pr_error("Return type mismatch at line %d. Function return type is %s whereas returning void" % (p.lineno(0), ret_type))

    def p_translation_unit(self, p):
        '''translation_unit : external_declaration
                           | translation_unit external_declaration
       '''
        p[0] = Node(name='translation_unit')
        if(len(p) == 2):
            p[0] = p[1]
        else:
            p[0].children = p[0].children+[p[1], p[2]]

    def p_external_declaration(self, p):
        '''external_declaration : declaration
                               | function_definition
       '''
        p[0] = Node(name='external_declaration')
        if(len(p) == 2):
            p[0] = p[1]
        elif(len(p) == 5):
            p[0].children = p[0].children+[p[1], p[2], p[3], p[4]]
            p[0].idName = p[3]
            try:
                p[0].value = p[4].value
            except:
                p[0].value = p[4]
            symbolTable["variables"][p[0].idName] = {
                "value": p[0].value,
                "type": 'int',
                "scope": 0,
                "line_no": 0,
                "isMacro": 1,
                "const": 1
            }
        else:
            p[0].children = p[0].children+[p[1], p[2], p[3], p[5], p[8]]
            p[0].idName = p[3]

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
    def p_function_definition_init(self, p):
        '''function_definition_init : declaration_specifiers func_declarator'''
        global global_node
        if check_func_redef(p[2].idName):
            pr_error("Function %s redefined at line %d"%(p[2].idName,p.lineno(1)))
        p[0] = Node(name='function_definition_init',type=p[1].type, idName=p[2].idName)

        # If there are arguments
        try:
            root = p[2].children[1]
            
            numberArgs = 0
            node=root
            while not isinstance(node,str) and node.name=='parameter_list':
                node=node.children[0]
                numberArgs+=1
            if(node.name=='parameter_declaration'):
                numberArgs+=1
            if(p[2].children[1].children[0].name=="type_specifier"):
                numberArgs = 1
            global_node[p[0].idName] = {
                "func_parameters": {
                    "number_args": numberArgs,
                    "arguments": {},
                    "return_type": p[0].type,
                    "scope": 0
                },
                "variables": {},
                "dataTypes": {}
            }
            if(p[2].children[1].children[0].name=="type_specifier"):
                pass
                symbolTable[p[0].idName]["func_parameters"]["arguments"][root.children[1].idName] = root.children[0].type
            else:
                node=root
                # while(not isinstance(node,str) and node.name=='parameter_list'):
                    # symbolTable[p[0].idName]["func_parameters"]["arguments"][node.children[1].idName] = node.children[1].type
                    # add_arguments(p,tmp_node=p[2],type=p[1].type,qualifier_list=p[1].qualifier_list,global_node=global_node,isStruct=0,global_stack=global_stack,entry_node=symbolTable[p[0].idName]["func_parameters"])
                    
                    # node=node.children[0]
                # symbolTable[p[0].idName]["func_parameters"]["arguments"][node.idName] = node.type
            add_arguments(p,p[2].children[1],global_node,global_stack,p[2].children[0].idName,0)
        except:
            symbolTable[p[0].idName] = {
                "func_parameters": {
                    "number_args": 0,
                    "arguments": {},
                    "return_type": p[0].type,
                    "scope": 0
                },
                "variables": {},
                "dataTypes": {}
            }

        p[0].children = p[0].children+[p[1], p[2]]
        global_stack.append(global_node)
        global_node = global_node[p[0].idName]
        emit(dest=p[2].idName, src1='', op='func_label', src2='')
    def p_function_definition(self, p):
        '''function_definition  : function_definition_init ';'  MARKER2
                               | function_definition_init compound_statement MARKER2 
        '''
        
        p[0] = Node(name='function_definition',type=p[1].type, idName=p[1].idName)
        if(len(p)==4):
            if(p[2]==';'):
                p[0]=p[1]
                
            else:
                p[0].children += [p[1], p[2]]
        if(not tac_code[-1].op.startswith('return')):
            emit(dest='', src1='', op='return', src2='')


    # def p_declaration_list(self, p):
    #     '''declaration_list : declaration
    #                        | declaration_list declaration
    #    '''
    #     p[0] = Node(name='declaration_list')
    #     if(len(p) == 2):
    #         p[0] = p[1]
    #     else:
    #         p[0].children = p[0].children+[p[1], p[2]]

    # def find_column(self, input, token):
    #    line_start = input.rfind('n', 0, token.lexpos) + 1
    #    return (token.lexpos - line_start) + 1

    def p_error(self, p):
        if p == None:
            print("EOF tokens.")
        print(p.value)
        print(p, type(p))
        # print(p.lineno, self.find_column(p.lexpos))
        print("Syntax error in input!")
        exit(-1)

    def build(self, **kwargs):
        self.parser = yacc.yacc(start='translation_unit', module=self, **kwargs, debug=True)

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

    def parse_inp(self, input):
        result = self.parser.parse(input, tracking = True)
        if "main" not in symbolTable.keys():
            print("'main' function not present.")
            exit(1)
        print("Parsing completed successfully")
        # for i in tac_code:
        #     print(i.print())
        # print("GlobalTAC code:")
        # for i in global_tac_code:
        #     print(i.print())
        gen_var_offset(symbolTable)
        variable_optimize(tac_code)
        for ind, i in enumerate(tac_code):
            print(ind, end = ' - ')
            i.print()
        self.generate_dot_ast(result)
        self.generate_dot()
        print(json.dumps(symbolTable,indent=4))
        #print(json.dumps(program_variables,indent=4))
        generate_final_code(tac_code)

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