import serial
import numpy as np
import csv
import pandas as pd
import time
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import datetime
import math

"""
Taken from stack-exchange:
https://stackoverflow.com/questions/14313510/
    how-to-calculate-rolling-moving-average-using-numpy-scipy
yatu
"""
def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def main():
    serial_port='COM9'
    baud_rate=921600
    ser=serial.Serial(serial_port,baud_rate)
    
    #Leave in for testing with .csv file input (without bluetooth
    #testIn_filename = "test_data.csv" 
    #ser = open(testIn_filename, 'r')

    print("Connection established\n")

    #Wait for valid entry from user about their mode of operation before continuing
    #Filename with contain mode of operation and time of data collection
    invalid_entry = 1
    time_now_formatted = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    while invalid_entry:
        mode = int(input("Please enter mode of operation:\n1- Active Range of Motion\n2- Passive Range of Motion\n3- Daily Range of Motion\n"))
        if mode == 1:
            fileOut_name = time_now_formatted+"Active_ROM"
            invalid_entry=0
        elif mode ==2:
            fileOut_name = time_now_formatted+"Passive_ROM"
            invalid_entry=0
        elif mode ==3:
            fileOut_name = time_now_formatted+"Daily_ROM"
            invalid_entry=0
        else:
            print("Please enter a value between 1 to 3!\n")


    #Initialize empty data array
    data_array = []


    ser.reset_output_buffer()
    ser.reset_input_buffer()

    #Get initial time
    t0 = time.time()
    while True:
        try:
            #time.sleep(0.25) #Leave in for testing with .csv file input (without Bluetooth)
            data = ser.readline()
            data=data.decode("utf-8")
            data = data.strip()
            data = data.split(",") #Get 6 item list
            data = [float(i) for i in data]

            #Convert rad to degrees
            for i in range(3):
                data[i] = 180-abs(data[i]*180/math.pi)
            #Find time relative to beginning
            relative_time = time.time()-t0
            data.insert(0,relative_time)
            print(data[3])
            data_array.append(data)
            
        except KeyboardInterrupt:
            print("\nYou have finished recording")
            ser.close()

            data_array.pop(0) #Remove first data due to possible spikes from the initial Bluetooth connection
            
            data_array = np.array(data_array)
            mean_values = np.mean(data_array, axis=0)
            averaging = 75
            knee_flex_angles =  data_array[:,3]
            knee_flex_angles_filt = moving_average(knee_flex_angles,averaging)
            
            time_list = data_array[:,0]
            time_list_average = moving_average(time_list,averaging) #Get a time_list the same length as the filtered data

            #Minimum samples between peaks/troughs should be 300
            #the peaks should be greater than the grand average component and the troughs should be less than average
            peak_indices, _ = find_peaks(knee_flex_angles_filt, height = np.mean(knee_flex_angles_filt),distance=300)
            trough_indices, _  = find_peaks(-knee_flex_angles_filt, height = -np.mean(knee_flex_angles_filt),distance=300)

            fig = plt.figure()
            plt.plot(time_list_average[peak_indices], knee_flex_angles_filt[peak_indices], "xr")
            plt.plot(time_list_average[trough_indices], knee_flex_angles_filt[trough_indices], "xr")

            plt.plot(time_list_average,knee_flex_angles_filt)

            plt.title("Knee Joint Angle Over Time")
            plt.xlabel("Time(s)")
            plt.ylabel("Angle (degrees)")

            
            plt.legend(['Peaks and Troughs'])
            plt.show()
            fig.savefig(fileOut_name+'.png')

            flexion = np.mean(knee_flex_angles_filt[trough_indices])
            extension = np.mean(knee_flex_angles_filt[peak_indices])
            ROM = extension-flexion

            summary = ['Min_flexion: ', flexion, 'max_extension: ', extension, "ROM", ROM]
            header = ['Time', 'X-axis_Angle', 'Y_axis_Angle', 'Z_axis_angle']

            with open(fileOut_name+'.csv', 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)

                #Write Summary Data
                writer.writerow(summary)
                    
                # write the header
                writer.writerow(header)

                # write multiple rows
                writer.writerows(data_array)
            
            break


        except:
            print("An error has occurred, please try again")
            ser.close()
            break

main()

