# Compiler
This repository contains a C compiler made as part of compiler course (CS335). The compiler properties are:  
**Source Language** : C  
**Implementation Language** : python 3  
**Target Architecture** : 64-bit MIPS

## Group Members
1. Ketan Chaturvedi (190428)
2. Sanjay Pander (190758)
3. Priyanshu Yadav (190652)
4. Hardik Sharma (190353)

## How to Run
To run the parser, cd into the compiler directory and use the following command:
```
python3 src/parser.py <test file path>
```
The above command will tell whether the input file is accepted by grammar or not and generates a .dot file in *src* directory. Now to generate Parser Automata, use the following command:
```
sfdp -x -Goverlap=scale -Tpng src/graph_file.dot > src/graph_out.png
```
-------------------------------------------------------------------------------
To run the lexer, cd into the compiler directory and use the following command:
```
python3 src/lexer.py <test file path>
```

## Milestones
1. **Milestone 1** : Added compiler source language specifications  
2. **Milestone 2** : Built lexer in python to tokenize C code
3. **Milestone 3** : Developed parser for the source language that outputs the Parser Automaton in a graphical form
    - Wrote grammer rules for the C language
    - Removed several reduce/reduce and shift/reduce conflicts
    - Used action table and goto table to generate .dot file which when processed by Graphviz, gave a Parser Automaton image file
