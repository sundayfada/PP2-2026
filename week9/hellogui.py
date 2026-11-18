from tkinter import tk

window = tk.Tk()
window.title("Hello 전재균")
window.geometry("400x200")

label = tk.Label(window, text = "Hello tkinter")
label.pack()

window.mainloop()