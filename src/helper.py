from symbolTab import tac_code
def emit(dest, src1, op, src2):
    # if len(tac_code) > 1 and tac_code[-2][2].startswith('post_'):
    #    temp_ent = tac_code.pop()
    #    tac_code.append([dest, src1, op, src2])
    #    tac_code.append(temp_ent)
    #    return
    tac_code.append([dest, src1, op, src2])
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

def check_variable_not_def(var, global_stack, global_node):
    if var in global_node["variables"]:
        return False
    for i in range(len(global_stack)-1, 0, -1):
        if var in global_stack[i]["variables"]:
            return False
    return True

def check_variable_func_conflict(var, symbolTable):
    if var in symbolTable.keys():
        return True
    return False

def check_variable_redefined(var,global_node):
    if var in global_node["variables"].keys():
        return True
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
    for i in range(len(global_stack)-1, 0, -1):
        if var in global_stack[i]["variables"]:
            if global_stack[i]["variables"][var]["const"]:
                return True
    return False


def add_var(tmp_node,type,qualifier_list,global_node,isStruct,global_stack):
    prev_node=tmp_node
    while(len(tmp_node.children) == 2 and tmp_node != None and tmp_node.name != "direct_declarator"):
        
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
            "elements":{}
        }
        #adding struct elements in var
        if(isStruct):
            add_struct_elements_in_var(global_stack,global_node,global_node["variables"][child.idName])

        # checking for const,unsigned,volatile
        for quality in qualifier_list:
            global_node["variables"][child.idName][quality]=1
        # checking if it is an array
        if(len(child.children)==2):
            if child.children[0].name=='pointer':
                 global_node["variables"][child.idName]["type"]+='ptr'
            global_node["variables"][child.idName]["array"]=1
            global_node["variables"][child.idName]["size"]=child.children[1].value
        if(len(child.children)==3):
            global_node["variables"][child.idName]["array"]=1
            global_node["variables"][child.idName]["size"]=len(child.children[2].array_list)
            global_node["variables"][child.idName]["value"]=child.children[2].array_list
        prev_node=child
        tmp_node=tmp_node.children[0]
    if(tmp_node.name=='pointer'):
        global_node["variables"][prev_node.idName]["type"]+="ptr"
    else:
        global_node["variables"][tmp_node.idName]={
            "type":type,
            "value":tmp_node.value,
            "array":0,
            "size":0,
            "offset":0,
            "const":0,
            "volatile":0,
            "struct":isStruct,
            "elements":{}
        }
        if(isStruct):
            add_struct_elements_in_var(global_stack,global_node,global_node["variables"][tmp_node.idName])
        # emit(tmp_node.idName, tmp_node.value if tmp_node.value!="" else tmp_node.idName, '', '')
    # checking for const,unsigned,volatile
    for quality in qualifier_list:
        global_node["variables"][tmp_node.idName][quality]=1
    if(len(tmp_node.children)==2):
        global_node["variables"][tmp_node.idName]["array"]=1
        global_node["variables"][tmp_node.idName]["size"]=tmp_node.children[1].value        
    if(len(tmp_node.children)==3):
            global_node["variables"][tmp_node.idName]["array"]=1
            global_node["variables"][tmp_node.idName]["size"]=len(tmp_node.children[2].array_list)
            global_node["variables"][tmp_node.idName]["value"]=tmp_node.children[2].array_list
            
def add_struct_element(struct_name,tmp_node,type,qualifier_list,global_node):
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
            global_node["dataTypes"][struct_name][child.idName][quality]=1
        # checking if it is an array
        if(len(child.children)==2):
            if child.children[0].name=='pointer':
                 global_node["dataTypes"][struct_name][child.idName]["type"]+='ptr'
            global_node["dataTypes"][struct_name][child.idName]["array"]=1
            global_node["dataTypes"][struct_name][child.idName]["size"]=child.children[1].value
        if(len(child.children)==3):
            global_node["dataTypes"][struct_name][child.idName]["array"]=1
            global_node["dataTypes"][struct_name][child.idName]["size"]=len(child.children[2].array_list)
            global_node["dataTypes"][struct_name][child.idName]["value"]=child.children[2].array_list
        tmp_node=tmp_node.children[0]
    global_node["dataTypes"][struct_name][tmp_node.idName]={
        "type":type,
        "value":tmp_node.value,
        "array":0,
        "size":0,
        "offset":0,
        "const":0,
        "volatile":0,
    }
    # checking for const,unsigned,volatile
    for quality in qualifier_list:
        global_node["dataTypes"][struct_name][tmp_node.idName][quality]=1
    if(len(tmp_node.children)==2):
        global_node["dataTypes"][struct_name][tmp_node.idName]["array"]=1
        global_node["dataTypes"][struct_name][tmp_node.idName]["size"]=tmp_node.children[1].value        
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
    for i in range(len(global_stack)-1, 0, -1):
        if flg:
            break
        if name in global_stack[i]["dataTypes"]:
            struct_node=global_stack[i]["dataTypes"][name]  
    node["elements"]=struct_node  
