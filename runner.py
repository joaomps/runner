import time
import requests
import schedule
import socket
import subprocess
import os
from datetime import datetime

get_jobs_to_run_ws = 'https://expressjs-prisma-production-36b8.up.railway.app/getjobs'

# Get the name of the macOS device
macos_device_name = socket.gethostname()

def clear_terminal():
    os.system('clear')

clear_terminal()  # Clear terminal before running jobs

def check_and_run_jobs():
    try:
        r = requests.get(get_jobs_to_run_ws)
        if r is not None and r.status_code == 200:
            data = r.json()
            
            if data is None:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"{current_time} - No jobs to run, checking again soon...")
                return
            
           # Check if the devicename matches the name of the macOS device
            if data['devicename'] == macos_device_name:
                print_job_details(data)
                # Run the command specified in pathtorun in a new terminal tab
                cmd = ['osascript', '-e', 'tell application "Terminal" to do script "{}"'.format(data['pathtorun'])]
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                id = data['id']
                delete_job_ws = f"https://expressjs-prisma-production-36b8.up.railway.app/deletejob/{id}"
                headers = {'Content-Type': 'application/json'}
                response = requests.delete(delete_job_ws, headers=headers)

                #sleep for 5 seconds to avoid rate limiting
                time.sleep(5)

                if response.status_code == 200:
                    deleted_job = response.json()
                    print(f"Deleted job with ID {deleted_job['id']}")
                else:
                    print("Error deleting job")

    except requests.exceptions.Timeout:
        print("The request timed out.")
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)

def print_job_details(job):
    print(f"Job details:\n"
          f"ID: {job['id']}\n"
          f"Account to run: {job['accounttorun']}\n"
          f"Path to run: {job['pathtorun']}\n"
          f"Device name: {job['devicename']}\n")
    
# check_and_run_jobs()

# Schedule the function to run every 2 minutes
schedule.every(1).minute.do(check_and_run_jobs)

# Keep the script running and execute the scheduled jobs
while True:
    schedule.run_pending()
    time.sleep(1)