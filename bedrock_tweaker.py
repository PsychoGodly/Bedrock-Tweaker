import os
import shutil
import subprocess
import ctypes

def set_full_control_permissions(file_path):
    """
    Set full control permissions for Everyone on the specified file.
    """
    try:
        command = f'icacls "{file_path}" /grant Everyone:F /T'
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting permissions for {file_path}: {e}")
        return False

def copy_and_replace_file(src, dst):
    """
    Copy a file from src to dst, replacing the existing file if necessary.
    """
    if os.path.exists(dst):
        # Check and set permissions before replacing the file
        if not set_full_control_permissions(dst):
            return False
    shutil.copy2(src, dst)
    return True

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
    if copy_and_replace_file(syswow64_src, syswow64_dst) and copy_and_replace_file(system32_src, system32_dst):
        print("Successfully done.")
    else:
        print("An error occurred during the file copy process.")

if __name__ == "__main__":
    main()
