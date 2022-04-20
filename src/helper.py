from symbolTab import tac_code, var_global_ctr, program_variables, global_tac_code
from code_gen import byte_align, get_data_type_size
from symbolTab import global_node, global_stack
from code_gen import TACInstruction

def emit(dest, src1, op, src2):
    # if len(tac_code) > 1 and tac_code[-2][2].startswith('post_'):
    #    temp_ent = tac_code.pop()
    #    tac_code.append([dest, src1, op, src2])
    #    tac_code.append(temp_ent)
    #    return
    ins = TACInstruction(src1, src2, dest, op)
    if(len(global_stack)==0 and op!='return'):
        global_tac_code.append(ins)
    else:
        tac_code.append(ins)

ret_type_check = {
    "INT": ["INT", "LONG", "LONG_LONG"],
    "CHAR": ["CHAR"],
    "FLOAT": ["FLOAT", "DOUBLE"],
    "BOOL": ["BOOL"]
}

type_cast_arr = {
    "int": ["char", "float"]
}

defaut_values={
    "int":0,
    "char":'a',
    "float":0.0,
    "bool":False
}

def pr_error(err):
    print("\033[91mERROR\033[00m: %s" % (err))

def pr_warning(warn):
    print("\033[95mWARNING\033[00m: %s" % (warn))

def get_var_data(var, global_stack, global_node):
    if var in global_node["variables"]:
        return global_node["variables"][var]
    for i in range(len(global_stack)-1, 0, -1):
        if var in global_stack[i]["variables"]:
            return global_stack[i]["variables"][var]
    return None

#Substitute global id name for variables
def glo_subs(var, global_stack, global_node):
    gvar = get_var_data(var, global_stack, global_node)
    if gvar == None:
        return var
    return gvar["global_var"]
    
def check_variable_not_def(var, global_stack, global_node):
    if var in global_node["variables"]:
        return False
    for i in range(len(global_stack)-1, -1, -1):
        if var in global_stack[i]["variables"]:
            return False
    if var in global_node["func_parameters"]["arguments"].keys():
        return False
    return True

def get_var_type(var, global_stack, global_node):
    if var in global_node["variables"]:
        return global_node["variables"][var]["type"]
    for i in range(len(global_stack)-1, -1, -1):
        if var in global_stack[i]["variables"]:
            return global_node["variables"][var]["type"]
    return "Not Defined"

def check_variable_func_conflict(var, symbolTable):
    if var in symbolTable.keys():
        return True
    return False

def check_variable_redefined(var,global_node):
    if var in global_node["variables"].keys():
        return True
    # when global there is no parameter
    try:
        if var in global_node["func_parameters"]["arguments"].keys():
            return True
    except:
        _=None
    return False

def check_struct_redefined(var,global_node):
    if var in global_node.keys():
        return True
    return False

def check_variable_redefined_struct(var,global_node):
    if var in global_node.keys():
        return True
    return False

def check_if_const_changed(var,global_node,global_stack):
    if var in global_node["variables"]:
        if global_node["variables"][var]["const"]:
            return True
    for i in range(len(global_stack)-1, -1, -1):
        if var in global_stack[i]["variables"]:
            if global_stack[i]["variables"][var]["const"]:
                return True
    return False


