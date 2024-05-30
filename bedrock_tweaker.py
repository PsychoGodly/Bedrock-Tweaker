import os
import shutil
import subprocess
import ctypes
import time

def has_full_control_permissions(file_path):
    """
    Check if the file has full control permissions for Everyone.
    """
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
    """
    Set full control permissions for Everyone on the specified file.
    """
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

def copy_and_replace_file(src, dst, max_retries=5, delay=10, force_replace=False):
    """
    Copy a file from src to dst, replacing the existing file if necessary.
    Retries the operation up to max_retries times if the file is in use.
    """
    if os.path.exists(dst):
        print(f"File exists at {dst}, checking and setting permissions...")
        # Check and set permissions before replacing the file
        if not set_full_control_permissions(dst):
            print(f"Failed to set permissions for {dst}, attempting to copy anyway...")
    
    for attempt in range(max_retries):
        try:
            # Attempt to force replace the file by opening it with exclusive access
            with open(dst, "wb") as f:
                pass
            
            shutil.copy2(src, dst)
            print(f"Copied {src} to {dst}")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error copying file from {src} to {dst}: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Error copying file from {src} to {dst} after {max_retries} attempts: {e}")
                return False

def main():
    patch_folder = os.path.join(os.getcwd(), "Patch Files")
    syswow64_src = os.path.join(patch_folder, "sysWOW64", "Windows.ApplicationModel.Store.dll")
    system32_src = os.path.join(patch_folder, "System32", "Windows.ApplicationModel.Store.dll")
    
    windows_folder = os.path.expandvars(r"%WINDIR%")
    syswow64_dst = os.path.join(windows_folder, "SysWOW64", "Windows.ApplicationModel.Store.dll")
    system32_dst = os.path.join(windows_folder, "System32", "Windows.ApplicationModel.Store.dll")
    
    # Check if script is run with administrative privileges
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Please run the script with administrative privileges.")
        return
    
    # Copy and replace the files
    syswow64_success = copy_and_replace_file(syswow64_src, syswow64_dst, force_replace=True)
    system32_success = copy_and_replace_file(system32_src, system32_dst, force_replace=True)
    
    if syswow64_success and system32_success:
        print("Successfully done.")
    else:
        print("An error occurred during the file copy process. Please ensure the files are not in use and try again.")

if __name__ == "__main__":
    main()
