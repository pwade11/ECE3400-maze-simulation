import sys
from ctypes import cdll
import os
import numpy as np
#simulate navigation for ece3400 lab 4/final
# by Peter Wade (pfw44)
# 11/5/21

#arguments to call: 'step' makes it so that you pring everthing out

#need the nav function to take distance inputs, and output numbers corresponding to operations (move, turn, etc)

#format for data arrays:
#even number indecies are barier stuff, odd numbers are valid spaces
# grid = 	[[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],
#			[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
#			[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
#			[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
#			[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
#			[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
#			[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
#			[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
#			[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
#			[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "^", "|"],
#			[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],
#]

#1 means explored, empty barier area means no barier, arrow means robot, direction indicates direction

#How to use:
#there are four ways to call this program:
#1. python nav_sim.py test
#-- this will run it in test mode, which is for debugging this file, and should likely not be needed
#2. python nav_sim.py step <True/False> <relative directory path>
#-- this mode will run set mazes, that are located in the directory path
#-- the step <True/False> indicates if you want to step through each action, or just
#-- see if the code will sucessfully find all accessible blocks
#3. python nav_sim.py step <True/False> random
#-- the step <True/False> part has the same action as above
#-- this will cause it to try one random maze
#4. python nav_sim.py step <True/False> random <n>
#-- this will cause it to try n random mazes

#see this stackoverflow post for info about how to produce a file from your C code
#https://stackoverflow.com/questions/145270/calling-c-c-from-python
#arduino code should just be C code in general, so as long as you dont have arduino specific functions, 
#you should just copy the function into a C file and compile
#this code assumes your final shared library file will be called "nav_code_lib.so"
#and will be in the same directory as this python file
#This has more details on compiling with gcc for this type of thing
#cprogramming.com/tutorial/shared-libraries-linux-gcc.html

#commands I used to compile the C program:
#gcc -c -Wall -Werror -fpic nav_test_test.c
#gcc -shared -o -nav_code_lib.so nav_test_test.o


#you should set some values so that they are realistic and will work with your code, specifically:
#distempyblock - distance measured for a full empty block (15 inches)
#distemptywall - distance measured for an empty wall width (1.5 inches I think)
#distrobotside - distance measured to the side when the robot is centered in one block
#distrobotfront - distrance to the front when the robot is centered in a block

def dist_west():
	intr_row = grid[roboty]
	selected_pos = robotx-1
	add_dist = 0
	while (intr_row[selected_pos] != "|"):
		selected_pos -= 2
		add_dist += distemptywall +distempyblock
		#if no block to the side, the dist will be an empty wall space + empty block
	return(add_dist)

def dist_east():
	intr_row = grid[roboty]
	selected_pos = robotx+1
	add_dist = 0
	while (intr_row[selected_pos] != "|"):
		selected_pos += 2
		add_dist += distemptywall +distempyblock
		#if no block to the side, the dist will be an empty wall space + empty block
	return(add_dist)

def dist_south():
	intr_col = []
	for i in range(len(grid)):
		intr_col.append(grid[i][robotx])
	selected_pos = roboty+1
	add_dist = 0
	while (intr_col[selected_pos] != "-"):
		selected_pos += 2
		add_dist += distemptywall +distempyblock
	return(add_dist)

def dist_north():
	intr_col = []
	for i in range(len(grid)):
		intr_col.append(grid[i][robotx])
	selected_pos = roboty -1
	add_dist = 0
	while (intr_col[selected_pos] != "-"):
		selected_pos -= 2
		add_dist += distemptywall +distempyblock
	return(add_dist)

def gen_distances():
	#determine the distances to send to the robot
	if(robot_dir == 0):
		#if facing north
		leftdist = distrobotside + dist_west()
		forwarddist = distrobotfront + dist_north()
		rightdist = distrobotside + dist_east()
	elif(robot_dir == 1):
		#if facing east
		leftdist = distrobotside + dist_north()
		forwarddist = distrobotfront + dist_east()
		rightdist = distrobotside + dist_south()
	elif(robot_dir == 2):
		#if facing south
		leftdist = distrobotside + dist_east()
		forwarddist = distrobotfront + dist_south()
		rightdist = distrobotside + dist_west()
	else:
		#if facing west
		leftdist = distrobotside + dist_south()
		forwarddist = distrobotfront + dist_west()
		rightdist = distrobotside + dist_north()

	return (leftdist, forwarddist, rightdist)

