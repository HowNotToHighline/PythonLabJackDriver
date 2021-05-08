import tkinter as tk
import threading


class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.peak_force = None
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while not self.stopped():
            pass
        print("Quit tkinter")

    def get_peak_force(self):
        if self.peak_force is None:
            return 0
        return self.peak_force


root = tk.Tk()
root.title("Jetse is awesome!")
root.geometry("1200x250")

status = tk.Label(root, text="Loading", font=("Arial", 200))
status.grid()

def update_peak_force(kiloNewtons):
    status["text"] = "{0:.2f}".format(kiloNewtons) + 'kN'


counter = 100


def update_status():
    global counter

    if counter > 200:
        counter = 0
    else:
        counter += 1.13

    update_peak_force(150.29)

    root.after(int(1.0), update_status)


# Launch the status message after 1 millisecond (when the window is loaded)
root.after(1, update_status)

root.mainloop()
print("done")
