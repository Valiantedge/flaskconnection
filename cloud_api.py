from fastapi import FastAPI, Request

app = FastAPI()

# Store reported IPs in memory (for demo; use DB in production)
reported_ips = {}

@app.post("/report")
async def report_ips(request: Request):
    data = await request.json()
    customer = data.get("customer")
    ips = data.get("ips")
    if not customer or not ips:
        return {"status": "error", "message": "Missing customer or IPs"}
    reported_ips[customer] = ips
    return {"status": "success", "message": f"IPs received for {customer}", "ips": ips}

@app.get("/ips/{customer}")
async def get_ips(customer: str):
    ips = reported_ips.get(customer)
    if not ips:
        return {"status": "error", "message": "No IPs found for customer"}
    return {"status": "success", "customer": customer, "ips": ips}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
