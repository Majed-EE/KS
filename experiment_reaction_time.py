
from socket import *
import threading
import src
from proto_util import ctrl_command_pb2 as command
import time
import random
import keyboard
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import csv
import logging


file_name=__file__
file_name=file_name[:-3]+"_log.log"
logging.basicConfig(
    filename=file_name,
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.info("file name: %s",file_name)




global act_time_stamp, press_time_stamp, n_index, array_n,cmd_dict,yn,joint_name,active_joint,points
# act_time_stamp is the actual time stamp
t_Start = time.time() # reference time

active_joint=1


data_points=100

n_index=10 #number of plot points per experiment
points = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]*n_index # total samples= len(points) * i_index
yn=[-1 for _ in range(len(points))]
def click_test(): # equivalent to time stamp in dhg_test_2
    global array_n,yn
    print("Press any key to timestamp. Press 'q' to quit.")
    while True:
        key = keyboard.read_event(suppress = True)
        if key.event_type=="up":
                
            print(key)
            if key.name == 'q':  # Exit if 'q' is pressed
                break
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            print("Key pressed at:", timestamp)
	    print(press_time_stamp)
            press_time_stamp[array_n]=time.time()-t_Start
	    yn[array_n]=1
            
            print("Timestamp recorded at:", timestamp)

        else:
            continue



    

threads=[]
xn=n_index
# recording press and act time
act_time_stamp=[]
press_time_stamp=[-1 for _ in range(len(points))]


thread_click = threading.Thread(target=click_test)
thread_click.start()
threads.append(thread_click)
array_n=0
cmd_dict={}
joint_name=["Thumb","Index","Middle","Ring","Pinky"]

print("info for the active joint: ")
print(joint_name[active_joint])

def dex_force(i,test): # works same as before
    global cmd_dict,active_joint
    if i==1:
	for x in range (len(joint_name)):
            if joint_name[x]==joint_name[active_joint]:
                cmd_dict[joint_name[x]]={"Stiffness":test,"SetPoint":0.2}
            else:
                
                cmd_dict[joint_name[x]]={"Stiffness":0,"SetPoint":0} # realax condition
    
    else:
    	for x in range (len(joint_name)):
		cmd_dict[joint_name[x]]={"Stiffness":0,"SetPoint":0} # realax condition
        return False
    print(cmd_dict)


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



def test_worker(command_write_worker):
    global array_n, points
    To=1
    for x in range(len(points)+1):
	array_n=x
        if array_n==len(points):
		print("Last rest")
		dex_force(1,0)
	        new_impedance_control = set_test_impedance_control()
	        command_write_worker.add_new_impedance_control(337785601,new_impedance_control)
		break
        
	time.sleep(T0)	
	print("y and stiffness:")
	print(points)
	print(x)
	print(points[x])	
	dex_force(1,points[x])

        new_impedance_control = set_test_impedance_control()
        command_write_worker.add_new_impedance_control(337785601, new_impedance_control)  # the id need to be the id of your hands
	act_time_stamp.append(time.time()-t_Start)        
	time.sleep(T0)


# connect to server

host_ip = "127.0.0.1"
host_port = 55555
sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host_ip, host_port))
print("changing")

try:

	command_write_worker_i = src.command_write_worker(sock)
	command_write_worker_t = threading.Thread(target=command_write_worker_i.worker)
	command_write_worker_t.start()
        threads.append(command_write_worker_t)

	test_worker(command_write_worker_i)
	print("ending loop")
        print("graceful shutdown test")

	print("ending")

#	plt.step(act_time_stamp, xn, where='post')
#	#plt.scatter(array_n, xn, color='red')
#	plt.scatter(act_time_stamp, xn, color='red')
#	plt.scatter(press_time_stamp, xn, color='black')
#	print(press_time_stamp)
#	print(act_time_stamp)
	
#	title_text= 'To:1s, Joint Name: '+ joint_name[active_joint]
#	plt.xlabel('Time in Second')
#	plt.ylabel('Stiffness Factor')	
#	plt.title(title_text)
#	plt.grid(True)
#	plt.xlim(0, len(xn))
#	figure_name=joint_name[active_joint]+".png"
#	plt.savefig(figure_name)
#	plt.show()



#	diff_chat=[]

#	for x in range(len(press_time_stamp)):
#   		if press_time_stamp[x]!=-1:
#        		diff_chat.append(1000*(-act_time_stamp[x]+press_time_stamp[x]))
#			print("index")
#			print(x)
#	diff_plot=[_ for _ in range(len(diff_chat))]
#	print(len(diff_chat),len(diff_plot))
#	print(press_time_stamp)
#	print(act_time_stamp)
#	print(diff_chat)
	
#	print(len(xn),len(xn_1),len(yn))

	# constant threshold calculation


	csv_file="temporal_resolution.csv"
	data_dict={"actual time stamp":[act_time_stamp],"reaction time stamp":[press_time_stamp]}
	# Load existing data or start new
	json_file="temporal_resolution.json"
	if os.path.exists(json_file):
		with open(json_file, 'w') as f:
    			json.dump(data_dict, f, indent=2)
  
	# save csv

	with open(csv_file, 'a') as f:
	    writer = csv.writer(f)
	    # Write header only if file is empty
	    if f.tell() == 0:
		writer.writerow(['actual_time', 'reaction_time'])
	    writer.writerow(row)
	

	print(len(act_time_stamp))
	print(len(press_time_stamp))
	#print(act_time_stamp, press_time_stamp)


	data=[]
	for indi in range(len(press_time_stamp)):
		if press_time_stamp[indi]!=-1:
			time_differ=1000*(press_time_stamp[indi]-act_time_stamp[indi]) # time difference in mili seconds
			
			data.append(time_differ)
			print(time_differ)
	print(data)		


	plt.hist(data, bins=50, density=True)


	plt.xlabel('Time in Milliseconds')
	plt.ylabel('Density')
	name_title="Reaction Time Plot Joint: "+joint_name[active_joint]  
	plt.title(name_title)



	mean_value = np.mean(data)


	plt.axvline(x=mean_value, color='red', linestyle='--', label='Mean')


	plt.legend()
	name_fig="reaction_joint_"+joint_name[active_joint]+".png"
	plt.savefig(name_fig)


	plt.show()



	thread1.join()
	command_write_worker_t.join()
	sock.close()
except KeyboardInterrupt:
	print("keyboard interrupt")

finally:
        # Close the socket
        sock.close()
        print("Socket disconnected.")



