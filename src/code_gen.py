data_type_size = {
    "int": 4,
    "long": 8,
    "long long int": 8,
    "long long": 8,
    "long int": 8,
    "char": 1,
    "float": 4,
    "double": 8,
    "bool": 1
}

#Finds struct size
def find_struct_size(var_data):
    vars = list(var_data.keys())
    vars.remove("1type")
    size = 0
    for i in vars:
        size += data_type_size[var_data["type"]]

#Byte aligns a variable
def byte_align(offset, type_len):
    offset += type_len
    offset += (type_len - (offset % type_len)) % type_len
    return offset

#Orders variables according to their size
def order_variables(gvars, type_size):
    return sorted(gvars.keys(), key = lambda x:type_size[gvars["type"]], reverse = True)

#Collects variables from all scopes
def func_collect_vars(func):
    vars = [func["variables"][i] for i in func["variables"]]
    scopes = list(func.keys())
    scopes = [i for i in scopes if i.startswith("scope")]
    for i in scopes:
        vars += func_collect_vars(func[i])
    return vars

#Generates offset for variables
def gen_var_offset(emit_arr, symbolTable):
    temp_data_sizes = {i:data_type_size[i] for i in data_type_size}
    for i in symbolTable["dataTypes"]:
        temp_data_sizes[i] = symbolTable["dataTypes"][i]["1size"]
    global_offset = 0
    gvars = [symbolTable["variables"][i] for i in symbolTable["variables"]]
    gvar_list = order_variables(gvars, temp_data_sizes)
    for var_data in gvar_list:
        type_len = temp_data_sizes[var_data["type"]]
        global_offset = byte_align(global_offset, type_len) + type_len * var_data["array"] * var_data["size"]
        var_data["offset"] = global_offset
    
    funcs = list(symbolTable.keys())
    funcs.remove("variables")
    funcs.remove("dataTypes")
    for func in funcs:
        local_offset = 0
        lvars = func_collect_vars(symbolTable[func])
        lvar_list = order_variables(lvars)
        for var in lvar_list:
            var_data = lvars[var]
            type_len = data_type_size[var_data["type"]]
            local_offset = byte_align(local_offset, type_len) + type_len * var_data["array"] * var_data["size"]
            var_data["offset"] = local_offset

#Function for finding basic blocks position
def create_basic_blocks(emit_arr):
    leader_arr = []
    labels = {}
    for ind, i in enumerate(emit_arr):
        if i[2] == 'label':
            labels[i[0]] = ind

    for ind, i in enumerate(emit_arr):
        if '__main' in i:
            leader_arr.append(ind)
        if 'goto' in i:
            label_ind = labels.get(i[0], None)
            if label_ind == None:
                print("Error in parsing")
                exit(0)
            leader_arr.append(label_ind)
            leader_arr.append(ind + 1)
    return leader_arr.sort()

#Function to split emit_arr into blocks
def split_basic_blocks(emit_arr):
    block_pos = create_basic_blocks(emit_arr)
    out_arr = []
    offset = 0
    for i in block_pos:
        out_arr += [emit_arr[offset:i+1]]
        offset = i+1
    return out_arr

def is_temp(var):
    return var.startswith('__var_')

def variable_optimize(block):
    symTab = {i[0]: {"state": "dead"} for i in block if is_temp(i[0])}
    statement_data = [None] * len(block)
    for ind in range(len(statement_data)):
        statement_data[ind] = {"reuse":[]}
    for i in range(len(block)-1, -1, -1):
        ins = block[i]
        if is_temp(ins[1]):
            if symTab[ins[1]]["state"] == "dead":
                statement_data[i]["reuse"].append(ins[1])
            symTab[ins[1]]["state"] = "live"
            symTab[ins[1]]["next_use"] = i
        if is_temp(ins[3]):
            if symTab[ins[3]]["state"] == "dead":
                statement_data[i]["reuse"].append(ins[3])
            symTab[ins[3]]["state"] = "live"
            symTab[ins[3]]["next_use"] = i
        if is_temp(ins[0]):
            symTab[ins[0]]["state"] = "dead"
            symTab[ins[0]].pop("next_use")
    var_map = {i:i for i in symTab.keys()}
    reuse_var = []
    for i in range(len(block)):
        if is_temp(block[i][0]):
            block[i][0] = var_map[block[i][0]]
        if is_temp(block[i][1]):
            block[i][1] = var_map[block[i][1]]
        if is_temp(block[i][3]):
            block[i][3] = var_map[block[i][3]]
        for j in range(len(statement_data[i]["reuse"])):
            statement_data[i]["reuse"][j] = var_map[statement_data[i]["reuse"][j]]
        reuse_var += statement_data[i]["reuse"]
        reuse_var = sorted(reuse_var, key = lambda x:int(x.strip('__var_')))
        if len(reuse_var) == 0:
            continue
        if is_temp(block[i][0]):
            var_map[block[i][0]] = reuse_var[0]
            reuse_var += [block[i][0]]
            block[i][0] = reuse_var[0]
            reuse_var = reuse_var[1:]
    return block

#variable_optimize(block)