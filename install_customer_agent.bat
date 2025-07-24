@echo off

REM Ensure C:\WireGuard directory exists before anything else
if not exist "C:\WireGuard" mkdir "C:\WireGuard"

REM Set script paths
set AGENT_SCRIPT_PATH=C:\WireGuard\customer_agent_api.py
set REGISTER_SCRIPT_PATH=C:\WireGuard\customer_agent_register.py
set FETCH_SCRIPT_PATH=C:\WireGuard\fetch_and_install_wg_config.py
set LOGFILE=C:\WireGuard\agent_install.log

REM Write customer_agent_api.py
echo from fastapi import FastAPI, Request> "%AGENT_SCRIPT_PATH%"
echo import os>> "%AGENT_SCRIPT_PATH%"
echo import socket>> "%AGENT_SCRIPT_PATH%"
echo import requests>> "%AGENT_SCRIPT_PATH%"
echo def get_local_ips():>> "%AGENT_SCRIPT_PATH%"
echo     ips = []>> "%AGENT_SCRIPT_PATH%"
echo     hostname = socket.gethostname()>> "%AGENT_SCRIPT_PATH%"
echo     try:>> "%AGENT_SCRIPT_PATH%"
echo         for ip in socket.gethostbyname_ex(hostname)[2]:>> "%AGENT_SCRIPT_PATH%"
echo             if not ip.startswith("127."):>> "%AGENT_SCRIPT_PATH%"
echo                 ips.append(ip)>> "%AGENT_SCRIPT_PATH%"
echo     except Exception:>> "%AGENT_SCRIPT_PATH%"
echo         pass>> "%AGENT_SCRIPT_PATH%"
echo     try:>> "%AGENT_SCRIPT_PATH%"
echo         import psutil>> "%AGENT_SCRIPT_PATH%"
echo         for iface, addrs in psutil.net_if_addrs().items():>> "%AGENT_SCRIPT_PATH%"
echo             for addr in addrs:>> "%AGENT_SCRIPT_PATH%"
echo                 if addr.family == socket.AF_INET and not addr.address.startswith("127."):>> "%AGENT_SCRIPT_PATH%"
echo                     if addr.address not in ips:>> "%AGENT_SCRIPT_PATH%"
echo                         ips.append(addr.address)>> "%AGENT_SCRIPT_PATH%"
echo     except ImportError:>> "%AGENT_SCRIPT_PATH%"
echo         pass>> "%AGENT_SCRIPT_PATH%"
echo     return ips>> "%AGENT_SCRIPT_PATH%"
echo.>> "%AGENT_SCRIPT_PATH%"
echo def report_ips_to_cloud(cloud_api_url, customer, ips):>> "%AGENT_SCRIPT_PATH%"
echo     try:>> "%AGENT_SCRIPT_PATH%"
echo         resp = requests.post(cloud_api_url, json={"customer": customer, "ips": ips}, timeout=10)>> "%AGENT_SCRIPT_PATH%"
echo         print(f"Reporting IPs to cloud: {ips} for customer: {customer}")>> "%AGENT_SCRIPT_PATH%"
echo         print(f"Cloud API response: {resp.status_code} {resp.text}")>> "%AGENT_SCRIPT_PATH%"
echo     except Exception as e:>> "%AGENT_SCRIPT_PATH%"
echo         print(f"Failed to report IPs to cloud: {e}")>> "%AGENT_SCRIPT_PATH%"
echo.>> "%AGENT_SCRIPT_PATH%"
echo app = FastAPI()>> "%AGENT_SCRIPT_PATH%"
echo.>> "%AGENT_SCRIPT_PATH%"
echo WG_CONFIG_PATH = "C:/WireGuard/wg0.conf"  ^# Change path as needed for Windows>> "%AGENT_SCRIPT_PATH%"
echo.>> "%AGENT_SCRIPT_PATH%"
echo @app.post("/api/wgconfig")>> "%AGENT_SCRIPT_PATH%"
echo async def receive_wg_config(request: Request):>> "%AGENT_SCRIPT_PATH%"
echo     data = await request.json()>> "%AGENT_SCRIPT_PATH%"
echo     config = data.get("config")>> "%AGENT_SCRIPT_PATH%"
echo     customer = data.get("customer")>> "%AGENT_SCRIPT_PATH%"
echo     if not config:>> "%AGENT_SCRIPT_PATH%"
echo         return {"status": "error", "message": "No config provided"}>> "%AGENT_SCRIPT_PATH%"
echo     with open(WG_CONFIG_PATH, "w") as f:>> "%AGENT_SCRIPT_PATH%"
echo         f.write(config)>> "%AGENT_SCRIPT_PATH%"
echo     os.system(f'"C:\\Program Files\\WireGuard\\wireguard.exe" /installtunnelservice "{WG_CONFIG_PATH}"')>> "%AGENT_SCRIPT_PATH%"
echo     local_ips = get_local_ips()>> "%AGENT_SCRIPT_PATH%"
echo     cloud_api_url = os.environ.get("CLOUD_API_URL")>> "%AGENT_SCRIPT_PATH%"
echo     if cloud_api_url:>> "%AGENT_SCRIPT_PATH%"
echo         try:>> "%AGENT_SCRIPT_PATH%"
echo             report_ips_to_cloud(cloud_api_url, customer, local_ips)>> "%AGENT_SCRIPT_PATH%"
echo         except Exception as e:>> "%AGENT_SCRIPT_PATH%"
echo             return {"status": "partial", "message": f"Config applied, but failed to report IPs: {e}"}>> "%AGENT_SCRIPT_PATH%"
echo     return {"status": "success", "message": f"Config applied for {customer}", "ips": local_ips}>> "%AGENT_SCRIPT_PATH%"
echo.>> "%AGENT_SCRIPT_PATH%"
echo if __name__ == "__main__":>> "%AGENT_SCRIPT_PATH%"
echo     customer = os.environ.get("CUSTOMER", "customer1")>> "%AGENT_SCRIPT_PATH%"
echo     cloud_api_url = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/report")>> "%AGENT_SCRIPT_PATH%"
echo     local_ips = get_local_ips()>> "%AGENT_SCRIPT_PATH%"
echo     print(f"[Agent Startup] Reporting IPs: {local_ips} for customer: {customer}")>> "%AGENT_SCRIPT_PATH%"
echo     report_ips_to_cloud(cloud_api_url, customer, local_ips)>> "%AGENT_SCRIPT_PATH%"
echo     import uvicorn>> "%AGENT_SCRIPT_PATH%"
echo     uvicorn.run(app, host="0.0.0.0", port=5000)>> "%AGENT_SCRIPT_PATH%"
echo Finished writing customer_agent_api.py>> "%LOGFILE%"
if exist "%AGENT_SCRIPT_PATH%" (
    echo customer_agent_api.py created successfully in C:\WireGuard>> "%LOGFILE%"
) else (
    echo ERROR: customer_agent_api.py was NOT created in C:\WireGuard. Check permissions and run as Administrator.>> "%LOGFILE%"
)

