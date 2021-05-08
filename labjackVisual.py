from labjack import ljm
import tkinter as tk
import datetime
import os

# Open first found LabJack
handle = ljm.openS("T7", "ETHERNET", "10.0.5.69")  # T7 device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("\nOpened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# ========== User config starts here ==========
# Positive channel has to be even, and the negative channel has to be one higher
positive_channel = 0  # AIN0
negative_channel = positive_channel + 1  # AIN1
excitation_channel = 2  # AIN2
sample_rate = 1000
excitation_voltage = 9.18

signal_level = 0.1  # Set to 0.01 for force less then 1/3 max capacity

calibration_factor = 20000 / (0.003 * excitation_voltage)
calibration_offset = -85

do_hardware_config = False  # This is experimental, and could brick something
# ========== User config ends here ==========

positive_channel_name = "AIN%i" % positive_channel
negative_channel_name = "AIN%i" % negative_channel
excitation_channel_name = "AIN%i" % excitation_channel

name = "labjackVisual"
rate_ms = int(1000 / sample_rate)
rate_us = int(1000000 / sample_rate)

if do_hardware_config:
    # Setup differential mode https://labjack.com/support/datasheets/t-series/ain#differential
    ljm.eWriteName(handle, positive_channel_name + "_NEGATIVE_CH", negative_channel)
    # Set right range
    ljm.eWriteName(handle, positive_channel_name + "_RANGE", signal_level)
    # TODO: Configure LJTick-DAC
    # It seems quite complicated, I don't really feel like implementing it
    # Maybe I'll implement it some day, maybe only in the "proper" versions, maybe we'll remove it all together

# Get the current working directory
cwd = os.getcwd()

# Build a file-name and the file path.
file_name = datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S%p") + "-%s.csv" % name
file_path = os.path.join(cwd, file_name)

# Open the file & write a header-line
f = open(file_path, 'w')
f.write("Iteration, Current tick (us), Number of skipped intervals, Raw measurement, Force\n")

# Print some program-initialization information
print("Reading %i times per second and saving data to the file:\n - %s\n" % (sample_rate, file_path))

# Prepare final variables for program execution
interval_handle = 0
ljm.startInterval(interval_handle, rate_us)
cur_iteration = 0
peak_force = None

root = tk.Tk()
root.title("Jetse is awesome!")
root.geometry("1000x250")

status = tk.Label(root, text="Loading", font=("Arial", 200))
status.grid()


def update_peak_force(kilo_newtons):
    status["text"] = "{0:.0f}".format(kilo_newtons) + 'lb'


def update_status():
    print("update_status")
    global peak_force
    global cur_iteration

    num_skipped_intervals = ljm.waitForNextInterval(interval_handle)
    print("After next interval")
    cur_tick = ljm.getHostTick()

    raw_measurement = ljm.eReadName(handle, positive_channel_name)

    force = (raw_measurement * calibration_factor) + calibration_offset
    if peak_force is None or force > peak_force:
        print("Updating peak force")
        peak_force = force
        update_peak_force(peak_force)

    data_string = "{0:d}, {1:d}, {2:d}, {3:f}, {4:.3f}".format(cur_iteration, cur_tick, num_skipped_intervals,
                                                               raw_measurement, force)
    print(data_string)
    f.write(data_string + "\n")
    cur_iteration += 1

    root.after(rate_ms, update_status)


# Launch the status message after 1 millisecond (when the window is loaded)
root.after(1, update_status)

# This call is blocking until the window closes
root.mainloop()

# Close file
f.close()

# Close handles
ljm.cleanInterval(interval_handle)
ljm.close(handle)
