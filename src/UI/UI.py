import tkinter as tk
from tkinter import ttk
import sumData

def get_input_value():
    """Function to retrieve the input and display it."""
    user_input = name_entry.get()
    global UserDate
    if user_input:
        result_label.config(text=f"Submitted!", foreground="green")
        UserDate = user_input
        name_entry.delete(0, tk.END) 
    else:
        result_label.config(text="Please enter date.", foreground="red")


root = tk.Tk()
root.title("ok")

root.geometry("400x300")
root.resizable(False, False)

label = tk.Label(root, text="Weather Rainforecast", font=("Arial", 16))
label.pack()


button = tk.Button(root, text="click me to say hello world", command=lambda: print(sumData.hw))
button.pack()

name_entry = ttk.Entry(root, width=30)
name_entry.place(x=100, y=100)
name_entry.focus_set()

submit_button = ttk.Button(root, text="Submit", command=get_input_value)
submit_button.pack(pady=10)

result_label = ttk.Label(root, text="", font=("Arial", 12))
result_label.place(x=150, y=150)

endbutton = tk.Button(root, text="End", command=lambda: root.destroy())
endbutton.place(x=150, y=200)

root.mainloop()

print("UserDate:", UserDate)