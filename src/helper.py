ret_type_check = {
    "INT": ["INT", "LONG", "LONG_LONG"],
    "CHAR": ["CHAR"],
    "FLOAT": ["FLOAT", "DOUBLE"],
    "BOOL": ["BOOL"]
}

type_cast_arr = {
    "int": ["char", "float"]
}

def pr_error(err):
    print("\033[91mERROR\033[00m: %s" % (err))

def pr_warning(warn):
    print("\033[95mWARNING\033[00m: %s" % (warn))