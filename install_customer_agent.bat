@echo off


REM Ensure C:\WireGuard directory exists before anything else
if not exist "C:\WireGuard" mkdir "C:\WireGuard"

REM Create log file immediately for diagnostics
set LOGFILE=C:\WireGuard\agent_install.log
echo --- Agent install started at %DATE% %TIME% --- > "%LOGFILE%"

REM Silent install WireGuard if not present
if not exist "C:\Program Files\WireGuard\wireguard.exe" (
    echo Installing WireGuard...
    msiexec /i "WireGuardInstaller.msi" /quiet /qn /norestart
)

REM Generate WireGuard keys if not present
echo --- Directory listing before keygen --- >> "%LOGFILE%"
dir "C:\WireGuard" >> "%LOGFILE%"
set WG_PRIV_KEY=C:\WireGuard\wg_private.key
set WG_PUB_KEY=C:\WireGuard\wg_public.key
set WG_CONFIG=C:\WireGuard\wg0.conf
set WG_EXE=C:\Program Files\WireGuard\wg.exe
REM Use wg.exe from C:\Program Files\WireGuard
REM Check for wg.exe before keygen
if exist "%WG_EXE%" (
    if not exist "%WG_PRIV_KEY%" (
        echo Generating WireGuard private key...>> "%LOGFILE%"
        cd /d "C:\Program Files\WireGuard"
        "%WG_EXE%" genkey > "%WG_PRIV_KEY%.tmp" 2>> "%LOGFILE%"
        REM Convert to Windows line endings to ensure set /p works
        powershell -Command "[IO.File]::WriteAllLines('%WG_PRIV_KEY%', (Get-Content -Raw '%WG_PRIV_KEY%.tmp').Replace('`n','`r`n'))"
        del "%WG_PRIV_KEY%.tmp"
        REM Log the actual output of wg.exe genkey for diagnostics
        echo --- wg.exe genkey output --- >> "%LOGFILE%"
        type "%WG_PRIV_KEY%" >> "%LOGFILE%"
        echo --- end wg.exe genkey output --- >> "%LOGFILE%"
        if not exist "%WG_PRIV_KEY%" (
            echo ERROR: Private key file was not created.>> "%LOGFILE%"
            echo Check permissions for C:\WireGuard and run as Administrator.>> "%LOGFILE%"
        ) else (
            cd /d C:\WireGuard
            echo Generating WireGuard public key...>> "%LOGFILE%"
            "C:\Program Files\WireGuard\wg.exe" pubkey < wg_private.key > wg_public.key 2>> "%LOGFILE%"
            if exist "wg_public.key" (
                echo --- wg.exe pubkey output --- >> "%LOGFILE%"
                type wg_public.key >> "%LOGFILE%"
                echo --- end wg.exe pubkey output --- >> "%LOGFILE%"
            ) else (
                echo ERROR: Public key file was not created.>> "%LOGFILE%"
            )
        )
    )
    if exist "%WG_PRIV_KEY%" (
        set /p PRIVKEY=<"%WG_PRIV_KEY%"
        if not "%PRIVKEY%"=="" if not "%PRIVKEY:~43,1%"=="" (
            echo Generating WireGuard public key...>> "%LOGFILE%"
            "%WG_EXE%" pubkey < "%WG_PRIV_KEY%" > "%WG_PUB_KEY%" 2>> "%LOGFILE%"
        ) else (
            echo ERROR: Private key is not the correct length. Public key not generated.>> "%LOGFILE%"
        )
    )
    if exist "%WG_PRIV_KEY%" if exist "%WG_PUB_KEY%" (
        cd /d C:\WireGuard
        set /p PRIVKEY=<wg_private.key
        set /p PUBKEY=<wg_public.key
        echo WireGuard keys generated successfully.>> "%LOGFILE%"
        echo.>> "%LOGFILE%"
        echo === Manual Cloud Registration Required ===>> "%LOGFILE%"
        echo To register your public key with the server, run the following command in PowerShell or CMD:>> "%LOGFILE%"
        echo curl -X POST -H "Content-Type: application/json" -d "{\"customer\": \"customer1\", \"peer_public_key\": \"%PRIVKEY%\"}" http://13.58.212.239:8000/add_peer>> "%LOGFILE%"
        echo.>> "%LOGFILE%"
        echo To fetch your WireGuard config, run:>> "%LOGFILE%"
        echo curl -X POST -H "Content-Type: application/json" -d "{\"customer\": \"customer1\"}" http://13.58.212.239:8000/generate_config -o C:\WireGuard\wg0.conf>> "%LOGFILE%"
        echo.>> "%LOGFILE%"
        echo After downloading wg0.conf, you can start the tunnel with:>> "%LOGFILE%"
        echo "C:\Program Files\WireGuard\wireguard.exe" /installtunnelservice C:\WireGuard\wg0.conf>> "%LOGFILE%"
        echo =========================================>> "%LOGFILE%"
        echo.>> "%LOGFILE%"
        echo === Manual Cloud Registration Required ===
        echo To register your public key with the server, run the following command in PowerShell or CMD:
        echo curl -X POST -H "Content-Type: application/json" -d "{\"customer\": \"customer1\", \"peer_public_key\": \"%PRIVKEY%\"}" http://13.58.212.239:8000/add_peer
        echo.
        echo To fetch your WireGuard config, run:
        echo curl -X POST -H "Content-Type: application/json" -d "{\"customer\": \"customer1\"}" http://13.58.212.239:8000/generate_config -o C:\WireGuard\wg0.conf
        echo.
        echo After downloading wg0.conf, you can start the tunnel with:
        echo "C:\Program Files\WireGuard\wireguard.exe" /installtunnelservice C:\WireGuard\wg0.conf
        echo =========================================
    ) else (
        echo ERROR: WireGuard keys not generated.>> "%LOGFILE%"
    )
) else (
    echo ERROR: wg.exe not found in C:\WireGuard. Key generation skipped.>> "%LOGFILE%"
)

