@echo off
REM Silent installer for customer agent
REM Edit these values as needed
set CLOUD_API_URL=http://13.58.212.239:8000/report
set CUSTOMER=customer1

REM Set environment variables system-wide
setx CLOUD_API_URL "%CLOUD_API_URL%" /M
setx CUSTOMER "%CUSTOMER%" /M

REM Install Python if missing
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Python...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile '%TEMP%\python-installer.exe'"
    start /wait %TEMP%\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del %TEMP%\python-installer.exe
)

REM Install required Python packages
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn psutil requests

REM Install WireGuard if missing
if not exist "C:\Program Files\WireGuard\wireguard.exe" (
    echo Installing WireGuard...
    powershell -Command "Invoke-WebRequest -Uri 'https://download.wireguard.com/windows-client/wireguard-installer.exe' -OutFile '%TEMP%\wireguard-installer.exe'"
    start /wait %TEMP%\wireguard-installer.exe /install /quiet
    del %TEMP%\wireguard-installer.exe
)

REM Copy agent script to C:\WireGuard
if not exist "C:\WireGuard" mkdir "C:\WireGuard"
REM Ensure clean agent script file
if exist "C:\WireGuard\customer_agent_api.py" del "C:\WireGuard\customer_agent_api.py"
REM Write customer_agent_api.py directly from batch file

REM Generate WireGuard keys if missing
if not exist "C:\WireGuard\client_private.key" (
    powershell -Command "[Convert]::ToBase64String((New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes(32))" > "C:\WireGuard\client_private.key"
)
REM Use wireguard.exe to generate keys if available
if exist "C:\Program Files\WireGuard\wireguard.exe" (
    "C:\Program Files\WireGuard\wireguard.exe" /generateprivkey > "C:\WireGuard\client_private.key"
    set /p CLIENT_PRIVATE_KEY=<"C:\WireGuard\client_private.key"
    echo %CLIENT_PRIVATE_KEY% | "C:\Program Files\WireGuard\wireguard.exe" /generatepubkey > "C:\WireGuard\client_public.key"
    set /p CLIENT_PUBLIC_KEY=<"C:\WireGuard\client_public.key"
)

REM Set server public key and endpoint (edit these as needed)