def check_north():
	#check if can move to north
	if(grid[roboty-1][robotx] == "-"):
		return False
	else:
		return True

def check_south():
	#check if can move to the south
	if(grid[roboty+1][robotx] == "-"):
		return False
	else:
		return True

def check_east():
	#check if can move east
	if(grid[roboty][robotx+1] == "|"):
		return False
	else:
		return True

def check_west():
	#check if can move west
	if(grid[roboty][robotx-1] == "|"):
		return False
	else:
		return True

def set_dir_arrow():
	global robot_dir
	global roboty
	global robotx
	global grid
	if(robot_dir == 0):
		grid[roboty][robotx] = "^"
	elif(robot_dir == 1):
		grid[roboty][robotx] = ">"
	elif(robot_dir == 2):
		grid[roboty][robotx] = "v"
	elif(robot_dir == 3):
		grid[roboty][robotx] = "<"
	else:
		#raise error
		raise Exception("invalid direction")

def check_complete():
	#check all the locations, and see that all possible areas are explored
	for i in range(5):
		for j in range(5):
			if(grid[2*i+1][2*j+1] == "0"):
				#if it is not found, check if it was possible go get there
				if((grid[2*i+2][2*j+1] != "-") or (grid[2*i][2*j+1] != "-") or (grid[2*i+1][2*j+2] != "|") or (grid[2*i+1][2*j] != "|")):
					#if it is acceccible
					#raise error: missed one
					return 2
	return 1

def print_grid():
	for i in range(len(grid)):
		printstr = ""
		for x in range(len(grid[i])):
			printstr += grid[i][x]
		print(printstr)
	print("\n")
	print("======================")
	print("\n")

def moveloop(nav_func):
	global robot_dir
	global roboty
	global robotx
	global grid
	if(step):
		print_grid()
	ld, fd, rd = gen_distances()
	state = nav_func(ld, fd, rd)
	if(state == 0):
		#if told to move forward, check if can and then do so
		if(robot_dir == 0):
			#if facing north
			valid = check_north()
			if(valid):
				#move forward
				grid[roboty][robotx] = "1"
				#set as found
				grid[roboty-2][robotx] = "^"
				#move forward
				roboty -= 2
			else:
				#raise an error
				raise Exception("cannot move forward")
		elif(robot_dir == 1):
			#if facing east
			valid = check_east()
			if(valid):
				grid[roboty][robotx] = "1"
				#set as found
				grid[roboty][robotx+2] = ">"
				#move forward
				robotx += 2
			else:
				#raise error
				raise Exception("cannot move forward")
		elif(robot_dir == 2):
			#if facing south
			valid = check_south()
			if(valid):
				#move forward
				grid[roboty][robotx] = "1"
				#set as found
				grid[roboty+2][robotx] = "v"
				#move forward
				roboty += 2
			else:
				#raise an error
				raise Exception("cannot move forward")
		elif(robot_dir == 3):
			#if facing west
			valid = check_west()
			if(valid):
				grid[roboty][robotx] = "1"
				#set as found
				grid[roboty][robotx-2] = "<"
				#move forward
				robotx -= 2
			else:
				#raise error
				raise Exception("cannot move forward")
		else:
			#raise error
			raise Exception("invalid direction")

	elif(state == 1):
		#if told to turn right, do so
		robot_dir = (robot_dir + 1)%4
		set_dir_arrow()
	elif(state == 2):
		#if told to turn left, do so
		robot_dir = (robot_dir + 3)%4
		set_dir_arrow()
	elif(state == 3):
		#if told to turn around
		robot_dir = (robot_dir + 2)%4
		set_dir_arrow()
	elif(state == 4):
		#if think done
		return check_complete()
	else:
		raise Exception("invalid state")
	return 0