REM Set script paths
set AGENT_SCRIPT_PATH=C:\WireGuard\customer_agent_api.py
set REGISTER_SCRIPT_PATH=C:\WireGuard\customer_agent_register.py
set FETCH_SCRIPT_PATH=C:\WireGuard\fetch_and_install_wg_config.py
set LOGFILE=C:\WireGuard\agent_install.log
set ADD_PEER_SCRIPT_PATH=C:\WireGuard\add_peer.py

REM Write customer_agent_api.py
call :write_agent_script > "%AGENT_SCRIPT_PATH%"
echo Finished writing customer_agent_api.py>> "%LOGFILE%"
echo Finished writing customer_agent_api.py>> "%LOGFILE%"
if exist "%AGENT_SCRIPT_PATH%" (
    echo customer_agent_api.py created successfully in C:\WireGuard>> "%LOGFILE%"
) else (
    echo ERROR: customer_agent_api.py was NOT created in C:\WireGuard. Check permissions and run as Administrator.>> "%LOGFILE%"
)

REM Write customer_agent_register.py
call :write_register_script > "%REGISTER_SCRIPT_PATH%"
echo Finished writing customer_agent_register.py>> "%LOGFILE%"
echo Finished writing customer_agent_register.py>> "%LOGFILE%"
if exist "%REGISTER_SCRIPT_PATH%" (
    echo customer_agent_register.py created successfully in C:\WireGuard>> "%LOGFILE%"
) else (
    echo ERROR: customer_agent_register.py was NOT created in C:\WireGuard. Check permissions and run as Administrator.>> "%LOGFILE%"
)


REM Write fetch_and_install_wg_config.py
call :write_fetch_script > "%FETCH_SCRIPT_PATH%"
echo Finished writing fetch_and_install_wg_config.py>> "%LOGFILE%"
if exist "%FETCH_SCRIPT_PATH%" (
    echo fetch_and_install_wg_config.py created successfully in C:\WireGuard>> "%LOGFILE%"
) else (
    echo ERROR: fetch_and_install_wg_config.py was NOT created in C:\WireGuard. Check permissions and run as Administrator.>> "%LOGFILE%"
)



REM Automated: Fetch WireGuard config from cloud and install
python "%FETCH_SCRIPT_PATH%"


REM Run agent registration script automatically
python "%REGISTER_SCRIPT_PATH%"


REM Fetch WireGuard config from cloud and install
python "%FETCH_SCRIPT_PATH%"

REM Start WireGuard tunnel in Windows
if exist "%WG_CONFIG%" if exist "C:\Program Files\WireGuard\wireguard.exe" (
    "C:\Program Files\WireGuard\wireguard.exe" /installtunnelservice "%WG_CONFIG%"
    echo WireGuard tunnel started using wireguard.exe>> "%LOGFILE%"
) else (
    echo ERROR: WireGuard config or executable missing.>> "%LOGFILE%"
)

REM Start agent in a new window for immediate testing (window always stays open)
start "" cmd /k "python %AGENT_SCRIPT_PATH% & pause"

echo Customer agent installed and set to run at startup. No manual steps required.

pause
goto :eof

