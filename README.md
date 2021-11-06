# ECE3400-maze-simulation
To test out navigation algorithms for lab4/the final

simulate navigation for ece3400 lab 4/final
by Peter Wade (pfw44)
11/5/21

I make no guarantees that this works perfectly.

arguments to call: 'step' makes it so that you pring everthing out

need the nav function to take distance inputs, and output numbers corresponding to operations (move, turn, etc)

format for data arrays:
even number indecies are barier stuff, odd numbers are valid spaces

grid = 	

	[[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],

	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "^", "|"],
	
	[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],]

1 means explored, empty barier area means no barier, arrow means robot, direction indicates direction

How to use:
there are four ways to call this program:
1. python nav_sim.py test
-- this will run it in test mode, which is for debugging this file, and should likely not be needed
2. python nav_sim.py step <True/False> <relative directory path>
-- this mode will run set mazes, that are located in the directory path
-- the step <True/False> indicates if you want to step through each action, or just
-- see if the code will sucessfully find all accessible blocks
3. python nav_sim.py step <True/False> random
-- the step <True/False> part has the same action as above
-- this will cause it to try one random maze
4. python nav_sim.py step <True/False> random <n>
-- this will cause it to try n random mazes

see this stackoverflow post for info about how to produce a file from your C code: https://stackoverflow.com/questions/145270/calling-c-c-from-python
	
arduino code should just be C code in general, so as long as you dont have arduino specific functions, you should just copy the function into a C file and compile
	
this code assumes your final shared library file will be called "nav_code_lib.so"
	
and will be in the same directory as this python file
	
This has more details on compiling with gcc for this type of thing: cprogramming.com/tutorial/shared-libraries-linux-gcc.html

commands I used to compile the C program:
	
gcc -c -Wall -Werror -fpic nav_test_test.c
	
gcc -shared -o -nav_code_lib.so nav_test_test.o


you should set some values so that they are realistic and will work with your code, specifically:
	
distempyblock - distance measured for a full empty block (15 inches)
	
distemptywall - distance measured for an empty wall width (1.5 inches I think)
	
distrobotside - distance measured to the side when the robot is centered in one block
	
distrobotfront - distrance to the front when the robot is centered in a block


I am also including a example c file that shows what you need to do with your arduino code. Just copy the navigation part into a c file and make a header. 
	
I also included one example maze csv file
