@echo off
REM Ensure C:\WireGuard directory exists before anything else
if not exist "C:\WireGuard" mkdir "C:\WireGuard"
set LOGFILE=C:\WireGuard\agent_install.log
echo Batch started at %DATE% %TIME% > "%LOGFILE%"
REM Detect if running in PowerShell (not cmd.exe)
if defined PSModulePath (
    echo WARNING: This batch file should be run with cmd.exe, not PowerShell. Some echo commands may fail in PowerShell.>> "%LOGFILE%"
)
echo Starting customer agent installer...>> "%LOGFILE%"
REM Edit these values as needed
set CLOUD_API_URL=http://13.58.212.239:8000/report
set CUSTOMER=customer1

REM Set environment variables system-wide
setx CLOUD_API_URL "%CLOUD_API_URL%" /M >> "%LOGFILE%"
setx CUSTOMER "%CUSTOMER%" /M >> "%LOGFILE%"

echo Checking for Python...>> "%LOGFILE%"
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Python...>> "%LOGFILE%"
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile '%TEMP%\python-installer.exe'"
    start /wait %TEMP%\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del %TEMP%\python-installer.exe
)

echo Installing required Python packages...>> "%LOGFILE%"
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn psutil requests

echo Checking for WireGuard...>> "%LOGFILE%"
if not exist "C:\Program Files\WireGuard\wireguard.exe" (
echo Installing WireGuard...>> "%LOGFILE%"
powershell -Command "Invoke-WebRequest -Uri 'https://download.wireguard.com/windows-client/wireguard-installer.exe' -OutFile '%TEMP%\wireguard-installer.exe'"
start /wait %TEMP%\wireguard-installer.exe /install /quiet
del %TEMP%\wireguard-installer.exe
)

REM Ensure clean agent script file
if exist "C:\WireGuard\customer_agent_api.py" del "C:\WireGuard\customer_agent_api.py"

REM Write all Python agent scripts after directory creation
set AGENT_SCRIPT_PATH=C:\WireGuard\customer_agent_api.py
set REGISTER_SCRIPT_PATH=C:\WireGuard\customer_agent_register.py
set FETCH_SCRIPT_PATH=C:\WireGuard\fetch_and_install_wg_config.py

REM Write customer_agent_api.py
echo Writing customer_agent_api.py...>> "%LOGFILE%"
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
echo WG_CONFIG_PATH = "C:/WireGuard/wg0.conf"  # Change path as needed for Windows>> "%AGENT_SCRIPT_PATH%"
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
echo     os.system(f'"C:\Program Files\WireGuard\wireguard.exe" /installtunnelservice "{WG_CONFIG_PATH}"')>> "%AGENT_SCRIPT_PATH%"
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
echo Writing customer_agent_register.py...>> "%LOGFILE%"
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
echo Writing fetch_and_install_wg_config.py...>> "%LOGFILE%"
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

echo Generating WireGuard keys if missing...>> "%LOGFILE%"
if not exist "C:\WireGuard\client_private.key" (
    powershell -Command "[Convert]::ToBase64String((New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes(32))" > "C:\WireGuard\client_private.key"
)
echo Generating WireGuard keys with wireguard.exe if available...>> "%LOGFILE%"
if exist "C:\Program Files\WireGuard\wireguard.exe" (
    "C:\Program Files\WireGuard\wireguard.exe" /generateprivkey > "C:\WireGuard\client_private.key"
    set /p CLIENT_PRIVATE_KEY=<"C:\WireGuard\client_private.key"
    echo %CLIENT_PRIVATE_KEY% | "C:\Program Files\WireGuard\wireguard.exe" /generatepubkey > "C:\WireGuard\client_public.key"
    set /p CLIENT_PUBLIC_KEY=<"C:\WireGuard\client_public.key"
)

REM Set server public key and endpoint (edit these as needed)

