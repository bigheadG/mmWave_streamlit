#=============================================
# File Name: pc3_fish_ex0.py
#
# Requirement:
# Hardware: AOP
# Firmware: 
# lib: pc3_fish.py
# show v6
# type: raw
# Application: output RAW data
# library modified from pc3
#
# v6 data structure: readsxyz
#=============================================

# ===
import serial
from mmWave import pc3_fish
# V01: 
import pandas as pd
import numpy as np

############################################################################
# Parameters:
JB_select_df_flag 	= 1 # default 0, original; 1 for df DafaFrame mode more easier for reading 
JB_limit_points_num	= 10 # limit the length of displaying on data points for easy reading only, Alert: pending extra one line for mean values
JB_sensor1_height 	= 1.387 # unit: meter, Alert: depends on Sensor installation height   
JB_signal_noise_TH 	= 120 # deafult 120
JB_uart_port 		= "/dev/tty.SLAB_USBtoUART5" # via TX0 921600
# Alert: did not consider the TILT angle for axis conversion please computed by yourself on y and z values, x not chnaged
############################################################################
	
# Set display options to show all rows and columns without truncation
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', '{:.2f}'.format)

#pi 3 or pi 4
#port = serial.Serial("/dev/ttyS0",baudrate = 921600, timeout = 0.5)
#for Jetson nano UART port
#port = serial.Serial("/dev/ttyTHS1",baudrate = 921600, timeout = 0.5)
#port = serial.Serial("/dev/tty.usbmodemGY0052534",baudrate = 921600 , timeout = 0.5)
#port = serial.Serial("/dev/ttyACM1",baudrate = 921600 , timeout = 0.5)
#port = serial.Serial("/dev/tty.SLAB_USBtoUART",baudrate = 921600, timeout = 0.5)  
#port = serial.Serial("COM11",baudrate = 921600, timeout = 0.5)  
port = serial.Serial(JB_uart_port,baudrate = 921600, timeout = 0.5)  
radar = pc3_fish.Fish(port)
jb_columns = ['x', 'y', 'z', 'r', 'e', 'a', 'd', 's', 'fn']  # Specify the column headers

# V01: axis_convertion 
def jb_axis_convertion(df, h=0):
	# rule:
	# x1 = z
	# z1 = -x + h	
	dfc = df.copy()
	df['x'] = dfc['z'] 
	df['z'] = -dfc['x'] + h 
	return df
	
def uartGetTLVdata(name):
	fn_prev = 0
	fn = 0
	port.flushInput()
	while True:			
		(dck,v6,_,_) = radar.tlvRead(False)
		fn = radar.hdr.frameNumber
	
		if JB_select_df_flag == 0: 
			radar.headerShow()
			print(f'fn: {fn} dck:{dck} v6:{len(v6)}\n')
		
		if fn_prev != fn:
			fn_prev = fn 			 			
			if len(v6) != 0:
				if JB_select_df_flag == 0:
					print('---------- v6: Detected Object(Dynamic Points) ----------') 
					print(f'v6={v6}\n')
				else:
					df = pd.DataFrame(v6, columns = jb_columns)
					jb_shape_0 = df.shape # start
					
					######################################################
					# V01: axis_convertion
					# Alert: before processing run axis convertion first
					df = jb_axis_convertion(df)
					######################################################
					
					# offset z axis
					x = df['x']
					y = df['y']
					#z = df['z']
					#df['r'] = np.sqrt(x*x + y*y + z*z)					
					df['r'] = np.sqrt(x*x + y*y) # Alert: r only on x, y no z										
					df['z'] += JB_sensor1_height
										
					# Sort the DataFrame by the 's' column in descending order
					sort_df = df.sort_values(by='s', ascending=False)
					# Filter rows where 's' is greater than or equal to 120
					sort_s_df = sort_df[sort_df['s'] >= JB_signal_noise_TH]					
					# Sort the DataFrame by the 'y' column in descending order
					#sort_y_df = sort_s_df.sort_values(by='y', ascending=False) # sorted on y
					#sort_y_df = sort_s_df.sort_values(by='s', ascending=False) # tmp nochange
					sort_y_df = sort_s_df.sort_values(by='z', ascending=False) # sorted by z
					# convert a in degree
					sort_y_df['e'] *= (180 / 3.1415926)
					sort_y_df['a'] *= (180 / 3.1415926)
					jb_shape_filtered = sort_y_df.shape
					if sort_y_df.shape[0] > 0:
						print('\n\nfn= {}, FILTER: before {} => after {}, Alert: mean value vector at last row'.format(fn, jb_shape_0, jb_shape_filtered))						
						# limit showing points
						if sort_y_df.shape[0] >= JB_limit_points_num:
							df1 = sort_y_df[:JB_limit_points_num].copy()
							#print(sort_y_df[:JB_limit_points_num], '\n')
						else:
							df1 = sort_y_df.copy()
							print(sort_y_df, '\n')
						# Calculate the mean of each column
						column_means = df1.mean()
						# Add the mean values as a new row to the DataFrame
						#df1 = df1.append(column_means, ignore_index=True)
						#print(df1)						
					
				
			
			 
