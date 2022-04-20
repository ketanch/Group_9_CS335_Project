from numpy import var
from symbolTab import program_variables

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

#returns size of a data type
def get_data_type_size(type, global_node, global_stack):
    # print(type, end = ' ')
    type_size = data_type_size.get(type, None)
    found = 0
    if type_size == None:
        temp_types = global_node["dataTypes"]
        for i in temp_types.keys():
            if type == temp_types[i]["1type"] + i:
                return temp_types[i]["1size"]

        for i in range(len(global_stack)-1, -1, -1):
            temp_types = global_stack[i]["dataTypes"]
            for i in temp_types.keys():
                if type == temp_types[i]["1type"] + i:
                    type_size = temp_types[i]["1size"]
                    return type_size
    else:
        return type_size
    return None

#Useful for returning size when symbol table is complete 
def get_type_size(var_data):
    if var_data["type"].endswith("0ptr"):
        return 8
    elif var_data["type"].startswith("struct") or var_data["type"].startswith("union"):
        return var_data["elements"]["1size"]
    else:
        return data_type_size[var_data["type"]]

#Byte aligns a variable
def byte_align(offset, type_len):
    offset += type_len
    offset += (type_len - (offset % type_len)) % type_len
    return offset

#Orders variables according to their size
def order_variables(gvars):
    return sorted(gvars, key = lambda x:get_type_size(x), reverse = True)

#Collects variables from all scopes
def func_collect_vars(func):
    vars = [func["variables"][i] for i in func["variables"]]
    scopes = list(func.keys())
    scopes = [i for i in scopes if i.startswith("scope")]
    for i in scopes:
        vars += func_collect_vars(func[i])
    return vars

#Generates offset for variables
def gen_var_offset(symbolTable):
    temp_data_sizes = {i:data_type_size[i] for i in data_type_size}
    for i in symbolTable["dataTypes"]:
        temp_data_sizes[i] = symbolTable["dataTypes"][i]["1size"]
    global_offset = 0
    gvars = [symbolTable["variables"][i] for i in symbolTable["variables"]]
    gvar_list = order_variables(gvars)
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
        for var_data in lvar_list:
            type_len = get_type_size(var_data)
            local_offset = byte_align(local_offset, type_len) + type_len * var_data["array"] * var_data["size"]
            var_data["offset"] = local_offset
        symbolTable[func]["stack_offset"] = local_offset

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

def is_glo_var(var):
    return var.startswith('1gvar_')

def variable_optimize(block):
    symTab = {i.dest: {"state": "dead"} for i in block if is_temp(i.dest)}
    statement_data = [None] * len(block)
    for ind in range(len(statement_data)):
        statement_data[ind] = {"reuse":[]}
    for i in range(len(block)-1, -1, -1):
        ins = block[i]
        if is_temp(ins.src1):
            if symTab[ins.src1]["state"] == "dead":
                statement_data[i]["reuse"].append(ins.src1)
            symTab[ins.src1]["state"] = "live"
            symTab[ins.src1]["next_use"] = i
        if is_temp(ins.src2):
            if symTab[ins.src2]["state"] == "dead":
                statement_data[i]["reuse"].append(ins.src2)
            symTab[ins.src2]["state"] = "live"
            symTab[ins.src2]["next_use"] = i
        if is_temp(ins.dest):
            symTab[ins.dest]["state"] = "dead"
            symTab[ins.dest].pop("next_use")
    var_map = {i:i for i in symTab.keys()}
    reuse_var = []
    for i in range(len(block)):
        if is_temp(block[i].dest):
            block[i].dest = var_map[block[i].dest]
        if is_temp(block[i].src1):
            block[i].src1 = var_map[block[i].src1]
        if is_temp(block[i].src2):
            block[i].src2 = var_map[block[i].src2]
        for j in range(len(statement_data[i]["reuse"])):
            statement_data[i]["reuse"][j] = var_map[statement_data[i]["reuse"][j]]
        reuse_var += statement_data[i]["reuse"]
        reuse_var = sorted(reuse_var, key = lambda x:int(x.strip('__var_')))
        if len(reuse_var) == 0:
            continue
        if is_temp(block[i].dest):
            var_map[block[i].dest] = reuse_var[0]
            reuse_var += [block[i].dest]
            block[i].dest = reuse_var[0]
            reuse_var = reuse_var[1:]
    return block

#variable_optimize(block)

register_des = {}
for i in range(32):
    register_des[str(i)] = None


class TACInstruction:
    def __init__(self, src1, src2, dest, op):
        self.src1 = src1
        self.src2 = src2
        self.dest = dest
        self.op = op
        self.next_use = {
            "src1": None,
            "src2": None,
            "dest": None
        }

    def print(self):
        return [self.dest, self.src1, self.op, self.src2]

class MIPSGenerator:

    def __init__(self):
        self.mips_code = ''

    def getreg(self):
        pass

    def prepare_reg(self, var):
        pass

    def tac_to_mips(self, tac_code):
        if tac_code.op == '+int':
            flag_imm = 0
            dest_reg = self.getreg()
            src1_dec = tac_code.src1.isdecimal()
            src2_dec = tac_code.src2.isdecimal()
            if src1_dec and src2_dec:
                self.mips_code += '\n\taddi %s, $0, %s' % (dest_reg, int(tac_code.src1) + int(tac_code.src2))
            elif src1_dec:
                self.mips_code += '\n\taddi %s, %s, %s' % (dest_reg, self.prepare_reg(tac_code.src2), tac_code.src1)
            elif src2_dec:
                self.mips_code += '\n\taddi %s, %s, %s' % (dest_reg, self.prepare_reg(tac_code.src1), tac_code.src2)
            else:
                self.mips_code += '\n\taddu %s, %s, %s' % (dest_reg, self.prepare_reg(tac_code.src1), self.prepare_reg(tac_code.src2))

        elif tac_code.op == 'gotofunc':
            pass

        elif tac_code.op == 'return':
            if tac_code.src1 == '':
                self.mips_code += '\n\tjr $ra'
            elif is_glo_var(tac_code.src1):
                self.mips_code += '\n\tlw $v0, -%d($fp)' % (program_variables[tac_code.src1]["offset"])
            elif is_temp(tac_code.src1):
                self.mips_code

        elif tac_code.op == 'label':
            self.mips_code += '\n' + tac_code.dest + ':'

        elif tac_code.op == 'goto':
            pass

        elif tac_code.op == 'store':
            pass

def generate_final_code(emit_arr):
    mips_gen = MIPSGenerator()
    for i in emit_arr:
        mips_gen.tac_to_mips(i)
    # print(mips_gen.mips_code)