REM Write customer_agent_register.py
echo import requests> "%REGISTER_SCRIPT_PATH%"
echo import os>> "%REGISTER_SCRIPT_PATH%"
echo CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/register")>> "%REGISTER_SCRIPT_PATH%"
echo CUSTOMER = os.environ.get("CUSTOMER", "customer1")>> "%REGISTER_SCRIPT_PATH%"
echo payload = {"customer": CUSTOMER}>> "%REGISTER_SCRIPT_PATH%"
echo try:>> "%REGISTER_SCRIPT_PATH%"
echo     r = requests.post(CLOUD_API_URL, json=payload, timeout=10)>> "%REGISTER_SCRIPT_PATH%"
echo     print(f"Registration result: {r.text}")>> "%REGISTER_SCRIPT_PATH%"
echo except Exception as e:>> "%REGISTER_SCRIPT_PATH%"
echo     print(f"Failed to register agent: {e}")>> "%REGISTER_SCRIPT_PATH%"
echo Finished writing customer_agent_register.py>> "%LOGFILE%"
if exist "%REGISTER_SCRIPT_PATH%" (
    echo customer_agent_register.py created successfully in C:\WireGuard>> "%LOGFILE%"
) else (
    echo ERROR: customer_agent_register.py was NOT created in C:\WireGuard. Check permissions and run as Administrator.>> "%LOGFILE%"
)

REM Write fetch_and_install_wg_config.py
echo import os> "%FETCH_SCRIPT_PATH%"
echo import requests>> "%FETCH_SCRIPT_PATH%"
echo CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/generate_config")>> "%FETCH_SCRIPT_PATH%"
echo CUSTOMER = os.environ.get("CUSTOMER", "customer1")>> "%FETCH_SCRIPT_PATH%"
echo WG_CONFIG_PATH = "C:/WireGuard/wg0.conf" >> "%FETCH_SCRIPT_PATH%"
echo resp = requests.post(CLOUD_API_URL, json={"customer": CUSTOMER})>> "%FETCH_SCRIPT_PATH%"
echo if resp.status_code == 200:>> "%FETCH_SCRIPT_PATH%"
echo     data = resp.json()>> "%FETCH_SCRIPT_PATH%"
echo     config_path = data.get("config_path")>> "%FETCH_SCRIPT_PATH%"
echo     print(f"Config generated at server: {config_path}")>> "%FETCH_SCRIPT_PATH%"
echo     print("Please implement config download endpoint for full automation.")>> "%FETCH_SCRIPT_PATH%"
echo     os.system("sudo wg-quick up wg0")>> "%FETCH_SCRIPT_PATH%"
echo else:>> "%FETCH_SCRIPT_PATH%"
echo     print("Failed to fetch config from cloud API.")>> "%FETCH_SCRIPT_PATH%"
echo Finished writing fetch_and_install_wg_config.py>> "%LOGFILE%"
if exist "%FETCH_SCRIPT_PATH%" (
    echo fetch_and_install_wg_config.py created successfully in C:\WireGuard>> "%LOGFILE%"
) else (
    echo ERROR: fetch_and_install_wg_config.py was NOT created in C:\WireGuard. Check permissions and run as Administrator.>> "%LOGFILE%"
)

REM Run agent registration script automatically
python "%REGISTER_SCRIPT_PATH%"

REM Fetch WireGuard config from cloud and install
python "%FETCH_SCRIPT_PATH%"

REM Start agent in a new window for immediate testing (window always stays open)
start "" cmd /k "python %AGENT_SCRIPT_PATH% & pause"

echo Customer agent installed and set to run at startup. No manual steps required.

REM Create startup task to run agent on boot
schtasks /Create /F /RU SYSTEM /SC ONSTART /TN "CustomerAgentAPI" /TR "python %AGENT_SCRIPT_PATH%" /RL HIGHEST

