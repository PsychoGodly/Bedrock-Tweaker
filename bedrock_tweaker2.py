import os
import shutil
import subprocess
import ctypes
import time
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Progressbar

def has_full_control_permissions(file_path):
    try:
        command = f'icacls "{file_path}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if "Everyone:(F)" in result.stdout:
            return True
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking permissions for {file_path}: {e}")
        return False

def set_full_control_permissions(file_path):
    if has_full_control_permissions(file_path):
        print(f"Full control permissions already granted for {file_path}")
        return True
    
    try:
        command = f'icacls "{file_path}" /grant Everyone:F /T'
        result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting permissions for {file_path}: {e}")
        print(e.output)
        return False

def take_ownership(file_path):
    try:
        command = f'takeown /F "{file_path}" /A /R /D Y'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error taking ownership of {file_path}: {e}")
        print(e.output)
        return False

def remove_read_only_attribute(file_path):
    try:
        os.chmod(file_path, 0o777)
        print(f"Read-only attribute removed from {file_path}")
        return True
    except Exception as e:
        print(f"Error removing read-only attribute from {file_path}: {e}")
        return False

def copy_and_replace_file(src, dst, progress_var, max_retries=5, delay=1):
    if os.path.exists(dst):
        print(f"File exists at {dst}, checking and setting permissions...")
        if not set_full_control_permissions(dst):
            print(f"Failed to set permissions for {dst}, attempting to copy anyway...")
        if not remove_read_only_attribute(dst):
            print(f"Failed to remove read-only attribute for {dst}, attempting to copy anyway...")
        if not take_ownership(dst):
            print(f"Failed to take ownership of {dst}, attempting to copy anyway...")
    
    total_progress = 0
    for attempt in range(max_retries):
        try:
            shutil.copy2(src, dst)
            print(f"Copied {src} to {dst}")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error copying file from {src} to {dst}: {e}. Retrying in {delay} seconds...")
                total_progress += 20  # Increment progress by 20% for each retry
                progress_var.set(total_progress)
                time.sleep(delay)
            else:
                print(f"Error copying file from {src} to {dst} after {max_retries} attempts: {e}")
                return False

def patch_files(progress_var):
    patch_folder = os.path.join(os.getcwd(), "Patch Files")
    syswow64_src = os.path.join(patch_folder, "sysWOW64", "Windows.ApplicationModel.Store.dll")
    system32_src = os.path.join(patch_folder, "System32", "Windows.ApplicationModel.Store.dll")
    
    windows_folder = os.path.expandvars(r"%WINDIR%")
    syswow64_dst = os.path.join(windows_folder, "SysWOW64", "Windows.ApplicationModel.Store.dll")
    system32_dst = os.path.join(windows_folder, "System32", "Windows.ApplicationModel.Store.dll")
    
    if not ctypes.windll.shell32.IsUserAnAdmin():
        messagebox.showerror("Error", "Please run the script with administrative privileges.")
        return
    
    total_progress = 0
    
    # Patching syswow64
    progress_var.set(total_progress)
    syswow64_success = copy_and_replace_file(syswow64_src, syswow64_dst, progress_var)
    if syswow64_success:
        total_progress += 50  # Increment progress by 50% for syswow64 success
    else:
        messagebox.showerror("Error", "An error occurred during the file copy process for syswow64. Please ensure the file is not in use and try again.")
    
    # Patching system32
    progress_var.set(total_progress)
    system32_success = copy_and_replace_file(system32_src, system32_dst, progress_var)
    if system32_success:
        total_progress += 50  # Increment progress by 50% for system32 success
    else:
        messagebox.showerror("Error", "An error occurred during the file copy process for system32. Please ensure the file is not in use and try again.")
    
    if syswow64_success or system32_success:
        messagebox.showwarning("Reboot Required", "A system reboot is required to complete the operation. Please reboot your system and run the script again to continue.")

def create_gui():
    root = tk.Tk()
    root.title("Bedrock Tweaker")
    root.geometry("300x150")
    root.iconbitmap("icon.ico")  # Set custom icon
    
    progress_var = tk.DoubleVar()
    progress_bar = Progressbar(root, orient="horizontal", length=200, mode="determinate", variable=progress_var)
    progress_bar.pack(pady=20)
    
    patch_button = tk.Button(root, text="Patch", command=lambda: patch_files(progress_var))
    patch_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