uartGetTLVdata("inCabin Detection Sensing(ODS)")
# ===


''' old version
import serial
#import struct
#import numpy as np

from mmWave import pc3_fish

#pi 3 or pi 4
#port = serial.Serial("/dev/ttyS0",baudrate = 921600, timeout = 0.5)
#for Jetson nano UART port
#port = serial.Serial("/dev/ttyTHS1",baudrate = 921600, timeout = 0.5)
#port = serial.Serial("/dev/tty.usbmodemGY0052534",baudrate = 921600 , timeout = 0.5)
#port = serial.Serial("/dev/ttyACM1",baudrate = 921600 , timeout = 0.5)
port = serial.Serial("/dev/tty.SLAB_USBtoUART6",baudrate = 921600, timeout = 0.5)  
radar = pc3_fish.Fish(port)

def uartGetTLVdata(name):
	fn_prev = 0
	fn = 0
	port.flushInput()
	while True:	
		
		(dck,v6,_,_) = radar.tlvRead(False)
		fn = radar.hdr.frameNumber
		
		radar.headerShow()
		print(f'fn: {fn} dck:{dck} v6:{len(v6)}\n')
		
		if fn_prev != fn:
			fn_prev = fn
			if len(v6) != 0:
				print(f'v6={v6}\n')
			
			 
uartGetTLVdata("PC3-fish Sensing(Fish)")
'''

exit()

#=============================================
# File Name: pc3_fish_ex0.py
#
# Requirement:
# Hardware: AOP
# Firmware: 
# lib: pc3_fish.py
# show v6
# type: raw
# Application: output RAW data
# library modified from pc3
#
# v6 data structure: readsxyz
#=============================================

# ===
import serial
from mmWave import pc3_fish
# V01: 
import pandas as pd
import numpy as np

############################################################################
# Parameters:
JB_sensor1_height 	= 1.387 # unit: meter
JB_limit_points_num = 2 # limit data points for easy reading only
JB_signal_noise_TH 	= 120 # deafult 120
JB_select_df_flag 	= 1 # default 0; 1 for df mode  
JB_uart_port 		= "COM8" # via TX0 921600
############################################################################
	
# Set display options to show all rows and columns without truncation
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', '{:.2f}'.format)

#pi 3 or pi 4
#port = serial.Serial("/dev/ttyS0",baudrate = 921600, timeout = 0.5)
#for Jetson nano UART port
#port = serial.Serial("/dev/ttyTHS1",baudrate = 921600, timeout = 0.5)
#port = serial.Serial("/dev/tty.usbmodemGY0052534",baudrate = 921600 , timeout = 0.5)
#port = serial.Serial("/dev/ttyACM1",baudrate = 921600 , timeout = 0.5)
#port = serial.Serial("/dev/tty.SLAB_USBtoUART",baudrate = 921600, timeout = 0.5)  
#port = serial.Serial("COM11",baudrate = 921600, timeout = 0.5)  
port = serial.Serial(JB_uart_port,baudrate = 921600, timeout = 0.5)  
radar = pc3_fish.Fish(port)
jb_columns = ['x', 'y', 'z', 'r', 'e', 'a', 'd', 's', 'fn']  # Specify the column headers

