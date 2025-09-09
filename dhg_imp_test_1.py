# test for basic dhg code and also for debugging
# dgh code for changing impedence 
from socket import *
import threading
import src
from proto_util import ctrl_command_pb2 as command
import time

global command_table
command_table=[]
for x in range (5):
	command_table.append([0,0])
for x in command_table:
	print(x)
global stiff
def set_test_impedance_control():# function to change impedance
    global command_table,stiff
    
    new_impedance_control = command.ImpedanceControl()
    new_impedance_control.Thumb.Stiffness = command_table[0][0] #0.5  # 0-1,stand for hardness of the force,0 stand for no force
    new_impedance_control.Thumb.SetPoint =  command_table[0][1] #0.3  # 0-1,stand for position of the force,sign stand for direction,positive number for inward,minus number for outward
    new_impedance_control.Index.Stiffness = command_table[1][0] #1  [finger_id][stiffness]
    new_impedance_control.Index.SetPoint =  command_table[1][1] #1    [finger_id][setpoint_id] -ve setpoint=>cant open hand, +ve setpoint=>cant close hand
    new_impedance_control.Middle.Stiffness =command_table[2][0] #0.5
    new_impedance_control.Middle.SetPoint = command_table[2][1] #-0.8
    new_impedance_control.Ring.Stiffness = command_table[3][0] #0.5
    new_impedance_control.Ring.SetPoint = command_table[3][1] #0.5
    new_impedance_control.Pinky.Stiffness = command_table[4][0] #0.5
    new_impedance_control.Pinky.SetPoint = command_table[4][1] #0.5
    new_impedance_control.has_index = True  # true stand for the command cannot be ignore,false stand for the command can be ignore
    return new_impedance_control

stiff=0
def test_worker(command_write_worker):
    i=0
    global stiff
    while True:
        new_impedance_control = set_test_impedance_control() # changing impedance
        command_write_worker.add_new_impedance_control(337785601,
                                                       new_impedance_control)  # the id need to be the id of your hands
        time.sleep(1)
        i=i+1
	stiff=stiff+0.1
	print("stiffness")
        print(stiff)
        print(10-i)
        if i==10:
            print("changing stiffness and set point back to 0 ")
	    stiff=0
	    for x in range (5):
		command_table.append([0,0]) # why not command_table[0]=[0,0]
	    for x in command_table:
		print("command table new")		
		print(x)

	    new_impedance_control = set_test_impedance_control() # setting back to zero
            command_write_worker.add_new_impedance_control(337785601,
                                                       new_impedance_control)
	    print("graceful shutdown test")
            sock.close()
            break





# connect to server

host_ip = "127.0.0.1"
host_port = 55555
sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host_ip, host_port))
print("changing")

try:

	command_write_worker_i = src.command_write_worker(sock)

	test_worker(command_write_worker_i)
except KeyboardInterrupt:
	print("keyboard interrupt")

finally:
        # Close the socket
        sock.close()
        print("Socket disconnected.")



