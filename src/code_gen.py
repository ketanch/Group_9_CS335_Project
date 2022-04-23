from audioop import mul
from symbolTab import program_variables, symbolTable, global_tac_code

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
    print(type, end = ' ')
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

def is_fpr(reg):
    if reg.strip('$').startswith("f"):
        return True
    return False

def is_temp(var):
    return var.startswith('__var_')

def is_glo_var(var):
    return var.startswith('1gvar_')

def is_float(var):
    try:
        a = float(var)
        return True
    except:
        return False

def is_constant(var):
    if var.isdecimal():
        return "int"
    if is_float(var):
        return "float"
    return False
    
def get_str(var):
    try:
        out = eval(var)
        if type(out) == str:
            return out
        return False
    except:
        return False

def variable_optimize(block):
    #for ind, i in enumerate(block):
        #print(ind, end = ' - ')
        #i.print()
    #symTab = {i.dest: {"state": "dead"} for i in block if is_temp(i.dest)}
    symTab = {}
    for i in block:
        if is_temp(i.dest):
            symTab[i.dest] = {"state": "dead"}
        if is_glo_var(i.src1):
            symTab[i.src1] = {}
        if is_glo_var(i.src2):
            symTab[i.src2] = {}
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
        elif is_glo_var(ins.src1) and ins.op != "mem":
            if symTab[ins.src1].get("next_use", None) == None:
                symTab[ins.src1]["next_use"] = i
        if is_temp(ins.src2):
            if symTab[ins.src2]["state"] == "dead":
                statement_data[i]["reuse"].append(ins.src2)
            symTab[ins.src2]["state"] = "live"
            symTab[ins.src2]["next_use"] = i
        elif is_glo_var(ins.src2):
            if symTab[ins.src2].get("next_use", None) == None:
                symTab[ins.src2]["next_use"] = i
        if is_temp(ins.dest):
            if ins.op == "store" or ins.op == "mem":
                symTab[ins.dest]["next_use"] = symTab[ins.dest].get("next_use", i)
                if symTab[ins.dest]["state"] == "dead":
                    statement_data[i]["reuse"].append(ins.dest)
            else:
                symTab[ins.dest]["state"] = "dead"
    for ind,i in enumerate(block):
        #print(ind)
        if i.op == '':
            continue
        if i.src1 in symTab.keys():
            if (i.op != "mem" or (i.op == "mem" and not is_glo_var(i.src1))) and symTab[i.src1]["next_use"] != ind:
                if symTab[i.src1]["next_use"] != ind:
                    i.next_use["src1"] = symTab[i.src1]["next_use"]
        if i.src2 in symTab.keys():
            if symTab[i.src2]["next_use"] != ind:
                i.next_use["src2"] = symTab[i.src2]["next_use"]
        if i.dest in symTab.keys():# and (i.op == "mem" and not is_glo_var(i.dest)) and i.op != '':
            if symTab[i.dest]["next_use"] != ind:
                i.next_use["dest"] = symTab[i.dest]["next_use"]
    var_map = {i:i for i in symTab.keys()}
    reuse_var = []
    for i in range(len(block)):
        #print(i, end = '')
        if is_temp(block[i].dest):
            #if block[i].dest in reuse_var:
            #print("DDDDDDDDDDDdd", block[i].dest, var_map[block[i].dest])
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
        if is_temp(block[i].dest) and block[i].op != "store":
            var_map[block[i].dest] = reuse_var[0]
            reuse_var += [block[i].dest]
            block[i].dest = reuse_var[0]
            reuse_var = reuse_var[1:]
        #block[i].print()
        #print(var_map)
        #print(reuse_var)
    return block

#variable_optimize(block)
 
