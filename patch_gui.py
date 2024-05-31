import tkinter as tk
from tkinter import messagebox
import patch_functionality

def patch_files():
    result = patch_functionality.patch_files()
    if "Successfully" in result:
        messagebox.showinfo("Success", result)
    else:
        messagebox.showerror("Error", result)

def create_gui():
    root = tk.Tk()
    root.title("Bedrock Tweaker")

    patch_button = tk.Button(root, text="Patch", command=patch_files)
    patch_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