def add_var(p,tmp_node,type,qualifier_list,global_node,isStruct,global_stack):
    global var_global_ctr
    prev_node=tmp_node
    ctr = 0
    while(len(tmp_node.children) == 2 and tmp_node != None and tmp_node.name != "direct_declarator"):
        ctr += 1
        child=tmp_node.children[1]
        # emit(child.idName, child.value if child.value!="" else child.idName, '', '')
        
        global_node["variables"][child.idName]={
            "type":type,
            "value":child.value,
            "array":0,
            "size":0,
            "offset":0,
            "const":0,
            "volatile":0,
            "struct":isStruct,
            "elements":{},
            "global_var": "1gvar_" + str(var_global_ctr)
        }
        if(child.name!="direct_declarator" and type!=child.type and global_node["variables"][child.idName]["array"]):
            pr_error("Type mismatch")
        program_variables["1gvar_" + str(var_global_ctr)] = global_node["variables"][child.idName]
        var_global_ctr += 1
        #adding struct elements in var
        if(isStruct):
            add_struct_elements_in_var(global_stack,global_node,global_node["variables"][child.idName])

        # checking for const,unsigned,volatile
        for quality in qualifier_list:
            global_node["variables"][child.idName][quality]=1
        # checking if it is an array
        if(len(child.children)==2):
            if child.children[0].name=='pointer':
                 global_node["variables"][child.idName]["type"]+='0ptr'
            else:
                global_node["variables"][child.idName]["array"]=1
                global_node["variables"][child.idName]["size"]=int(child.children[1].value)
        if(len(child.children)==3):
            if len(child.children):
                if len(child.children[0].children) and child.children[0].children[0].name=='pointer':
                    global_node["variables"][child.idName]["type"]+="0ptr"
                elif(child.children[2].name!="constant"):
                    if(len(child.children[0].children)==2):
                        given_size=int(child.children[0].children[1].value)
                        if(given_size!=len(child.children[2].array_list)):
                            pr_error("Size mismatch for variable %s at line no. %d"%(p[0].idName,p.lineno(1)))
                    
                    global_node["variables"][child.idName]["array"]=1
                    global_node["variables"][child.idName]["size"]=len(child.children[2].array_list)
                    global_node["variables"][child.idName]["value"]=child.children[2].array_list
        
        prev_node=child
        tmp_node=tmp_node.children[0]
    if(tmp_node.name=='pointer'):
        global_node["variables"][prev_node.idName]["type"]+="0ptr"
    else:
        ctr += 1
        global_node["variables"][tmp_node.idName]={
            "type":type,
            "value":tmp_node.value,
            "array":0,
            "size":0,
            "offset":0,
            "const":0,
            "volatile":0,
            "struct":isStruct,
            "elements":{},
            "global_var": "1gvar_" + str(var_global_ctr)
        }
        program_variables["1gvar_" + str(var_global_ctr)] = global_node["variables"][tmp_node.idName]
        var_global_ctr += 1
        if(isStruct):
            add_struct_elements_in_var(global_stack,global_node,global_node["variables"][tmp_node.idName])
        # emit(tmp_node.idName, tmp_node.value if tmp_node.value!="" else tmp_node.idName, '', '')
    # checking for const,unsigned,volatile
    for quality in qualifier_list:
        global_node["variables"][tmp_node.idName][quality]=1
    if(len(tmp_node.children)==2):
        
        global_node["variables"][tmp_node.idName]["array"]=1
        global_node["variables"][tmp_node.idName]["size"]=int(tmp_node.children[1].value)        
    if(len(tmp_node.children)==3):
        if len(tmp_node.children):
            if len(tmp_node.children[0].children) and tmp_node.children[0].children[0].name=='pointer':
                global_node["variables"][tmp_node.idName]["type"]+="0ptr"
            elif(tmp_node.children[2].name!='constant'):
                given_size=0
                if(len(tmp_node.children[0].children)==2):
                    given_size=int(tmp_node.children[0].children[1].value)
                    if(given_size!=len(tmp_node.children[2].array_list)):
                        pr_error("Size mismatch for variable %s at line no. %d"%(p[0].idName,p.lineno(1)))
                global_node["variables"][tmp_node.idName]["array"]=1
                global_node["variables"][tmp_node.idName]["size"]=len(tmp_node.children[2].array_list)
                global_node["variables"][tmp_node.idName]["value"]=tmp_node.children[2].array_list
    if len(global_stack):
        for i in range(ctr):
            tac_code[-1-i].dest = glo_subs(tac_code[-1-i].dest, global_stack, global_node)
    else:
        for i in range(ctr):
            global_tac_code[-1-i].dest = glo_subs(global_tac_code[-1-i].dest, global_stack, global_node)
    if tmp_node.name!="direct_declarator" and type!=tmp_node.type and not global_node["variables"][tmp_node.idName]["array"]:
        pr_error("Type mismatch")

