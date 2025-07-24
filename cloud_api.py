from fastapi import FastAPI, Request

app = FastAPI()

# Store reported IPs in memory (for demo; use DB in production)
reported_ips = {}
registered_agents = {}

@app.post("/report")
@app.post("/register")
async def register_agent(request: Request):
    data = await request.json()
    customer = data.get("customer")
    # Get public IP from request headers or remote address
    public_ip = request.client.host if hasattr(request, 'client') else None
    if not customer or not public_ip:
        return {"status": "error", "message": "Missing customer or public IP"}
    registered_agents[customer] = public_ip
    return {"status": "success", "message": f"Agent registered for {customer}", "ip": public_ip}
async def report_ips(request: Request):
    data = await request.json()
    customer = data.get("customer")
    ips = data.get("ips")
    if not customer or not ips:
        return {"status": "error", "message": "Missing customer or IPs"}
    reported_ips[customer] = ips
    return {"status": "success", "message": f"IPs received for {customer}", "ips": ips}

@app.get("/ips/{customer}")
@app.get("/agent/{customer}")
async def get_agent_ip(customer: str):
    ip = registered_agents.get(customer)
    if not ip:
        return {"status": "error", "message": "No agent IP found for customer"}
    return {"status": "success", "customer": customer, "ip": ip}
async def get_ips(customer: str):
    ips = reported_ips.get(customer)
    if not ips:
        return {"status": "error", "message": "No IPs found for customer"}
    return {"status": "success", "customer": customer, "ips": ips}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
