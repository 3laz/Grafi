import time
import serial
import datetime
import csv
import threading as th
import pandas as pd


port_number = input("What COM port are you using? ")
port_number = port_number.upper()

ser = serial.Serial(
    port=port_number,
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS)

# Name of your file
file_name = input("Enter your filename:  ")

# Time between each measurement
delta_t = float(input("Time between each measurement (in seconds): "))

# Saves file as a .csv file
filename_complete = file_name + ".csv"

keep_going = True

"""
range_one = int(input("Select channel 1 range (0.002, 0.02, 0.2, 2, 20, 200) in mS: "))
range_two = int(input("Select channel 2 range (0.002, 0.02, 0.2, 2, 20, 200) in mS: "))
ser.write(bytearray("set channel 1 range "+str(range_one)+"\n", "ascii"))
ser.write(bytearray("get channel 1 range\n", "ascii"))
a = ser.readline()
print(a)
ser.write(bytearray("set channel 2 range "+str(range_two)+"\n", "ascii"))
ser.write(bytearray("get channel 2 range\n", "ascii"))
b = ser.readline()
print(b)
"""


def key_capture_thread():
    global keep_going
    input()
    keep_going = False

# Makes a new .csv file,  opens it and adds a new measurements every delta_t seconds
with open(filename_complete, 'w', newline="") as fw:
    writer = csv.writer(fw, delimiter=',')
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    i = 0
    while keep_going:
        time.sleep(delta_t)
        ser.write(b"r\n")
        measurement = ser.read_until(b"r\r\n")
        measurement = measurement.decode("ascii")
        measurement = " ".join(measurement.split())
        sample_measurement = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), measurement
        writer.writerow(sample_measurement)
        print("This is measurement number ", i + 1)
        print(measurement)
        i += 1


# Cleans the data and makes a datetime table with results from both probes
podatki = pd.read_csv(filename_complete, engine="python", delimiter=' |,', header=None, skiprows=2)
podatki = podatki.dropna(axis=1)
podatki = podatki.drop(podatki.columns[[2, 3, 8, 9, 10, 11, 12, 13]], axis=1)
podatki.columns = ["Date", "Time", "Channel 1", "Units 1", "Channel 2", "Units 2"]

# podatki.to_excel(final_filename)
final_filename = filename_complete + ".xlsx"
podatki.to_excel(final_filename)
ser.close()