def uartGetTLVdata(name):
	fn_prev = 0
	fn = 0
	port.flushInput()
	while True:			
		(dck,v6,_,_) = radar.tlvRead(False)
		fn = radar.hdr.frameNumber
	
		if JB_select_df_flag == 0: 
			radar.headerShow()
			print(f'fn: {fn} dck:{dck} v6:{len(v6)}\n')
		
		if fn_prev != fn:
			fn_prev = fn 			 			
			if len(v6) != 0:
				if JB_select_df_flag == 0:
					print('---------- v6: Detected Object(Dynamic Points) ----------') 
					print(f'v6={v6}\n')
				else:
					df = pd.DataFrame(v6, columns = jb_columns)
					jb_shape_0 = df.shape # start
					# offset z axis
					x = df['x']
					y = df['y']
					#z = df['z']
					#df['r'] = np.sqrt(x*x + y*y + z*z)					
					df['r'] = np.sqrt(x*x + y*y) # Alert: r only on x, y no z										
					df['z'] += JB_sensor1_height
					# Sort the DataFrame by the 's' column in descending order
					sort_df = df.sort_values(by='s', ascending=False)
					# Filter rows where 's' is greater than or equal to 120
					sort_s_df = sort_df[sort_df['s'] >= JB_signal_noise_TH]					
					# Sort the DataFrame by the 'y' column in descending order
					#sort_y_df = sort_s_df.sort_values(by='y', ascending=False) # sorted on y
					#sort_y_df = sort_s_df.sort_values(by='s', ascending=False) # tmp nochange
					sort_y_df = sort_s_df.sort_values(by='z', ascending=False) # sorted by z
					# convert a in degree
					sort_y_df['e'] *= (180 / 3.1415926)
					sort_y_df['a'] *= (180 / 3.1415926)
					jb_shape_filtered = sort_y_df.shape
					if sort_y_df.shape[0] > 0:
						print('\n\nfn= {}, FILTER: before {} => after {}, Alert: mean value vector at last row'.format(fn, jb_shape_0, jb_shape_filtered))						
						# limit showing points
						if sort_y_df.shape[0] >= JB_limit_points_num:
							df1 = sort_y_df[:JB_limit_points_num].copy()
							#print(sort_y_df[:JB_limit_points_num], '\n')
						else:
							df1 = sort_y_df.copy()
							print(sort_y_df, '\n')
						# Calculate the mean of each column
						column_means = df1.mean()
						# Add the mean values as a new row to the DataFrame
						df1 = df1.append(column_means, ignore_index=True)
						print(df1)						
					
				
			
			 
uartGetTLVdata("inCabin Detection Sensing(ODS)")
# ===


''' old version
import serial
#import struct
#import numpy as np

from mmWave import pc3_fish

#pi 3 or pi 4
#port = serial.Serial("/dev/ttyS0",baudrate = 921600, timeout = 0.5)
#for Jetson nano UART port
#port = serial.Serial("/dev/ttyTHS1",baudrate = 921600, timeout = 0.5)
#port = serial.Serial("/dev/tty.usbmodemGY0052534",baudrate = 921600 , timeout = 0.5)
#port = serial.Serial("/dev/ttyACM1",baudrate = 921600 , timeout = 0.5)
port = serial.Serial("/dev/tty.SLAB_USBtoUART6",baudrate = 921600, timeout = 0.5)  
radar = pc3_fish.Fish(port)

def uartGetTLVdata(name):
	fn_prev = 0
	fn = 0
	port.flushInput()
	while True:	
		
		(dck,v6,_,_) = radar.tlvRead(False)
		fn = radar.hdr.frameNumber
		
		radar.headerShow()
		print(f'fn: {fn} dck:{dck} v6:{len(v6)}\n')
		
		if fn_prev != fn:
			fn_prev = fn
			if len(v6) != 0:
				print(f'v6={v6}\n')
			
			 
uartGetTLVdata("PC3-fish Sensing(Fish)")
'''






