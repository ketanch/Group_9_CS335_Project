# Template for symbol table
# global has scope 0
# symbolTable={
#     "global_variables":{
#         "a":{
#             "value":3,
#             "type":"int",
#             "scope":0,
#             "line_no":1
#                 "isMacro":1
#                 "isConst":1
#         }
#         # "b":{
#         #     .
#         #     .
#         # }
#     },
#     "func_name":{
#         "func_paramenters":{
#             "number_args":2,
#             "argument_types":{
#                 "1":'int',
#                 "2":'char'
#             },
#             "return_type":'int',
#             "scope":3
#         },
#         "varibles":{
#             "a":{
#                 "value":3,
#                 "type":"int",
#                 "scope":0,
#                 "line_no":1
#                 "isMacro":1
#                 "isConst":1
#             }
#             # "b":{
#             #     .
#             #     .
#             # }
#         }
#     }
# }

symbolTable={
    "predefined_functions":{
        "printf":{
            "func_paramenters":{
                "number_args":100,
                "argument_types":{
                    0:'char*',
                    1:'int'
                },
                "return_type":'int',
                "scope":0
            },
            "variables":{}
        },
        "scanf":{
            "func_paramenters":{
                "number_args":100,
                "argument_types":{
                    0:'char*',
                    1:'int'
                },
                "return_type":'int',
                "scope":0
            },
            "variables":{}
        },
        "fprintf":{
            "func_paramenters":{
                "number_args":100,
                "argument_types":{
                    0:'file_pointer',
                    1:'char*',
                    2:'int'
                },
                "return_type":'int',
                "scope":0
            },
            "variables":{}
        },
        "fscanf":{
            "func_paramenters":{
                "number_args":100,
                "argument_types":{
                    0:'file_pointer',
                    1:'char*',
                    2:'int'
                },
                "return_type":'int',
                "scope":0
            },
            "variables":{}
        },
        "fopen":{
            "func_paramenters":{
                "number_args":2,
                "argument_types":{
                    0:'char*',
                    1:'char*',
                },
                "return_type":'file_pointer',
                "scope":0
            },
            "variables":{}
        },
        "fclose":{
            "func_paramenters":{
                "number_args":2,
                "argument_types":{
                    0:'char*',
                    1:'char*',
                },
                "return_type":'file_pointer',
                "scope":0
            },
            "variables":{}
        },
        "exp":{
            "func_paramenters":{
                "number_args":1,
                "argument_types":{
                    0:'int',
                },
                "return_type":'float',
                "scope":0
            },
            "variables":{}
        },
        "floor":{
            "func_paramenters":{
                "number_args":1,
                "argument_types":{
                    0:'float',
                },
                "return_type":'int',
                "scope":0
            },
            "variables":{}
        },
        "ceil":{
            "func_paramenters":{
                "number_args":1,
                "argument_types":{
                    0:'float',
                },
                "return_type":'int',
                "scope":0
            },
            "variables":{}
        },
        "abs":{
            "func_paramenters":{
                "number_args":1,
                "argument_types":{
                    0:'int',
                },
                "return_type":'int',
                "scope":0
            },
            "variables":{}
        },
        "pow":{
            "func_paramenters":{
                "number_args":2,
                "argument_types":{
                    0:'float',
                    1:'int'
                },
                "return_type":'float',
                "scope":0
            },
            "variables":{}
        },
        "sizeof":{
            "func_paramenters":{
                "number_args":1,
                "argument_types":{
                    0:'char*',
                },
                "return_type":'int',
                "scope":0
            },
            "variables":{}
        },
    },
    "global_variables":{}
}