echo Fetching server public key and endpoint from cloud API...>> "%LOGFILE%"
for /f "delims=" %%i in ('python -c "import requests,os;resp=requests.get(os.environ.get('CLOUD_API_URL','http://13.58.212.239:8000/serverinfo'));j=resp.json();print(j.get('server_public_key',''));"') do set SERVER_PUBLIC_KEY=%%i
for /f "delims=" %%i in ('python -c "import requests,os;resp=requests.get(os.environ.get('CLOUD_API_URL','http://13.58.212.239:8000/serverinfo'));j=resp.json();print(j.get('server_endpoint',''));"') do set SERVER_ENDPOINT=%%i
set CLIENT_ADDRESS=10.0.0.2/32

echo Writing WireGuard config file...>> "%LOGFILE%"
echo [Interface]> "C:\WireGuard\wg0.conf"
if not "%CLIENT_PRIVATE_KEY%"=="" (
    echo PrivateKey = %CLIENT_PRIVATE_KEY%>> "C:\WireGuard\wg0.conf"
) else (
    echo ERROR: PrivateKey is missing!>> "C:\WireGuard\wg0.conf"
)
echo Address = %CLIENT_ADDRESS%>> "C:\WireGuard\wg0.conf"
echo DNS = 8.8.8.8>> "C:\WireGuard\wg0.conf"
echo.>> "C:\WireGuard\wg0.conf"
echo [Peer]>> "C:\WireGuard\wg0.conf"
if not "%SERVER_PUBLIC_KEY%"=="" (
    echo PublicKey = %SERVER_PUBLIC_KEY%>> "C:\WireGuard\wg0.conf"
) else (
    echo ERROR: PublicKey is missing!>> "C:\WireGuard\wg0.conf"
)
if not "%SERVER_ENDPOINT%"=="" (
    echo Endpoint = %SERVER_ENDPOINT%>> "C:\WireGuard\wg0.conf"
) else (
    echo ERROR: Endpoint is missing!>> "C:\WireGuard\wg0.conf"
)
echo AllowedIPs = 0.0.0.0/0>> "C:\WireGuard\wg0.conf"
echo PersistentKeepalive = 25>> "C:\WireGuard\wg0.conf"
echo Activating WireGuard tunnel...>> "%LOGFILE%"
"C:\Program Files\WireGuard\wireguard.exe" /installtunnelservice "C:\WireGuard\wg0.conf"


echo Writing Python agent scripts...>> "%LOGFILE%"
if not exist "C:\WireGuard" mkdir "C:\WireGuard"

REM Write improved customer_agent_api.py with automated IP reporting using absolute path
set AGENT_SCRIPT_PATH=C:\WireGuard\customer_agent_api.py
echo Writing customer_agent_api.py...>> "%LOGFILE%"
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
echo Finished writing customer_agent_api.py
if exist "%AGENT_SCRIPT_PATH%" (
    echo customer_agent_api.py created successfully in C:\WireGuard>> "%LOGFILE%"
) else (
    echo ERROR: customer_agent_api.py was NOT created in C:\WireGuard. Check permissions and run as Administrator.>> "%LOGFILE%"
)

REM Write customer_agent_register.py directly from batch file
set REGISTER_SCRIPT_PATH=C:\WireGuard\customer_agent_register.py
echo Writing customer_agent_register.py...>> "%LOGFILE%"
echo import requests> "%REGISTER_SCRIPT_PATH%"
echo import os>> "%REGISTER_SCRIPT_PATH%"
echo CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/register")>> "%REGISTER_SCRIPT_PATH%"
echo CUSTOMER = os.environ.get("CUSTOMER", "customer1")>> "%REGISTER_SCRIPT_PATH%"
echo payload = {"customer": CUSTOMER}> "%%REGISTER_SCRIPT_PATH%%"
echo try:>> "%REGISTER_SCRIPT_PATH%"
echo     r = requests.post(CLOUD_API_URL, json=payload, timeout=10)>> "%REGISTER_SCRIPT_PATH%"
echo     print(f"Registration result: {r.text}")>> "%%REGISTER_SCRIPT_PATH%%"
echo except Exception as e:>> "%REGISTER_SCRIPT_PATH%"
echo     print(f"Failed to register agent: {e}")>> "%%REGISTER_SCRIPT_PATH%%"
echo Finished writing customer_agent_register.py
if exist "%REGISTER_SCRIPT_PATH%" (
    echo customer_agent_register.py created successfully in C:\WireGuard>> "%LOGFILE%"
) else (
    echo ERROR: customer_agent_register.py was NOT created in C:\WireGuard. Check permissions and run as Administrator.>> "%LOGFILE%"
)

REM Write fetch_and_install_wg_config.py directly from batch file
set FETCH_SCRIPT_PATH=C:\WireGuard\fetch_and_install_wg_config.py
echo Writing fetch_and_install_wg_config.py...>> "%LOGFILE%"
echo import os> "%FETCH_SCRIPT_PATH%"
echo import requests>> "%FETCH_SCRIPT_PATH%"
echo CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/generate_config")>> "%FETCH_SCRIPT_PATH%"
echo CUSTOMER = os.environ.get("CUSTOMER", "customer1")>> "%FETCH_SCRIPT_PATH%"
echo WG_CONFIG_PATH = "C:/WireGuard/wg0.conf" >> "%FETCH_SCRIPT_PATH%"
echo resp = requests.post(CLOUD_API_URL, json={"customer": CUSTOMER})>> "%%FETCH_SCRIPT_PATH%%"
echo if resp.status_code == 200:>> "%FETCH_SCRIPT_PATH%"
echo     data = resp.json()>> "%FETCH_SCRIPT_PATH%"
echo     config_path = data.get("config_path")>> "%FETCH_SCRIPT_PATH%"
echo     print(f"Config generated at server: {config_path}")>> "%%FETCH_SCRIPT_PATH%%"
echo     print("Please implement config download endpoint for full automation.")>> "%%FETCH_SCRIPT_PATH%%"
echo     os.system("sudo wg-quick up wg0")>> "%%FETCH_SCRIPT_PATH%%"
echo else:>> "%%FETCH_SCRIPT_PATH%%"
echo     print("Failed to fetch config from cloud API.")>> "%%FETCH_SCRIPT_PATH%%"
echo Finished writing fetch_and_install_wg_config.py
if exist "%%FETCH_SCRIPT_PATH%%" (
    echo fetch_and_install_wg_config.py created successfully in C:\WireGuard>> "%%LOGFILE%%"
) else (
    echo ERROR: fetch_and_install_wg_config.py was NOT created in C:\WireGuard. Check permissions and run as Administrator.>> "%%LOGFILE%%"
)

echo Listing all .py files in C:\WireGuard...>> "%LOGFILE%"
dir /b C:\WireGuard\*.py >> "%LOGFILE%"

cd /d %~dp0
echo Installer finished at %DATE% %TIME%. Press any key to exit.>> "%LOGFILE%"
pause

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

REM Start agent in a new window for immediate testing (window always stays open)
start "" cmd /k "python C:\WireGuard\customer_agent_api.py && pause"

