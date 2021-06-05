from labjack import ljm
import tkinter as tk
import datetime
import os
import threading


class App(threading.Thread):

    def __init__(self, _positive_channel, _negative_channel, _excitation_channel, _sample_rate, _excitation_voltage,
                 _signal_level, _calibration_factor, _calibration_offset, _do_hardware_config):
        threading.Thread.__init__(self)

        self.positive_channel = _positive_channel
        self.negative_channel = _negative_channel
        self.excitation_channel = _excitation_channel
        self.sample_rate = _sample_rate
        self.excitation_voltage = _excitation_voltage
        self.signal_level = _signal_level
        self.calibration_factor = _calibration_factor
        self.calibration_offset = _calibration_offset
        self.do_hardware_config = _do_hardware_config

        # Open LabJack
        self.handle = ljm.openS("T7", "ETHERNET", "10.0.5.69")
        info = ljm.getHandleInfo(self.handle)
        print("\nOpened a LabJack with Device type: %i, Connection type: %i,\n"
              "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
              (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

        self.positive_channel_name = "AIN%i" % self.positive_channel
        self.negative_channel_name = "AIN%i" % self.negative_channel
        self.excitation_channel_name = "AIN%i" % self.excitation_channel

        name = "labjackVisual"
        rate_us = int(1000000 / self.sample_rate)

        if self.do_hardware_config:
            # Setup differential mode https://labjack.com/support/datasheets/t-series/ain#differential
            ljm.eWriteName(self.handle, self.positive_channel_name + "_NEGATIVE_CH", self.negative_channel)
            # Set right range
            ljm.eWriteName(self.handle, self.positive_channel_name + "_RANGE", self.signal_level)

            # aNames = ["AIN0_RANGE", "AIN1_RANGE", "STREAM_SETTLING_US",
            #           "STREAM_RESOLUTION_INDEX"]
            # aValues = [10.0, 10.0, 0, 0]
            # ljm.eWriteNames(self.handle, len(aNames), aNames, aValues)

            # TODO: Configure LJTick-DAC
            # It seems quite complicated, I don't really feel like implementing it
            # Maybe I'll implement it some day, maybe only in the "proper" versions, maybe we'll remove it all together

        # Get the current working directory
        cwd = os.getcwd()

        # Build a file-name and the file path.
        file_name = datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S%p") + "-%s.csv" % name
        file_path = os.path.join(cwd, file_name)

        # Open the file & write a header-line
        self.f = open(file_path, 'w')
        self.f.write("Current tick (us), Raw measurement, Excitation voltage, Force\n")

        # Print some program-initialization information
        print("Reading {0:.0f} times per second and saving data to the file:\n - {1}\n".format(self.sample_rate, file_path))

        # Prepare final variables for program execution
        self.peak_force = None

    def run(self):
        # Stream example: https://github.com/labjack/labjack-ljm-python/blob/b9ce507e6d1d90cd9b2acf72924b7e531dcfa7dc/Examples/More/Stream/stream_basic_with_stream_out.py
        global stop_threads

        stream_handle = 0
        streamInNames = [self.positive_channel_name]
        aScanList = ljm.namesToAddresses(len(streamInNames), streamInNames)[0]
        scanRate = self.sample_rate
        scansPerRead = 100
        actualScanRate = ljm.eStreamStart(stream_handle, scansPerRead, len(streamInNames), aScanList, scanRate)
        print("Stream started with a scan rate of {0:.0f}Hz ({0:.2f}Hz to be exact)".format(scanRate, actualScanRate))

        NUM_IN_CHANNELS = len(streamInNames)

        excitation_voltage = ljm.eReadName(self.handle, self.excitation_channel_name)
        while True:
            cur_tick = ljm.getHostTick()

            if stop_threads:
                break

            ret = ljm.eStreamRead(stream_handle)

            # Note that the Python eStreamData will return a data list of size
            # scansPerRead*TOTAL_NUM_CHANNELS, but only the first
            # scansPerRead*NUM_IN_CHANNELS samples in the list are valid. Output
            # channels are not included in the eStreamRead's returned data.
            data = ret[0][0:(scansPerRead * NUM_IN_CHANNELS)]
            if ret[1] > 200 or ret[2] > 200:
                print("Buffer overrun, deviceScanBacklog: {0:d}\tljmScanBacklog: {1:d}".format(ret[1], ret[2]))
            scans = len(data) / NUM_IN_CHANNELS

            # Shouldn't this be scans?
            for i in range(scansPerRead):
                raw_measurement = data[i * NUM_IN_CHANNELS + 0]

                force = (raw_measurement * (20000 / (0.003 * self.excitation_voltage) / 224.8089)) + self.calibration_offset
                if self.peak_force is None or force > self.peak_force:
                    self.peak_force = force

                data_string = "{0:d}, {1:f}, {2:.3f}, {3:.3f}\n".format(cur_tick, raw_measurement, excitation_voltage, force)
                self.f.write(data_string)

        # Close file
        self.f.close()

        # Close handles
        ljm.eStreamStop(stream_handle)
        ljm.close(self.handle)

        print("Quit thread")

    def get_peak_force(self):
        if self.peak_force is None:
            return 0
        return self.peak_force


# ========== User config starts here ==========
# Positive channel has to be even, and the negative channel has to be one higher
positive_channel = 0  # AIN0
negative_channel = positive_channel + 1  # AIN1
excitation_channel = 2  # AIN2
sample_rate = 1000.0
excitation_voltage = 9.18

signal_level = 0.1  # Set to 0.01 for force less then 1/3 max capacity

# Divide by 224.8089 to convert pounds to kN
calibration_factor = 20000 / (0.003 * excitation_voltage) / 224.8089
calibration_offset = -85 / 224.8089

do_hardware_config = False  # This is experimental, and could brick something
# ========== User config ends here ==========

root = tk.Tk()
root.title("Jetse is awesome!")
root.geometry("1200x250")

status = tk.Label(root, text="Loading", font=("Arial", 200))
status.grid()

stop_threads = False
app = App(positive_channel, negative_channel, excitation_channel, sample_rate, excitation_voltage, signal_level,
          calibration_factor, calibration_offset, do_hardware_config)
app.start()


def update_status():
    # Get peak force from thread
    peak_force = app.get_peak_force()
    if peak_force is not None:
        status["text"] = "{0:.2f}".format(peak_force) + 'kN'
    # Update UI with about 10Hz
    root.after(100, update_status)


# Launch the status message after 1 millisecond (when the window is loaded)
root.after(1, update_status)

# This call is blocking until the window closes
root.mainloop()

# Stop thread
stop_threads = True
