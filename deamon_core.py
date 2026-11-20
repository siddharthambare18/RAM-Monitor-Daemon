import psutil as ps 
import time 
import logging 
import os
import requests
from logging.handlers import RotatingFileHandler

rotator = RotatingFileHandler('system.log', maxBytes=5*1024*1024, backupCount=2)
logging.basicConfig(
    handlers=[rotator],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


RAM_THRESHOLD = 75.0
TARGET_HOGS = ['chrome.exe',  'spotify.exe', 'python.exe']
WEBHOOK_URL = "https://discord.com/api/webhooks/1520689607291830425/7slWB222vaIBP_sQ3doU7DCxFs4_t1yY6ljF37mv7rQgM4TkgN8CHhsq-sQcpDSFpE_7" 

DAEMON_PID = os.getpid()

def send_discord_alert(message):
    try:
        data = {"content": f"🚨 **SYSTEM ALERT** 🚨\n{message}"}
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        logging.error(f"Failed to send Discord alert: {e}")

def check_ram_vitals():
    ram = ps.virtual_memory().percent
    
    if ram > RAM_THRESHOLD:
        logging.warning(f"Critical resource Strain: RAM at {ram}%")
        
        highest_mem_mb = 0
        culprit = None
        
        
        for proc in ps.process_iter(['pid','name','memory_info']):
            try:
                proc_id = proc.info['pid']
                proc_name = proc.info['name']
                
                proc_vms_mb = proc.info['memory_info'].vms / (1024 * 1024)

                if proc_id == DAEMON_PID:
                    continue

                if proc_name not in TARGET_HOGS:
                    continue
                    
                # If the target is eating more than 150 MB of Virtual Memory, target acquired!
                elif proc_vms_mb > highest_mem_mb and proc_vms_mb > 150.0:
                    highest_mem_mb = proc_vms_mb
                    culprit = proc.info
                    
            except (ps.NoSuchProcess, ps.AccessDenied):
                continue
                

        if culprit:
            logging.warning("culprit is found")
            logging.warning(f"the heaviest memory user is {culprit['name']} (PID {culprit['pid']} at {highest_mem_mb:.1f} MB)")

            try:
                target = ps.Process(culprit['pid'])
                target.terminate()
                
                # Trigger the Discord Alert with the new MB data!
                alert_msg = f"Terminated **{culprit['name']}** (PID: {culprit['pid']}). It was consuming **{highest_mem_mb:.1f} MB** of Virtual Memory."
                send_discord_alert(alert_msg)
                
                logging.warning(f"ACTION TAKEN: Terminated {culprit['name']} to free up RAM.")
            except ps.AccessDenied:
                logging.error(f"ACTION FAILED: Permission denied to kill {culprit['name']}.")
            except ps.NoSuchProcess:
                logging.info(f"ACTION CANCELLED: {culprit['name']} closed itself before termination.")

    else:
        logging.info(f"System Stable: RAM at {ram}%")


print("Daemon is actively monitoring the system.... Press Ctrl+C to stop")
try:
    while True:
        check_ram_vitals()
        time.sleep(5)
except KeyboardInterrupt:
    logging.info("Daemon stopped by user.")