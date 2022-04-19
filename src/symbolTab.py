# Template for symbol table
# global has scope 0
# symbolTable={
#     "variables":{
#         "a":{
#             "value":3,
#             "type":"int",
#             "scope":0,
#             "line_no":1,
#             "isMacro":1,
#             "isConst":1,
#         }
#         # "b":{
#         #     .
#         #     .
#         # }
#     },
#     "func_name":{
#         "fp_base": 0
#         "stack_ptr": 0
#         "func_paramenters":{
#             "number_args":2,
#             "arguments":{
#                 "a":'int',
#                 "b":'char'
#             },
#             "return_type":'int',
#             "scope":3,
#         },
#         "varibles":{
#             "a":{
#                 "value":3,
#                 "type":"int",
#                 "scope":0,
#                 "line_no":1
#                 "isMacro":1
#                 "isConst":1
#                 "offset": <>
#             }
#             # "b":{
#             #     .
#             #     .
#             # }
#         }
#     }
# }

symbolTable={
    # "predefined_functions":{
    #     "printf":{
    #         "func_paramenters":{
    #             "number_args":100,
    #             "arguments":{
    #                 0:'char*',
    #                 1:'int'
    #             },
    #             "return_type":'int',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    #     "scanf":{
    #         "func_paramenters":{
    #             "number_args":100,
    #             "arguments":{
    #                 0:'char*',
    #                 1:'int'
    #             },
    #             "return_type":'int',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    #     "fprintf":{
    #         "func_paramenters":{
    #             "number_args":100,
    #             "arguments":{
    #                 0:'file_pointer',
    #                 1:'char*',
    #                 2:'int'
    #             },
    #             "return_type":'int',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    #     "fscanf":{
    #         "func_paramenters":{
    #             "number_args":100,
    #             "arguments":{
    #                 0:'file_pointer',
    #                 1:'char*',
    #                 2:'int'
    #             },
    #             "return_type":'int',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    #     "fopen":{
    #         "func_paramenters":{
    #             "number_args":2,
    #             "arguments":{
    #                 0:'char*',
    #                 1:'char*',
    #             },
    #             "return_type":'file_pointer',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    #     "fclose":{
    #         "func_paramenters":{
    #             "number_args":2,
    #             "arguments":{
    #                 0:'char*',
    #                 1:'char*',
    #             },
    #             "return_type":'file_pointer',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    #     "exp":{
    #         "func_paramenters":{
    #             "number_args":1,
    #             "arguments":{
    #                 0:'int',
    #             },
    #             "return_type":'float',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    #     "floor":{
    #         "func_paramenters":{
    #             "number_args":1,
    #             "arguments":{
    #                 0:'float',
    #             },
    #             "return_type":'int',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    #     "ceil":{
    #         "func_paramenters":{
    #             "number_args":1,
    #             "arguments":{
    #                 0:'float',
    #             },
    #             "return_type":'int',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    #     "abs":{
    #         "func_paramenters":{
    #             "number_args":1,
    #             "arguments":{
    #                 0:'int',
    #             },
    #             "return_type":'int',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    #     "pow":{
    #         "func_paramenters":{
    #             "number_args":2,
    #             "arguments":{
    #                 0:'float',
    #                 1:'int'
    #             },
    #             "return_type":'float',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    #     "sizeof":{
    #         "func_paramenters":{
    #             "number_args":1,
    #             "arguments":{
    #                 0:'char*',
    #             },
    #             "return_type":'int',
    #             "scope":0
    #         },
    #         "variables":{}
    #     },
    # },
    "variables":{},
    "dataTypes":{}
}

global_stack=[]
global_node=symbolTable

tac_code = []
global_tac_code=[]

#This array contains global id for each variable
program_variables = {}
var_global_ctr = 0
total_errors = 0

#Assuming 64 bit architecture
data_type_size = {
    "int": 4,
    "long": 8,
    "char": 1,
    "short": 2,
    "float": 4,
    "double": 8,
    "long long": 8,
}