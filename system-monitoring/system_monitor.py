import os
import sys
import time
import hashlib
import shutil
import socket
import psutil
import subprocess
from datetime import datetime
from pathlib import Path


def check_file_permissions(file_path, directory):
    file_stat = os.stat(file_path)
    file_perms = oct(file_stat.st_mode)[-3:]
    
    if int(file_perms, 8) > 0o644:
        print(f"The file '{file_path}' has insecure permissions.")
        os.chmod(file_path, 0o644)
        print("Permissions corrected to rw-r--r--.")
    
    print(f"Scanning directory '{directory}' for .sh files...")
    for script in Path(directory).glob("*.sh"):
        if not os.access(script, os.X_OK):
            print(f"The script '{script}' is not executable.")
        else:
            print(f"The script '{script}' is executable.")


def check_file_integrity(file_path, directory):
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return
    
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    
    filename = os.path.basename(file_path)
    file_found = False
    
    for path in Path(directory).glob(filename):
        with open(path, 'rb') as f:
            other_hash = hashlib.md5(f.read()).hexdigest()
        
        if file_hash == other_hash:
            print(f"File integrity verified for '{path}'.")
            file_found = True
        else:
            print(f"File integrity compromised for '{path}'.")
    
    if not file_found:
        print(f"File '{filename}' not found or not verified in the directory '{directory}'.")


def monitor_disk_space():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('disk_usage.log', 'a') as log:
        log.write(f"{current_time}: Checking disk usage...\n")
        
        for partition in psutil.disk_partitions():
            if partition.fstype:
                usage = psutil.disk_usage(partition.mountpoint)
                percent = usage.percent
                message = f"{current_time}: {'Warning: ' if percent > 80 else 'OK! '}Partition {partition.device} mounted on {partition.mountpoint} is {'above 80%' if percent > 80 else 'fine'}."
                print(message)
                log.write(message + "\n")


def track_system_processes():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('process_log.txt', 'a') as log:
        memory = psutil.virtual_memory()
        log.write(f"{current_time}: Total used memory:\n")
        log.write(f"Used: {memory.used/1024/1024:.1f}MB, Free: {memory.free/1024/1024:.1f}MB, Total: {memory.total/1024/1024:.1f}MB\n")
        
        log.write(f"{current_time}: Listing top memory-consuming processes...\n")
        processes = sorted(psutil.process_iter(['pid', 'memory_percent', 'name']), 
                         key=lambda x: x.info['memory_percent'], 
                         reverse=True)[:5]
        
        for proc in processes:
            log.write(f"{current_time}: PID {proc.info['pid']}, Mem: {proc.info['memory_percent']:.1f}%, Command: {proc.info['name']}\n")


def check_service_status(services=None):
    if services is None:
        services = ['nginx', 'ssh', 'cron']
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('service_status.log', 'a') as log:
        log.write(f"{current_time}: Checking service statuses...\n")
        
        for service in services:
            try:
                result = subprocess.run(['systemctl', 'is-active', service], 
                                     capture_output=True, text=True)
                status = 'running' if result.returncode == 0 else 'not running'
                message = f"{current_time}: Service '{service}' is {status}."
                log.write(message + "\n")
                
                if status == 'not running':
                    log.write(f"{current_time}: Service '{service}' is not running. Restarting...\n")
                    subprocess.run(['systemctl', 'restart', service])
            except subprocess.CalledProcessError:
                log.write(f"{current_time}: Error checking service '{service}'\n")


def automate_backup(directory):
    if not os.path.isdir(directory):
        print(f"Error: The provided directory '{directory}' does not exist.")
        return 1
    
    backup_dir = "./backup"
    Path(backup_dir).mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = f"{backup_dir}/{os.path.basename(directory)}_{timestamp}.tar.gz"
    
    try:
        shutil.make_archive(backup_file[:-7], 'gztar', directory)
        print(f"Backup created successfully at {backup_file}")
    except Exception as e:
        print(f"Error: Backup failed. {str(e)}")
        return 2


def main():
    functions = {
        "1": ("File Permissions and Security Script", check_file_permissions),
        "2": ("File Integrity Checker", check_file_integrity),
        "3": ("Disk Space Monitor", monitor_disk_space),
        "4": ("System Process Tracker", track_system_processes),
        "5": ("Service Status Checker", check_service_status),
        "6": ("Backup Automation Script", automate_backup)
    }
    
    print("Choose an exercise to run:")
    for key, (name, _) in functions.items():
        print(f"{key}) {name}")
    
    choice = input("Enter the number of the exercise: ")
    
    if choice in functions:
        name, func = functions[choice]
        if choice in ["1", "2"]:
            file_path = input("Enter the file path: ")
            directory = input("Enter the directory path: ")
            func(file_path, directory)
        elif choice == "5":
            services = input("Enter service names separated by spaces: ").split()
            func(services)
        elif choice == "6":
            directory = input("Enter the directory path to backup: ")
            func(directory)
        else:
            func()
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main()