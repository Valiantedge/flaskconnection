@echo off
setlocal enabledelayedexpansion

REM -----------------------------
REM CONFIGURATION
REM -----------------------------
set "WG_DIR=C:\WireGuard"
set "AGENT_SCRIPT_PATH=%WG_DIR%\customer_agent_api.py"
set "REGISTER_SCRIPT_PATH=%WG_DIR%\customer_agent_register.py"
set "FETCH_SCRIPT_PATH=%WG_DIR%\fetch_and_install_wg_config.py"
set "LOGFILE=%WG_DIR%\install.log"

REM -----------------------------
REM Create directory
REM -----------------------------
if not exist "%WG_DIR%" mkdir "%WG_DIR%"
echo [%DATE% %TIME%] Starting installation... > "%LOGFILE%"

REM -----------------------------
REM Check Python installation
REM -----------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python first. >> "%LOGFILE%"
    echo ERROR: Python is required. Install it and re-run this script.
    pause
    exit /b 1
)

REM -----------------------------
REM Write customer_agent_api.py
REM -----------------------------
(
echo from fastapi import FastAPI, Request
echo import os, socket, requests, uvicorn
echo
echo def get_local_ips():
echo     ips = []
echo     try:
echo         hostname = socket.gethostname()
echo         for ip in socket.gethostbyname_ex(hostname)[2]:
echo             if not ip.startswith("127."):
echo                 ips.append(ip)
echo     except: pass
echo     return ips
echo
echo def report_ips_to_cloud(url, customer, ips):
echo     try:
echo         r = requests.post(url, json={"customer":customer,"ips":ips}, timeout=10)
echo         print(f"Reported IPs: {ips} for {customer}. Response: {r.status_code}")
echo     except Exception as e:
echo         print(f"Error reporting IPs: {e}")
echo
echo app = FastAPI()
echo WG_CONFIG_PATH = "C:/WireGuard/wg0.conf"
echo
echo @app.post("/api/wgconfig")
echo async def receive_wg_config(request: Request):
echo     data = await request.json()
echo     config = data.get("config")
echo     customer = data.get("customer")
echo     if not config:
echo         return {"status":"error","message":"No config provided"}
echo     with open(WG_CONFIG_PATH,"w") as f: f.write(config)
echo     os.system(f'"C:\\Program Files\\WireGuard\\wireguard.exe" /installtunnelservice "{WG_CONFIG_PATH}"')
echo     local_ips = get_local_ips()
echo     url = os.environ.get("CLOUD_API_URL")
echo     if url: report_ips_to_cloud(url, customer, local_ips)
echo     return {"status":"success","ips":local_ips}
echo
echo if __name__ == "__main__":
echo     customer = os.environ.get("CUSTOMER","customer1")
echo     url = os.environ.get("CLOUD_API_URL","http://13.58.212.239:8000/report")
echo     ips = get_local_ips()
echo     report_ips_to_cloud(url, customer, ips)
echo     uvicorn.run(app, host="0.0.0.0", port=5000)
) > "%AGENT_SCRIPT_PATH%"
echo [INFO] Created %AGENT_SCRIPT_PATH% >> "%LOGFILE%"

REM -----------------------------
REM Write customer_agent_register.py
REM -----------------------------
(
echo import requests, os
echo url = os.environ.get("CLOUD_API_URL","http://13.58.212.239:8000/register")
echo customer = os.environ.get("CUSTOMER","customer1")
echo try:
echo     r = requests.post(url, json={"customer":customer}, timeout=10)
echo     print(f"Registration result: {r.text}")
echo except Exception as e:
echo     print(f"Failed to register agent: {e}")
) > "%REGISTER_SCRIPT_PATH%"
echo [INFO] Created %REGISTER_SCRIPT_PATH% >> "%LOGFILE%"

REM -----------------------------
REM Write fetch_and_install_wg_config.py
REM -----------------------------
(
echo import os, requests
echo url = os.environ.get("CLOUD_API_URL","http://13.58.212.239:8000/generate_config")
echo customer = os.environ.get("CUSTOMER","customer1")
echo r = requests.post(url,json={"customer":customer})
echo if r.status_code==200:
echo     data = r.json()
echo     print(f"Config path on server: {data.get('config_path')}")
echo     print("Download and apply manually for now.")
echo else:
echo     print("Failed to fetch config.")
) > "%FETCH_SCRIPT_PATH%"
echo [INFO] Created %FETCH_SCRIPT_PATH% >> "%LOGFILE%"

REM -----------------------------
REM Create scheduled task
REM -----------------------------
schtasks /Create /F /RU SYSTEM /SC ONSTART /TN "CustomerAgentAPI" /TR "python %AGENT_SCRIPT_PATH%" /RL HIGHEST
echo [INFO] Scheduled task created for agent. >> "%LOGFILE%"

REM -----------------------------
REM Run initial registration
REM -----------------------------
python "%REGISTER_SCRIPT_PATH%"

REM -----------------------------
REM Start agent now for testing
REM -----------------------------
start "" cmd /k "python %AGENT_SCRIPT_PATH% & pause"
echo [INFO] Installation complete. Press any key to exit. >> "%LOGFILE%"
pause
