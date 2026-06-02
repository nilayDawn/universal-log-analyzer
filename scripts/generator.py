#Generates random log lines and appends them to a local text file. This simulates a real application generating logs over time, which can be useful for testing log processing pipelines or monitoring tools.

import time
import random
import datetime
import os

# Create the data folder if it doesn't exist yet
os.makedirs("data", exist_ok=True)
LOG_FILE_PATH = "data/mock_app.log"

# Mock data pools
IP_LIST = ["192.168.1.10", "10.0.0.5", "172.16.0.2", "198.51.100.7","237.84.2.178","244.178.44.111","237.84.2.178"]
ENDPOINTS = ["/index.html", "/api/v1/login", "/api/v1/checkout","/api/v1/products", "/contact", "/about", "/api/v1/search"]

print(f"🚀 Starting log simulator... Writing to {LOG_FILE_PATH}")
print("Press Ctrl+C to stop the script at any time.")

try:
    while True:
        # Randomly choose one of three log types to create
        log_type = random.choice(["WEB", "AUTH", "DATABASE"])
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = ""
        
        if log_type == "WEB":
            ip = random.choice(IP_LIST)
            path = random.choice(ENDPOINTS)
            # Simulate mostly 200 (Success), with occasional 500 (Errors)
            status = random.choices([200, 500], weights=[90, 10])[0]
            log_line = f"{now} [WEB] IP={ip} PATH={path} STATUS={status}\n"
            
        elif log_type == "AUTH":
            user = random.choice(["admin", "root", "user1","user2", "guest"])
            status = random.choices(["SUCCESS", "FAILED"], weights=[80, 20])[0]
            log_line = f"{now} [AUTH] USER={user} LOGIN={status}\n"
            
        elif log_type == "DATABASE":
            level = random.choices(["INFO", "ERROR"], weights=[85, 15])[0]
            msg = "Connection successful" if level == "INFO" else "Connection timeout exceeded"
            log_line = f"{now} [DATABASE] LEVEL={level} MSG=\"{msg}\"\n"

        # Append the line directly to our local text log file
        with open(LOG_FILE_PATH, "a") as f:
            f.write(log_line)
            
        # Wait a random fraction of a second before creating the next log line
        time.sleep(random.uniform(0.5, 0.9))

except KeyboardInterrupt:
    print("\n🛑 Simulator stopped gracefully.")