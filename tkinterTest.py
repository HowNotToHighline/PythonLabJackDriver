import tkinter as tk

root = tk.Tk()
root.title("Jetse is awesome!")
root.geometry("1200x250")

status = tk.Label(root, text="Working", font=("Arial", 200), bg='blue')
status.pack(fill=tk.BOTH)
# status.grid()

def update_peak_force(kiloNewtons):
    status["text"] = "{0:.2f}".format(kiloNewtons) + 'kN'

counter = 100

def update_status():
    global counter

    if counter > 200:
        counter = 0
    else:
        counter += 1.13

    update_peak_force(counter)

    root.after(int(1.0), update_status)


# Launch the status message after 1 millisecond (when the window is loaded)
root.after(1, update_status)

root.mainloop()
print("done")