:write_agent_script
echo from fastapi import FastAPI, Request
echo import os
echo import socket
echo import requests
echo def get_local_ips():
echo     ips = []
echo     hostname = socket.gethostname()
echo     try:
echo         for ip in socket.gethostbyname_ex(hostname)[2]:
echo             if not ip.startswith("127."):
echo                 ips.append(ip)
echo     except Exception:
echo         pass
echo     try:
echo         import psutil
echo         for iface, addrs in psutil.net_if_addrs().items():
echo             for addr in addrs:
echo                 if addr.family == socket.AF_INET and not addr.address.startswith("127."):
echo                     if addr.address not in ips:
echo                         ips.append(addr.address)
echo     except ImportError:
echo         pass
echo     return ips
echo.
echo def report_ips_to_cloud(cloud_api_url, customer, ips):
echo     try:
echo         resp = requests.post(cloud_api_url, json={"customer": customer, "ips": ips}, timeout=10)
echo         print(f"Reporting IPs to cloud: {ips} for customer: {customer}")
echo         print(f"Cloud API response: {resp.status_code} {resp.text}")
echo     except Exception as e:
echo         print(f"Failed to report IPs to cloud: {e}")
echo.
echo app = FastAPI()
echo.
echo WG_CONFIG_PATH = "C:/WireGuard/wg0.conf"  # Change path as needed for Windows
echo.
echo @app.post("/api/wgconfig")
echo async def receive_wg_config(request: Request):
echo     data = await request.json()
echo     config = data.get("config")
echo     customer = data.get("customer")
echo     if not config:
echo         return {"status": "error", "message": "No config provided"}
echo     with open(WG_CONFIG_PATH, "w") as f:
echo         f.write(config)
echo     os.system(f'"C:\\Program Files\\WireGuard\\wireguard.exe" /installtunnelservice "{WG_CONFIG_PATH}"')
echo     local_ips = get_local_ips()
echo     cloud_api_url = os.environ.get("CLOUD_API_URL")
echo     if cloud_api_url:
echo         try:
echo             report_ips_to_cloud(cloud_api_url, customer, local_ips)
echo         except Exception as e:
echo             return {"status": "partial", "message": f"Config applied, but failed to report IPs: {e}"}
echo     return {"status": "success", "message": f"Config applied for {customer}", "ips": local_ips}
echo.
echo if __name__ == "__main__":
echo     customer = os.environ.get("CUSTOMER", "customer1")
echo     cloud_api_url = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/report")
echo     local_ips = get_local_ips()
echo     print(f"[Agent Startup] Reporting IPs: {local_ips} for customer: {customer}")
echo     report_ips_to_cloud(cloud_api_url, customer, local_ips)
echo     import uvicorn
echo     uvicorn.run(app, host="0.0.0.0", port=5000)
goto :eof

:write_register_script
echo import requests, os, socket
echo CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/register")
echo CUSTOMER = os.environ.get("CUSTOMER", "customer1")
echo def get_local_ips():
echo     ips = []
echo     hostname = socket.gethostname()
echo     try:
echo         for ip in socket.gethostbyname_ex(hostname)[2]:
echo             if not ip.startswith("127."):
echo                 ips.append(ip)
echo     except Exception:
echo         pass
echo     return ips
echo ips = get_local_ips()
echo payload = {"customer": CUSTOMER, "ips": ips}
echo try:
echo     r = requests.post(CLOUD_API_URL, json=payload, timeout=10)
echo     print(f"Registration result: {r.text}")
echo except Exception as e:
echo     print(f"Failed to register agent: {e}")
goto :eof

:write_fetch_script
echo import os, requests
echo CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/generate_config")
echo CUSTOMER = os.environ.get("CUSTOMER", "customer1")
echo WG_CONFIG_PATH = "C:/WireGuard/wg0.conf"
echo resp = requests.post(CLOUD_API_URL, json={"customer": CUSTOMER})
echo if resp.status_code == 200:
echo     data = resp.json()
echo     config_content = data.get("config")
echo     if config_content:
echo         with open(WG_CONFIG_PATH, "w") as f:
echo             f.write(config_content)
echo         print(f"WireGuard config saved to {WG_CONFIG_PATH}")
echo     else:
echo         print("No config content received from server. Check backend response.")
echo else:
echo     print(f"Failed to fetch config from cloud API. Status: {resp.status_code}, Response: {resp.text}")


REM Write add_peer.py for peer automation
call :write_add_peer_script > "%ADD_PEER_SCRIPT_PATH%"
echo Finished writing add_peer.py>> "%LOGFILE%"
if exist "%ADD_PEER_SCRIPT_PATH%" (
    echo add_peer.py created successfully in C:\WireGuard>> "%LOGFILE%"
) else (
    echo ERROR: add_peer.py was NOT created in C:\WireGuard. Check permissions and run as Administrator.>> "%LOGFILE%"
)
goto :eof

:write_add_peer_script
echo import requests, os
echo CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://13.58.212.239:8000/add_peer")
echo CUSTOMER = os.environ.get("CUSTOMER", "customer1")
echo PEER_PUBLIC_KEY = os.environ.get("PEER_PUBLIC_KEY", "")
echo PEER_ALLOWED_IPS = os.environ.get("PEER_ALLOWED_IPS", "10.0.0.2/32")
echo payload = {"customer": CUSTOMER, "peer_public_key": PEER_PUBLIC_KEY, "peer_allowed_ips": PEER_ALLOWED_IPS}
echo try:
echo     r = requests.post(CLOUD_API_URL, json=payload, timeout=10)
echo     print(f"Add peer result: {r.text}")
echo except Exception as e:
echo     print(f"Failed to add peer: {e}")
goto :eof

