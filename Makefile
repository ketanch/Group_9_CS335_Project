1:
	@echo "Running test case 1"
	@python3 src/parser.py tests/test1.c  

2:
	@echo "Running test case 2"
	@python3 src/parser.py tests/test2.c  

3:
	@echo "Running test case 3"
	@python3 src/parser.py tests/test3.c  

4:
	@echo "Running test case 4"
	@python3 src/parser.py tests/test4.c  

5:
	@echo "Running test case 5"
	@python3 src/parser.py tests/test5.c  

6:
	@echo "Running test case 6"
	@python3 src/parser.py tests/test6.c  

7:
	@echo "Running test case 7"
	@python3 src/parser.py tests/test7.c   

help:
	@echo "To run the test case number n run :\nmake n "

clean:
	@echo "Cleaning temporary files"
	@rm -rf src/__pycache__
	@rm -rf src/*.dot
	@rm -rf src/*.out
	@rm -rf src/parsetab.py
	@rm -rf *.png
	@rm -rf asm.s