def add_struct_element(struct_name,tmp_node,type,qualifier_list,global_node):
    prev_node=tmp_node
    while(len(tmp_node.children) == 2 and tmp_node != None and tmp_node.name != "direct_declarator"):
        child=tmp_node.children[1]
        global_node["dataTypes"][struct_name][child.idName]={
            "type":type,
            "value":child.value,
            "array":0,
            "size":0,
            "offset":0,
            "const":0,
            "volatile":0,
        }
        # checking for const,unsigned,volatile
        for quality in qualifier_list:
            if child.children[0].name=='pointer':
                 global_node["dataTypes"][struct_name][child.idName]["type"]+='0ptr'
            global_node["dataTypes"][struct_name][child.idName][quality]=1
        # checking if it is an array
        if(len(child.children)==2):
            if child.children[0].name=='pointer':
                 global_node["dataTypes"][struct_name][child.idName]["type"]+='0ptr'
            else:
                global_node["dataTypes"][struct_name][child.idName]["array"]=1
                global_node["dataTypes"][struct_name][child.idName]["size"]=int(child.children[1].value)
        if(len(child.children)==3):
            global_node["dataTypes"][struct_name][child.idName]["array"]=1
            global_node["dataTypes"][struct_name][child.idName]["size"]=len(child.children[2].array_list)
            global_node["dataTypes"][struct_name][child.idName]["value"]=child.children[2].array_list
        prev_node=child
        tmp_node=tmp_node.children[0]

        offset = global_node["dataTypes"][struct_name]["1size"]
        var_data = global_node["dataTypes"][struct_name][child.idName]
        type = var_data["type"]
        tlen = None
        if type.endswith("0ptr"):
            tlen = 8
        else:
            tlen = get_data_type_size(type, global_node, global_stack)
        offset += (tlen - offset) % tlen
        var_data["offset"] = offset
        offset += tlen
        global_node["dataTypes"][struct_name]["1size"] = offset
        
    if(tmp_node.name=='pointer'):
        var_data = global_node["dataTypes"][struct_name][prev_node.idName]
        offset = global_node["dataTypes"][struct_name]["1size"] - get_data_type_size(var_data["type"], global_node, global_stack)
        offset += (8 - offset) % 8
        var_data["offset"] = offset
        offset += 8
        global_node["dataTypes"][struct_name]["1size"] = offset
        global_node["dataTypes"][struct_name][prev_node.idName]["type"]+="0ptr"

    else:
        offset = global_node["dataTypes"][struct_name]["1size"]
        tlen = get_data_type_size(type, global_node, global_stack)
        offset += (tlen - offset) % tlen
        global_node["dataTypes"][struct_name][tmp_node.idName]={
            "type":type,
            "value":tmp_node.value,
            "array":0,
            "size":0,
            "offset":offset,
            "const":0,
            "volatile":0,
        }
        offset += tlen
        global_node["dataTypes"][struct_name]["1size"] = offset
    # checking for const,unsigned,volatile
    for quality in qualifier_list:
        global_node["dataTypes"][struct_name][tmp_node.idName][quality]=1
    if(len(tmp_node.children)==2):
        global_node["dataTypes"][struct_name][tmp_node.idName]["array"]=1
        global_node["dataTypes"][struct_name][tmp_node.idName]["size"]=int(tmp_node.children[1].value)        
    if(len(tmp_node.children)==3):
            global_node["dataTypes"][struct_name][tmp_node.idName]["array"]=1
            global_node["dataTypes"][struct_name][tmp_node.idName]["size"]=len(tmp_node.children[2].array_list)
            global_node["dataTypes"][struct_name][tmp_node.idName]["value"]=tmp_node.children[2].array_list

def add_struct_elements_in_var(global_stack,global_node,node):
    name=''
    
    if(node["type"].startswith("struct")):
        name=node["type"][6:]
    else:
        name=node["type"][5:]
    flg=0
    struct_node={}
    if name in global_node["dataTypes"]:
        flg=1
        struct_node=global_node["dataTypes"][name]
    for i in range(len(global_stack)-1, -1, -1):
        if flg:
            break
        if name in global_stack[i]["dataTypes"]:
            struct_node=global_stack[i]["dataTypes"][name]  
    node["elements"]=struct_node  
    
def check_no_of_arguments_mismatch(n, node):
    counter=1
    while not isinstance(node,str) and len(node.children) != 0 :
        node=node.children[0]
        counter+=1
    if counter == n:
        return False, counter
    return True, counter

def check_arguments_type_mismatch(func_entry, node):
    counter=0
    argument_list_name=list(func_entry["func_parameters"]["arguments"])
    n=len(argument_list_name)
    while not isinstance(node,str) and len(node.children) != 0 :
        type_given=get_var_type(node.children[1].idName,global_stack=global_stack,global_node=global_node)
        if type_given=="Not Defined":
            type_given=node.children[n-1-counter].type
        if func_entry["func_parameters"]["arguments"][argument_list_name[n-1-counter]] != type_given:
            return True
        node=node.children[0]
        counter+=1
    type_given=get_var_type(node.idName,global_stack=global_stack,global_node=global_node)
    if type_given=="Not Defined":
        type_given=node.type
    if func_entry["func_parameters"]["arguments"][argument_list_name[n-1-counter]] != type_given:
        return True
    return False
    # if counter == n:
    #     return False, counter
    # return True, counter
    
def check_data_type_not_def(type, global_stack, global_node):
    if type in global_node["dataTypes"]:
        return False
    for i in range(len(global_stack)-1, -1, -1):
        if type in global_stack[i]["dataTypes"]:
            return False
    return True

def check_is_array(var,global_node,global_stack):
    if var in global_node["variables"]:
        return global_node["variables"][var]["array"]
    for i in range(len(global_stack)-1, -1, -1):
        if var in global_stack[i]["variables"]:
            return global_node["variables"][var]["array"]
    return False

def check_is_struct(var,global_node,global_stack):
    if var in global_node["variables"]:
        return global_node["variables"][var]["struct"]
    for i in range(len(global_stack)-1, -1, -1):
        if var in global_stack[i]["variables"]:
            return global_node["variables"][var]["struct"]
    return False

def check_type_mismatch(type1,type2):
    if type1!=type2:
        return True
    return False

def check_is_element_of_struct(struct,var,global_node,global_stack):
    
    try:
        if var in global_node["variables"][struct]["elements"]:
            return True
    except:
        pass
    for i in range(len(global_stack)-1, -1, -1):
        try:
            if var in global_stack[i]["variables"][struct]["elements"]:
                return True
        except:
            pass
    return False