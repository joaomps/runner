import time
import requests
import schedule
import socket
import subprocess

get_jobs_to_run_ws = 'https://expressjs-prisma-production-36b8.up.railway.app/getjobs'

# Get the name of the macOS device
macos_device_name = socket.gethostname()

def check_and_run_jobs():
    try:
        r = requests.get(get_jobs_to_run_ws)
        if r.status_code == 200:
            data = r.json()

           # Check if the devicename matches the name of the macOS device
            if data['devicename'] == macos_device_name:
                # Run the command specified in pathtorun in a new terminal tab
                cmd = ['osascript', '-e', 'tell application "Terminal" to do script "{}"'.format(data['pathtorun'])]
                subprocess.Popen(cmd)

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
        else:
            return None
    except requests.exceptions.Timeout:
        print("The request timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None

# check_and_run_jobs()

# Schedule the function to run every 2 minutes
schedule.every(1).minute.do(check_and_run_jobs)

# Keep the script running and execute the scheduled jobs
while True:
    schedule.run_pending()
    time.sleep(1)