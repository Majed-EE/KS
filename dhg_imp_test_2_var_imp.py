
from socket import *
import threading
import src
from proto_util import ctrl_command_pb2 as command
import time
import random
import keyboard
from datetime import datetime


import logging

logging.basicConfig(
    filename='dhg_imp_test_2_log.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.info("file name: %s",file_name)




def time_stamp():
    print("Press any key to timestamp. Press 'q' to quit.") # why pressing "q" does not work? 
    loop=True     
    while loop:
        key = keyboard.read_event(suppress = True)
        if key.event_type=="up":
                
            print(key)
            if key.name == 'q':  # Exit if 'q' is pressed
               logging.info("exiting the loop: ")
               loop=False 
               break

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            print("Key pressed at:", timestamp)
        else:
            continue



global cmd_dict
cmd_dict={}
joint_name=["Thumb","Index","Middle","Ring","Pinky"]
def dex_force(i,stiff_val): # i!=1 means reset to 0 (relax) condition, stiff_val is stiffness 
    global cmd_dict
    if i==1: # i=1 for specific joint change
	for x in range (len(joint_name)):
            if joint_name[x]=="Index": # dex force only for Index
                cmd_dict[joint_name[x]]={"Stiffness":stiff_val,"SetPoint":0.2}
            else:
                
                cmd_dict[joint_name[x]]={"Stiffness":0,"SetPoint":0} # realax condition
    
    else:
    	for x in range (len(joint_name)):
		cmd_dict[joint_name[x]]={"Stiffness":0,"SetPoint":0} # realax condition
    # cmd_dict carries what? 
    print("print from dexforce--> command dict {}".format(cmd_dict))
    


def set_test_impedance_control():
    global cmd_dict
    new_impedance_control = command.ImpedanceControl()
    new_impedance_control.Thumb.Stiffness = cmd_dict["Thumb"]["Stiffness"] #0.5  # 0-1,stand for hardness of the force,0 stand for no force
    new_impedance_control.Thumb.SetPoint =  cmd_dict["Thumb"]["SetPoint"] #0.3  # 0-1,stand for position of the force,sign stand for direction,positive number for inward,minus number for outward
    new_impedance_control.Index.Stiffness = cmd_dict["Index"]["Stiffness"] #1
    new_impedance_control.Index.SetPoint =  cmd_dict["Index"]["SetPoint"] #1
    new_impedance_control.Middle.Stiffness = cmd_dict["Middle"]["Stiffness"]#0.5
    new_impedance_control.Middle.SetPoint = cmd_dict["Middle"]["SetPoint"] #-0.8
    new_impedance_control.Ring.Stiffness = cmd_dict["Ring"]["Stiffness"] #0.5
    new_impedance_control.Ring.SetPoint =  cmd_dict["Ring"]["SetPoint"] #0.5
    new_impedance_control.Pinky.Stiffness = cmd_dict["Pinky"]["Stiffness"] #0.5
    new_impedance_control.Pinky.SetPoint =  cmd_dict["Pinky"]["SetPoint"] #0.5
    new_impedance_control.has_index = True  # true stand for the command cannot be ignore,false stand for the command can be ignore
    return new_impedance_control



def test_worker(command_write_worker): # main thread for changing stiffness
    i=0
    T0 = 1 # Temporal resolution constant name? 
    t_run=3
    mode_run=3
    current_mod=1 # ==1 change index, !=1 relax
    while True:
        if current_mod==1:
            print("index mode")
	else:
            print("ending loop")
	    print("graceful shutdown test")
	    dex_force(-1,0)

	    new_impedance_control = set_test_impedance_control()
            command_write_worker.add_new_impedance_control(337785601,
                                                       new_impedance_control)
	    logging.info("closing the socket joining the thread, inside thread worker")
	    command_write_worker_t.join()
	    thread.join() # which thread is this? 
            sock.close()
	    break

            

	stiff_factor=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0]
	for x in range (len(stiff_factor)):   
		print("current mode: %s\nstiff factor: %s"%(current_mod, stiff_factor[x]))
		print("current mode and stiff")
		print(current_mod,stiff_factor[x])		
		dex_force(current_mod,stiff_factor[x]) 

        	new_impedance_control = set_test_impedance_control()
        	command_write_worker.add_new_impedance_control(337785601,
                                                       new_impedance_control)  # the id need to be the id of your hands
        	time.sleep(T0) # T0
		timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
		logging.info("Time Stamp {}".format(timestamp))
        
        # why do we even need those variables?
        i=i+1
        print(t_run-i)
        if i==t_run:
            i=0
#           print(i)
            current_mod=current_mod+1
            print("i: {} and current mode: {}".format(i,current_mod)
	    

# connect to server
logging.info("on the main thread: connecting to server")

host_ip = "127.0.0.1"
host_port = 55555
sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host_ip, host_port))

logging.info("Starting the thread: time stamp")
thread_time = threading.Thread(target=time_stamp)
thread_time.start()
threads=[]
threads.append(thread_time)
try:
	logging.info("Starting the thread: Command worker")
	command_write_worker_i = src.command_write_worker(sock)
	command_write_worker_t = threading.Thread(target=command_write_worker_i.worker)
	command_write_worker_t.start()
	test_worker(command_write_worker_i) # Note: test worker is in the mani thread 
	threads.append(comman_write_worker_i)
except KeyboardInterrupt:
	print("keyboard interrupt")

finally:
        # Close the socket
        sock.close()
        logging.info("Socket disconnected.")
	logging.info("ending the thread")
	if thread_time.isAlive():
	thread_time.join()



