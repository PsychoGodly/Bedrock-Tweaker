import os
import shutil
import subprocess
import ctypes

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

def copy_and_replace_file(src, dst):
    """
    Copy a file from src to dst, replacing the existing file if necessary.
    """
    if os.path.exists(dst):
        print(f"File exists at {dst}, checking and setting permissions...")
        # Check and set permissions before replacing the file
        if not set_full_control_permissions(dst):
            return False
    try:
        shutil.copy2(src, dst)
        print(f"Copied {src} to {dst}")
        return True
    except Exception as e:
        print(f"Error copying file from {src} to {dst}: {e}")
        return False

def main():
    patch_folder = os.path.join(os.getcwd(), "Patch Files")
    syswow64_src = os.path.join(patch_folder, "sysWOW64", "Windows.ApplicationModel.Store.dll")  # Replace with actual file name
    system32_src = os.path.join(patch_folder, "System32", "Windows.ApplicationModel.Store.dll")  # Replace with actual file name
    
    windows_folder = os.path.expandvars(r"%WINDIR%")
    syswow64_dst = os.path.join(windows_folder, "SysWOW64", "Windows.ApplicationModel.Store.dll")  # Replace with actual file name
    system32_dst = os.path.join(windows_folder, "System32", "Windows.ApplicationModel.Store.dll")  # Replace with actual file name
    
    # Check if script is run with administrative privileges
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Please run the script with administrative privileges.")
        return
    
    # Copy and replace the files
    if copy_and_replace_file(syswow64_src, syswow64_dst) and copy_and_replace_file(system32_src, system32_dst):
        print("Successfully done.")
    else:
        print("An error occurred during the file copy process.")

if __name__ == "__main__":
    main()