def test_nav_func():
	#this is to ensure that this code is functional, nothing else
	#should not be used if you are testing your own function
	global grid 
	#grid for test 1
	global testing
	global robotx
	global roboty
	global robot_dir
	grid = [["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "^", "|"],
	[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ]]

	run_program(grid,testing,test_1,1)
	#try test 1
	robotx = 9
	roboty = 9
	testing = 1
	robot_dir = 0
	grid = [["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "^", "|"],
	[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ]]
	run_program(grid,testing,test_2,1)
	#try test 2

	grid = [["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "^", "|"],
	[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ]]
	testing = 1
	robotx = 9
	roboty = 9
	robot_dir = 0
	try:	
		run_program(grid,testing,test_3,1)
	except:
		print("sucessfully caught the exception")
	#try test 3

	grid = [["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],
	[	"|", "0", "|", "0", "|", "0", " ", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", " ", "-", " ", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", " ", "-", " ", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", " ", "0", "|"],
	[	"|", "-", "-", "-", "-", " ", "-", " ", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", " ", "-", " ", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", " ", "0", "|", "^", "|"],
	[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ]]
	testing = 1
	robotx = 9
	roboty = 9
	robot_dir = 0
	run_program(grid,testing,test_4,1)


	grid = [["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],
	[	"|", "0", "|", "0", "|", "0", " ", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", " ", "-", " ", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", " ", "-", " ", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", " ", "0", "|"],
	[	"|", "-", "-", "-", "-", " ", "-", " ", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", " ", "-", " ", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", " ", "0", "|", "^", "|"],
	[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ]]
	testing = 1
	robotx = 9
	roboty = 9
	robot_dir = 0
	run_program(grid,testing,test_5,1)

	grid = [["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", " ", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "^", "|"],
	[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ]]
	testing = 1
	robotx = 9
	roboty = 9
	robot_dir = 0
	try:	
		run_program(grid,testing,test_6,1)
	except:
		print("sucessfully caught the exception")
	#try test 6


	grid = [["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "^", "|"],
	[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ]]

	testing = 1
	robotx = 9
	roboty = 9
	robot_dir = 0
	global GRID_DIRECTORY
	GRID_DIRECTORY='./test_mazes'
	grid = load_grid_files()[0]
	#test reading a file for the grid
	print("loaded file")
	run_program(grid,testing,test_4,1)

def test_1(ld,fd,rd):
	#check that this code is functional
	actions =[4]
	global testing
	testing += 1
	#use global variable to keep iterating through each action 
	return(actions[testing-2])

def test_2(ld,fd,rd):
	#check that this code is functional
	actions =[0,0,0,0,4]
	global testing
	testing += 1
	#use global variable to keep iterating through each action 
	return(actions[testing-2])

def test_3(ld,fd,rd):
	#check that this code is functional
	#test illegal move
	actions =[0,0,0,0,0,4]
	global testing
	testing += 1
	#use global variable to keep iterating through each action 
	return(actions[testing-2])

def test_4(ld,fd,rd):
	#check that this code is functional
	#test more complex movement patterns
	actions =[0,0,0,0,3,0,0,1,0,1,0,0,2,0,2,0,0,0,0,2,0,2,0,0,4]
	global testing
	testing += 1
	#use global variable to keep iterating through each action 
	return(actions[testing-2])

def test_5(ld, fd,rd):
	#check that this code is functional
	#test thinking it is done too early
	actions =[0,0,0,0,3,0,0,1,0,1,0,0,2,0,2,0,0,0,0,4]
	global testing
	testing += 1
	#use global variable to keep iterating through each action 
	return(actions[testing-2])

def test_6(ld,fd,rd):
	#check that this code is functional
	#test illegal move to the side
	actions =[0,0,0,1,0,4]
	global testing
	testing += 1
	#use global variable to keep iterating through each action 
	return(actions[testing-2])

def run_program(grid, testing, test_func, step):
	if(testing):
		nav_func = test_func
	else:
		#import the C (arduino) program for navigation:
		#based on this: https://stackoverflow.com/questions/145270/calling-c-c-from-python
		lib = cdll.LoadLibrary('./nav_code_lib.so')
		nav_func = lib.nav_func
		#rename it so easier to deal with

	fin_state = 0
	while(fin_state == 0):
		if(step):
			input("Press enter to continue")
			fin_state = moveloop(nav_func)
		else:
			fin_state= moveloop(nav_func)

	print_grid()
	print("\n")
	if(fin_state == 2):
		print("failed to find all")
	else:
		print("found all")

def load_grid_files():
	#store the grids as csv files, and load them
	gridlist = []
	for filename in os.listdir(GRID_DIRECTORY):
		if(filename.endswith(".csv")):
			f = open(GRID_DIRECTORY+'/'+filename,'r')
			new_grid = []
			for line in f:	
				new_grid.append(line.strip().split(','))
			gridlist.append(new_grid)
	return gridlist

def sweep_through_runs():
	#test the navigation code
	global grid 
	global testing
	global robotx
	global roboty
	global robot_dir
	global step
	gridlist = load_grid_files()

	for grid_inst in gridlist:
		#reset everything
		testing = 0
		robotx = 9
		roboty = 9
		robot_dir = 0
		grid = grid_inst
		run_program(grid,0,None,step)

def gen_rand_maze():
	#make a random grid
	curgrid = [["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "0", "|"],
	[	"|", "-", "-", "-", "-", "-", "-", "-", "-", "-", "|" ],
	[	"|", "0", "|", "0", "|", "0", "|", "0", "|", "^", "|"],
	[	"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-" ]]
	
	#need a 5 row x 4 column for the verticle lines, and a 5 row by 4 column for horizontal
	horizontal = np.random.randint(0,2,(4,5))
	verticle = np.random.randint(0,2,(5,4))
	for i in range(len(horizontal)):
		for j in range(len(horizontal[i])):
			if(horizontal[i][j]):
				curgrid[2*(i+1)][(2*j)+1] = " "
	for i in range(len(verticle)):
		for j in range(len(verticle[i])):
			if(verticle[i][j]):
				curgrid[2*i+1][2*(j+1)] = " "
	return(curgrid)

def random_maze_sweep(num_trials):
	global grid 
	global testing
	global robotx
	global roboty
	global robot_dir
	global step
	for i in range(num_trials):
		grid = gen_rand_maze()
		#reset everything
		testing = 0
		robotx = 9
		roboty = 9
		robot_dir = 0
		run_program(grid,0,None,step)
	

#this should be the directory where you store a set of csv files to represent the grids

testing = 0
step =0
	

distempyblock = 1
distemptywall = 1
distrobotside = 1
distrobotfront= 1
#distances for if there is an empty block and empty wall
#also distance from side of robot to wall, and front of robot of wall

#movemnt instructions
# 0 = move forwad
# 1 = turn right
# 2 = turn left
# 3 = turn around
# 4 = done

robotx = 9
roboty = 9

robot_dir = 0
#direction, 0 = north, 1= east, 2= south, 3 = west 

grid = []

if(len(sys.argv) == 2):
	if(sys.argv[1] == 'test'):
		#testing mode, dont use actual c code, just fixed inputs
		testing = 1
		step = 1
		test_nav_func()
		#above is to ensure this code works, not your code
elif(len(sys.argv) == 4 or len(sys.argv) == 5):
	#format must be nav_sim.py step <step val>
	if(sys.argv[1] == 'step' and sys.argv[2] == 'True'):
		step = 1
	elif(sys.argv[1] == 'step' and sys.argv[2] == 'False'):
		step = 0
	else:
		#error
		raise Exception("Invalid command line entries")
	if(sys.argv[3] == "random"):
		if(len(sys.argv) == 5):
			random_maze_sweep(sys.argv[4])
		else:
			random_maze_sweep(1)
	else:
		GRID_DIRECTORY = sys.argv[3]
		sweep_through_runs()
		#if not random, assume that they are giving a directory of files
else:
	raise Exception("Invalid command line entries")