def rep_float_int(n) :
    def float_bin(my_number, places = 3):
        my_whole, my_dec = str(my_number).split(".")
        my_whole = int(my_whole)
        res = (str(bin(my_whole))+".").replace('0b','')
        for x in range(places):
            my_dec = str('0.')+str(my_dec)
            temp = '%1.20f' %(float(my_dec)*2)
            my_whole, my_dec = temp.split(".")
            res += my_whole
        return res

    sign = 0
    if n < 0 :
        sign = 1
        n = n * (-1)
    p = 30
    dec = float_bin (n, places = p)
    dotPlace = dec.find('.')
    onePlace = dec.find('1')
    if onePlace > dotPlace:
        dec = dec.replace(".","")
        onePlace -= 1
        dotPlace -= 1
    elif onePlace < dotPlace:
        dec = dec.replace(".","")
        dotPlace -= 1
    mantissa = dec[onePlace+1:]
 
    exponent = dotPlace - onePlace
    exponent_bits = exponent + 127
    exponent_bits = bin(exponent_bits).replace("0b",'')
 
    mantissa = mantissa[0:23]    
    final = str(sign) + exponent_bits.zfill(8) + mantissa
    hstr = '0x%0*X' %((len(final) + 3) // 4, int(final, 2))
    return int(hstr, 16)

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
        print([self.dest, self.src1, self.op, self.src2], self.next_use)

def _reg(reg):
    return '$'+str(reg)

'''
Zero reg - $0
$1 ($at) -> try not to use
Return values - $2,$3 ($v0,$v1)
Function arguments - $4,$5,$6,$7 ($a0,$a1,$a2,$a3)
Caller saved - $8 to $15 ($t0 to $t7)
Callee saved - $16 to $23 ($s0 to $s7)
Caller saved - $24,$25 ($t8,$t9)
Global pointer - $28 ($gp) -> for global vars, callee saved reg
Stack ptr - $29 ($sp)
Frame ptr - $30 ($fp)
Return address - $31 ($ra)
'''

class MIPSGenerator:

    def __init__(self):
        self.mips_code = ''
        self.current_func = None
        self.func_code = ''
        self.data_code = ''
        #Register decriptor
        self.register_des = {}
        for i in range(1, 32):
            self.register_des[str(i)] = None
        for i in range(0, 32):
            self.register_des["f"+str(i)] = None
        self.address_des = {}
        self.fp_regs = [i for i in range(0,32)]
        self.caller_saved = [8,9,10,11,12,13,14,15,24,25]
        self.callee_saved = [16,17,18,19,20,21,22,23]
        self.local_labels_ctr = 0

    def generate_local_label(self):
        out = '$LC'+str(self.local_labels_ctr)
        self.local_labels_ctr += 1
        return out

    def push(self, reg):
        self.mips_code += '\n\tsw %s, -4($29)\
                           \n\taddiu $29, $29, -4' % (reg)
    
    def pop(self, reg):
        self.mips_code += '\n\tlw %s, 0($29)\
                           \n\taddiu $29, $29, 4' % (reg)

    def syscall(self, code):
        self.mips_code += '\n\tli $v0, %d\n\tsyscall' % (code)

    def process_global_data(self, glo_emit):
        self.data_code += "\n\t.data"
        var_arr = {}
        for ins in glo_emit:
            op = ins.op
            dest = ins.dest
            if op == "store":
                ident = None
                if ins.src1.isdecimal():
                    var_arr[dest] = int(ins.src1)
                elif is_float(ins.src1):
                    var_arr[dest] = float(ins.src1)

        for var in symbolTable["variables"]:
            tvar = symbolTable["variables"][var]["global_var"]
            ident = ".space"
            val = ''
            if tvar in var_arr.keys():
                if program_variables[tvar]["type"] == "int":
                    ident = ".word"
                    val = var_arr[tvar]
            else:
                val = data_type_size[program_variables[tvar]["type"]]
            self.data_code += '\n%s:\t%s\t%s' % (var, ident, val)

    def add_float_to_data(self, float_var):
        llabel = self.generate_local_label()
        self.data_code += '\n%s:\t%s\t%s' % (llabel, ".word", rep_float_int(float_var))
        return llabel

    def add_str_to_data(self, str_var):
        llabel = self.generate_local_label()
        self.data_code += '\n%s:\t%s\t%s' % (llabel, ".asciiz", str_var)
        return llabel

    def free_regs(self, reg_type):
        '''
        Will get called if no more registers left
        '''
        pass

    def getreg(self, ins = None, type = "int"):
        if ins != None:
            if ins.next_use["src1"] == None and (is_temp(ins.src1) or (is_glo_var(ins.src1) and ins.src1 in self.address_des.keys())):
                return _reg(self.address_des[ins.src1])
            elif ins.next_use["src2"] == None and (is_temp(ins.src2) or (is_glo_var(ins.src2) and ins.src2 in self.address_des.keys())):
                return _reg(self.address_des[ins.src2])
        if not type.startswith("float"):
            if len(self.caller_saved) != 0:
                reg = self.caller_saved.pop(0)
                return _reg(reg)
            else:
                reg = self.free_regs("gpr")
                return _reg(reg)
        else:
            if len(self.fp_regs) != 0:
                reg = self.fp_regs.pop(0)
                return "$f" + str(reg)
            else:
                reg = self.free_regs("fpr")
                return "$f" + str(reg)

    def free_reg(self, reg):
        reg = reg.strip('$')
        self.caller_saved.append(int(reg))
        self.caller_saved.sort()
        self.register_des[reg] = None

    def prepare_reg(self, var, type = "int"):
        reg = None
        if var in self.address_des.keys():
            reg = self.address_des[var]
        elif is_glo_var(var):
            reg = self.getreg(type = type)
            self.load_var_in_reg(var, type, reg)
            #self.mips_code += '\n\tlw $%d, -%d($30)' % (reg, program_variables[var]["offset"])
            reg = reg.strip('$')
            self.address_des[var] = reg
            self.register_des[reg] = var
        else:
            val = get_str(var)
            if is_temp(var):
                print("Temp variables should be in reg")
                raise SyntaxError
            elif is_constant(var) or val:
                if get_str(var):
                    var = ord(val)
                reg = self.getreg(type = type)
                reg = reg.strip('$')
                self.load_constant_in_reg(var, type, _reg(reg))
            elif val:
                val = ord(val)
            else:
                print("Not a constant")
                raise SyntaxError
        return _reg(reg)

    def update_desc(self, ins, rsrc1 = None, rsrc2 = None, rdest = None):
        '''
        This function updates the descriptors after an instruction
        '''
        #print("des1", self.address_des)
        if rdest != None:
            self.register_des[rdest.strip('$')] = ins.dest
            if ins.dest in self.address_des:
                self.register_des[self.address_des[ins.dest]] = None
            self.address_des[ins.dest] = rdest.strip('$')
        if rsrc1 != None and ins.next_use["src1"] == None and ins.src1 != ins.dest:
            self.register_des[rsrc1] = None
            if is_fpr(rsrc1):
                self.fp_regs.append(int(rsrc1.strip('$f')))
                self.fp_regs.sort()
            else:
                self.caller_saved.append(int(rsrc1.strip('$')))
                self.caller_saved.sort()
            if not is_constant(ins.src1):
                self.address_des.pop(ins.src1)
        if rsrc2 != None and ins.next_use["src2"] == None and ins.src1 != ins.src2 and ins.src2 != ins.dest:
            self.register_des[rsrc2] = None
            if is_fpr(rsrc2):
                self.fp_regs.append(int(rsrc2.strip('$f')))
                self.fp_regs.sort()
            else:
                self.caller_saved.append(int(rsrc2.strip('$')))
                self.caller_saved.sort()
            if not is_constant(ins.src2):
                self.address_des.pop(ins.src2)
        #print("des2", self.address_des)

    def load_constant_in_reg(self, const, type, reg):
        if type == "int":
            self.mips_code += '\n\tli %s, %s' % (reg, const)
        elif type == "char":
            self.mips_code += '\n\tli %s, %s' % (reg, const)
        elif type == "float":
            label = self.add_float_to_data(float(const))
            self.mips_code += '\n\tlwc1 %s, %s' % (reg, label)

    def load_var_in_reg(self, var, type, reg):
        '''
        Loads a program variable into a register
        '''
        if type == "int":
            self.mips_code += '\n\tlw %s, -%d($30)' % (reg, program_variables[var]["offset"])
        elif type == "char":
            cmd = "lb"
            if program_variables[var]["unsigned"]:
                cmd = "lbu"
            self.mips_code += '\n\taddi %s, $0, $0\n\t%s %s, -%d($30)' % (reg, cmd, reg, program_variables[var]["offset"])
        elif type == "short":
            cmd = "lh"
            if program_variables[var]["unsigned"]:
                cmd = "lhu"
            self.mips_code += '\n\taddi %s, $0, $0\n\t%s %s, -%d($30)' % (reg, cmd, reg, program_variables[var]["offset"])
        elif type == "float":
            self.mips_code += '\n\tlwc1 %s, -%d($30)' % (reg, program_variables[var]["offset"])
    
    def load_var_addr_in_reg(self, var, reg):
        off = program_variables[var]["offset"]
        self.mips_code += '\n\taddiu %s, $30, -%d' % (reg, off)    

    def tac_to_mips(self, tac_code, symTab):
        src1_reg = None
        src2_reg = None
        dest_reg = None

        if tac_code.op in ['+int', '*int', '/int', '-int']:
            op = tac_code.op
            src1_dec = tac_code.src1.isdecimal()
            src2_dec = tac_code.src2.isdecimal()
            if not src1_dec:
                src1_reg = self.prepare_reg(tac_code.src1)
            if not src2_dec:
                src2_reg = self.prepare_reg(tac_code.src2)
            dest_reg = self.getreg(tac_code)
            if src1_dec and src2_dec:
                if op == "+int":
                    res = int(tac_code.src1) + int(tac_code.src2)
                elif op == "*int":
                    res = int(tac_code.src1) * int(tac_code.src2)
                elif op == "/int":
                    res = int(tac_code.src1) // int(tac_code.src2)
                elif op == "-int":
                    res = int(tac_code.src1) - int(tac_code.src2)
                self.load_constant_in_reg(res, "int", dest_reg)
            elif src1_dec:
                if op == '+int':
                    self.mips_code += '\n\taddi %s, %s, %s' % (dest_reg, src2_reg, tac_code.src1)
                elif op in ['*int', '/int']:
                    src1_reg = self.getreg()
                    self.load_constant_in_reg(tac_code.src1, "int", src1_reg)
                    if op == "*int":
                        cmd = "mul"
                    elif op == "/int":
                        cmd = "div"
                    self.mips_code += '\n\t%s %s, %s, %s' % (cmd, dest_reg, src2_reg, src1_reg)
            elif src2_dec:
                if op == '+int':
                    self.mips_code += '\n\taddi %s, %s, %s' % (dest_reg, src1_reg, tac_code.src2)
                elif op in ['*int', '/int']:
                    src2_reg = self.getreg()
                    self.load_constant_in_reg(tac_code.src2, "int", src2_reg)
                    if op == "*int":
                        cmd = "mul"
                    elif op == "/int":
                        cmd = "div"
                    self.mips_code += '\n\t%s %s, %s, %s' % (cmd, dest_reg, src1_reg, src2_reg)
            else:
                if op == '+int':
                    self.mips_code += '\n\taddu %s, %s, %s' % (dest_reg, src1_reg, src2_reg)
                elif op == ['*int', '/int']:
                    if op == "*int":
                        cmd = "mul"
                    elif op == "/int":
                        cmd = "div"
                    self.mips_code += '\n\t%s %s, %s, %s' % (cmd, dest_reg, src1_reg, src2_reg)
            
        #Done
        elif tac_code.op == 'gotofunc':
            self.mips_code += '\n\tjal %s' % (tac_code.dest)

        elif tac_code.op == 'return':
            if tac_code.src1 == '':
                pass
            elif is_glo_var(tac_code.src1) or is_temp(tac_code.src1):
                if tac_code.src1 in self.address_des.keys():
                    self.mips_code += '\n\taddu $2, $0, $%s' % (self.address_des[tac_code.src1])
                elif is_glo_var(tac_code.src1):
                    self.mips_code += '\n\tlw $2, -%d($30)' % (program_variables[tac_code.src1]["offset"])
            else:
                #Constant value return
                ret_type = symTab[self.current_func]["func_parameters"]["return_type"]
                self.load_constant_in_reg(tac_code.src1, ret_type, "$2")
            self.mips_code += '\n\taddiu $29, $29, %d' % (symbolTable[self.current_func]["stack_offset"])
            self.pop("$30")
            self.pop("$31")
            self.mips_code += '\n\tjr $31'
            self.func_code = None

        #Done
        elif tac_code.op == 'label':
            self.mips_code += '\n' + tac_code.dest + ':'

        #Done
        elif tac_code.op == 'func_label':
            self.current_func = tac_code.dest
            self.mips_code += '\n'+tac_code.dest+':'
            self.push("$31")
            self.push("$30")
            self.mips_code += '\n\taddu $30, $0, $29'
            self.mips_code += '\n\taddiu $29, $29, -%d' % (symbolTable[self.current_func]["stack_offset"])

        elif tac_code.op == 'goto':
            pass

        elif tac_code.op == 'store':
            src1 = tac_code.src1
            reg = None
            if is_temp(tac_code.dest):
                var_type = tac_code.src2
            else:
                var_type = program_variables[tac_code.dest]["type"]
            reg = self.prepare_reg(src1, var_type)
            store_cmd = "sw"
            if var_type == "float":
                store_cmd += "c1"
            elif var_type == "char":
                store_cmd = "sb"
            if is_temp(tac_code.dest):
                self.mips_code += "\n\t%s %s, 0(%s)" % (store_cmd, reg, self.address_des[tac_code.dest])
            else:
                self.mips_code += '\n\t%s %s, -%d($30)' % (store_cmd, reg, program_variables[tac_code.dest]["offset"])
            dest_reg = _reg(reg)
        
        elif tac_code.op == 'func_param':
            if int(tac_code.src1) < 5:
                var_type = is_constant(tac_code.src1)
                val = int(tac_code.src1)
                if is_temp(tac_code.dest) or is_glo_var(tac_code.dest):
                    self.mips_code += '\n\taddu $%d, $0, %s' % (val+3, self.prepare_reg(self.dest))
                elif var_type:
                    pass
                    #var_name = list(symbolTable[self.current_func]["func_parameters"]["arguments"].keys())[val]
                    #var_type = symbolTable[self.current_func]["func_parameters"]["arguments"][var_name]
                    #print(var_type)
                    #self.load_constant_in_reg(tac_code.src1, var_type, self.getreg())
                else:
                    raise SyntaxError
            else:
                reg = self.prepare_reg(tac_code.dest)
                self.push(reg)
        
        elif tac_code.op == 'printf':
            src1 = tac_code.src1 #data to be printed
            src2 = tac_code.src2 #type of statement
            if src1 in self.address_des.keys():
                reg = self.address_des[src1]
                if src2 == "float":
                    self.mips_code += '\n\tmov.s $f12, $%s' % (reg)
                else:
                    self.mips_code += '\n\taddu $4, $0, $%s' % (reg)
            elif is_glo_var(src1):
                tar_reg = "$4"
                if src2 == "float":
                    tar_reg = "$f12"
                self.load_var_in_reg(src1, src2, tar_reg)
            elif is_constant(src1):
                self.load_constant_in_reg(src1, src2, "$4")
            elif src1 in symbolTable["variables"].keys():
                pass

            if src2 == "int":
                self.syscall(1)
            elif src2 == "str":
                label = self.add_str_to_data(src1)
                self.mips_code += '\n\tla $a0, %s' % (label)
                self.syscall(4)
            elif src2 == "float":
                self.syscall(2)
            elif src2 == "char":
                self.syscall(11)
        
        elif tac_code.op == 'scanf':
            src1 = tac_code.src1
            src2 = tac_code.src2

            if src2 == "int":
                self.syscall(5)
                if is_glo_var(src1):
                    self.mips_code += '\n\tsw $v0, -%d($30)' % (program_variables[src1]["offset"])
                else:
                    raise SyntaxError
            elif src2 == "float":
                self.syscall(6)
                if is_glo_var(src1):
                    self.mips_code += '\n\tswc1 $f0, -%d($30)' % (program_variables[src1]["offset"])
                else:
                    raise SyntaxError
            elif src2 == "char":
                self.syscall(12)
                if is_glo_var(src1):
                    self.mips_code += '\n\tsb $v0, -%d($30)' % (program_variables[src1]["offset"])
                else:
                    raise SyntaxError
        
        elif tac_code.op == "mem":
            if not is_glo_var(tac_code.src1):
                raise SyntaxError
            dest_reg = self.getreg()
            self.load_var_addr_in_reg(tac_code.src1, dest_reg)
        
        self.update_desc(tac_code, src1_reg, src2_reg, dest_reg)
        #print(self.address_des)
        #print(self.mips_code)

    def final_code(self):
        return self.data_code + '\n\n\t.text' + self.mips_code

def generate_final_code(emit_arr):
    for i in global_tac_code:
        i.print()
    mips_gen = MIPSGenerator()
    mips_gen.process_global_data(global_tac_code)
    ctr = 0
    for i in emit_arr:
        #print(ctr)
        ctr += 1
        mips_gen.tac_to_mips(i, symbolTable)
    print(mips_gen.final_code())
    open('tmp/a.s', 'w').write(mips_gen.final_code())