REM Fetch server public key and endpoint from cloud API
for /f "delims=" %%i in ('python -c "import requests,os;resp=requests.get(os.environ.get('CLOUD_API_URL','http://13.58.212.239:8000/serverinfo'));j=resp.json();print(j.get('server_public_key',''));"') do set SERVER_PUBLIC_KEY=%%i
for /f "delims=" %%i in ('python -c "import requests,os;resp=requests.get(os.environ.get('CLOUD_API_URL','http://13.58.212.239:8000/serverinfo'));j=resp.json();print(j.get('server_endpoint',''));"') do set SERVER_ENDPOINT=%%i
set CLIENT_ADDRESS=10.0.0.2/32

REM Write WireGuard config file
echo [Interface]> "C:\WireGuard\wg0.conf"
echo PrivateKey = %CLIENT_PRIVATE_KEY%>> "C:\WireGuard\wg0.conf"
echo Address = %CLIENT_ADDRESS%>> "C:\WireGuard\wg0.conf"
echo DNS = 8.8.8.8>> "C:\WireGuard\wg0.conf"
echo.>> "C:\WireGuard\wg0.conf"
echo [Peer]>> "C:\WireGuard\wg0.conf"
echo PublicKey = %SERVER_PUBLIC_KEY%>> "C:\WireGuard\wg0.conf"
echo Endpoint = %SERVER_ENDPOINT%>> "C:\WireGuard\wg0.conf"
echo AllowedIPs = 0.0.0.0/0>> "C:\WireGuard\wg0.conf"
echo PersistentKeepalive = 25>> "C:\WireGuard\wg0.conf"
REM Write improved customer_agent_api.py with automated IP reporting
echo from fastapi import FastAPI, Request> "C:\WireGuard\customer_agent_api.py"
echo import os>> "C:\WireGuard\customer_agent_api.py"
echo import socket>> "C:\WireGuard\customer_agent_api.py"
echo import requests>> "C:\WireGuard\customer_agent_api.py"
echo def get_local_ips():>> "C:\WireGuard\customer_agent_api.py"
echo     ips = []>> "C:\WireGuard\customer_agent_api.py"
echo     hostname = socket.gethostname()>> "C:\WireGuard\customer_agent_api.py"
echo     try:>> "C:\WireGuard\customer_agent_api.py"
echo         for ip in socket.gethostbyname_ex(hostname)[2]:>> "C:\WireGuard\customer_agent_api.py"
echo             if not ip.startswith("127."):>> "C:\WireGuard\customer_agent_api.py"
echo                 ips.append(ip)>> "C:\WireGuard\customer_agent_api.py"
echo     except Exception:>> "C:\WireGuard\customer_agent_api.py"
echo         pass>> "C:\WireGuard\customer_agent_api.py"
echo     try:>> "C:\WireGuard\customer_agent_api.py"
echo         import psutil>> "C:\WireGuard\customer_agent_api.py"
echo         for iface, addrs in psutil.net_if_addrs().items():>> "C:\WireGuard\customer_agent_api.py"
echo             for addr in addrs:>> "C:\WireGuard\customer_agent_api.py"
echo                 if addr.family == socket.AF_INET and not addr.address.startswith("127."):>> "C:\WireGuard\customer_agent_api.py"
echo                     if addr.address not in ips:>> "C:\WireGuard\customer_agent_api.py"
echo                         ips.append(addr.address)>> "C:\WireGuard\customer_agent_api.py"
echo     except ImportError:>> "C:\WireGuard\customer_agent_api.py"
echo         pass>> "C:\WireGuard\customer_agent_api.py"
echo     return ips>> "C:\WireGuard\customer_agent_api.py"
echo.>> "C:\WireGuard\customer_agent_api.py"
echo def report_ips_to_cloud(cloud_api_url, customer, ips):>> "C:\WireGuard\customer_agent_api.py"
echo     try:>> "C:\WireGuard\customer_agent_api.py"
echo         resp = requests.post(cloud_api_url, json={"customer": customer, "ips": ips}, timeout=10)>> "C:\WireGuard\customer_agent_api.py"
echo         print(f"Reporting IPs to cloud: {ips} for customer: {customer}")>> "C:\WireGuard\customer_agent_api.py"
echo         print(f"Cloud API response: {resp.status_code} {resp.text}")>> "C:\WireGuard\customer_agent_api.py"
echo     except Exception as e:>> "C:\WireGuard\customer_agent_api.py"
echo         print(f"Failed to report IPs to cloud: {e}")>> "C:\WireGuard\customer_agent_api.py"
echo.>> "C:\WireGuard\customer_agent_api.py"
echo app = FastAPI()>> "C:\WireGuard\customer_agent_api.py"
echo.>> "C:\WireGuard\customer_agent_api.py"
echo WG_CONFIG_PATH = "C:/WireGuard/wg0.conf"  # Change path as needed for Windows>> "C:\WireGuard\customer_agent_api.py"
echo.>> "C:\WireGuard\customer_agent_api.py"
echo @app.post("/api/wgconfig")>> "C:\WireGuard\customer_agent_api.py"
echo async def receive_wg_config(request: Request):>> "C:\WireGuard\customer_agent_api.py"
echo     data = await request.json()>> "C:\WireGuard\customer_agent_api.py"
echo     config = data.get("config")>> "C:\WireGuard\customer_agent_api.py"
echo     customer = data.get("customer")>> "C:\WireGuard\customer_agent_api.py"
echo     if not config:>> "C:\WireGuard\customer_agent_api.py"
echo         return {"status": "error", "message": "No config provided"}>> "C:\WireGuard\customer_agent_api.py"
echo     with open(WG_CONFIG_PATH, "w") as f:>> "C:\WireGuard\customer_agent_api.py"
echo         f.write(config)>> "C:\WireGuard\customer_agent_api.py"
echo     os.system(f'"C:\\Program Files\\WireGuard\\wireguard.exe" /installtunnelservice "{WG_CONFIG_PATH}"')>> "C:\WireGuard\customer_agent_api.py"
echo     local_ips = get_local_ips()>> "C:\WireGuard\customer_agent_api.py"
echo     cloud_api_url = os.environ.get("CLOUD_API_URL")>> "C:\WireGuard\customer_agent_api.py"
echo     if cloud_api_url:>> "C:\WireGuard\customer_agent_api.py"
echo         try:>> "C:\WireGuard\customer_agent_api.py"
echo             report_ips_to_cloud(cloud_api_url, customer, local_ips)>> "C:\WireGuard\customer_agent_api.py"
echo         except Exception as e:>> "C:\WireGuard\customer_agent_api.py"
echo             return {"status": "partial", "message": f"Config applied, but failed to report IPs: {e}"}>> "C:\WireGuard\customer_agent_api.py"
echo     return {"status": "success", "message": f"Config applied for {customer}", "ips": local_ips}>> "C:\WireGuard\customer_agent_api.py"
echo.>> "C:\WireGuard\customer_agent_api.py"
echo if __name__ == "__main__":>> "C:\WireGuard\customer_agent_api.py"
echo     customer = os.environ.get("CUSTOMER", "customer1")>> "C:\WireGuard\customer_agent_api.py"
echo     cloud_api_url = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/report")>> "C:\WireGuard\customer_agent_api.py"
echo     local_ips = get_local_ips()>> "C:\WireGuard\customer_agent_api.py"
echo     print(f"[Agent Startup] Reporting IPs: {local_ips} for customer: {customer}")>> "C:\WireGuard\customer_agent_api.py"
echo     report_ips_to_cloud(cloud_api_url, customer, local_ips)>> "C:\WireGuard\customer_agent_api.py"
echo     import uvicorn>> "C:\WireGuard\customer_agent_api.py"
echo     uvicorn.run(app, host="0.0.0.0", port=5000)>> "C:\WireGuard\customer_agent_api.py"

REM Create startup task to run agent on boot
schtasks /Create /F /RU SYSTEM /SC ONSTART /TN "CustomerAgentAPI" /TR "python C:\WireGuard\customer_agent_api.py" /RL HIGHEST

echo Customer agent installed and set to run at startup. No manual steps required.

REM Write customer_agent_register.py directly from batch file
REM Write customer_agent_register.py directly from batch file
echo import requests> "C:\WireGuard\customer_agent_register.py"
echo import os>> "C:\WireGuard\customer_agent_register.py"
echo CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/register")>> "C:\WireGuard\customer_agent_register.py"
echo CUSTOMER = os.environ.get("CUSTOMER", "customer1")>> "C:\WireGuard\customer_agent_register.py"
echo payload = {"customer": CUSTOMER}>> "C:\WireGuard\customer_agent_register.py"
echo try:>> "C:\WireGuard\customer_agent_register.py"
echo     r = requests.post(CLOUD_API_URL, json=payload, timeout=10)>> "C:\WireGuard\customer_agent_register.py"
echo     print(f"Registration result: {r.text}")>> "C:\WireGuard\customer_agent_register.py"
echo except Exception as e:>> "C:\WireGuard\customer_agent_register.py"
echo     print(f"Failed to register agent: {e}")>> "C:\WireGuard\customer_agent_register.py"

REM Run agent registration script automatically
python C:\WireGuard\customer_agent_register.py

REM Write fetch_and_install_wg_config.py directly from batch file

echo import os> "C:\WireGuard\fetch_and_install_wg_config.py"
echo import requests>> "C:\WireGuard\fetch_and_install_wg_config.py"
echo CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/generate_config")>> "C:\WireGuard\fetch_and_install_wg_config.py"
echo CUSTOMER = os.environ.get("CUSTOMER", "customer1")>> "C:\WireGuard\fetch_and_install_wg_config.py"
echo WG_CONFIG_PATH = "C:/WireGuard/wg0.conf" >> "C:\WireGuard\fetch_and_install_wg_config.py"
echo resp = requests.post(CLOUD_API_URL, json={"customer": CUSTOMER})>> "C:\WireGuard\fetch_and_install_wg_config.py"
echo if resp.status_code == 200:>> "C:\WireGuard\fetch_and_install_wg_config.py"
echo     data = resp.json()>> "C:\WireGuard\fetch_and_install_wg_config.py"
echo     config_path = data.get("config_path")>> "C:\WireGuard\fetch_and_install_wg_config.py"
echo     print(f"Config generated at server: {config_path}")>> "C:\WireGuard\fetch_and_install_wg_config.py"
echo     print("Please implement config download endpoint for full automation.")>> "C:\WireGuard\fetch_and_install_wg_config.py"
echo     os.system("sudo wg-quick up wg0")>> "C:\WireGuard\fetch_and_install_wg_config.py"
echo else:>> "C:\WireGuard\fetch_and_install_wg_config.py"
echo     print("Failed to fetch config from cloud API.")>> "C:\WireGuard\fetch_and_install_wg_config.py"
REM Fetch WireGuard config from cloud and install
python C:\WireGuard\fetch_and_install_wg_config.py

REM Start agent in a new window for immediate testing
start "" python C:\WireGuard\customer_agent_api.py
