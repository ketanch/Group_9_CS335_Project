# Compiler
This repository contains a C compiler made as part of compiler course (CS335). The compiler properties are:  
**Source Language** : C  
**Implementation Language** : python 3  
**Target Architecture** : MIPS

## Group Members
1. Ketan Chaturvedi (190428)
2. Sanjay Pander (190758)
3. Priyanshu Yadav (190652)
4. Hardik Sharma (190353)

## How to Run
To run the parser, cd into the compiler directory and use the following command:

python3 src/parser.py <test file path>

The above command will generate an assembly file `out.s`, which can be loaded into spim simulator and then executed.
The output of parser is in *output.s*

## Milestones
1. **Milestone 1** : Added compiler source language specifications  
2. **Milestone 2** : Built lexer in python to tokenize C code
3. **Milestone 3** : Developed parser for the source language that outputs the Parser Automaton in a graphical form
    - Wrote grammer rules for the C language
    - Removed several reduce/reduce and shift/reduce conflicts
    - Used action table and goto table to generate .dot file which when processed by Graphviz, gave a Parser Automaton image file
4. **Milestone 4** : Added error handling to the parser
5. **Milestone 5** : Generated TAC code for the input code 
6. **Milestone 6** : Bootstrapped the complete compiler. Added functionalities for code generation.