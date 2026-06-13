import asyncio
import httpx
import random
import time
from datetime import datetime, timezone

API_BASE_URL = "http://localhost:8000"

async def simulate_sensor_data():
    print(f"Starting engine simulation... pointing to {API_BASE_URL}")
    async with httpx.AsyncClient() as client:
        # Check health first
        try:
            r = await client.get(f"{API_BASE_URL}/health")
            print(f"Backend Health: {r.status_code} {r.json()}")
        except Exception as e:
            print(f"Failed to connect to backend: {e}")
            return

        engines = [f"ENG-{i:03d}" for i in range(101, 110)]

        while True:
            eng_id = random.choice(engines)
            
            payload = {
                "event": {
                    "engine_id": eng_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "engine_rpm": random.randint(800, 3000),
                    "lub_oil_pressure": random.uniform(1.0, 5.0),
                    "fuel_pressure": random.uniform(5.0, 15.0),
                    "coolant_pressure": random.uniform(1.0, 4.0),
                    "lub_oil_temp": random.uniform(60, 110),
                    "coolant_temp": random.uniform(70, 95)
                }
            }

            try:
                res = await client.post(f"{API_BASE_URL}/engine-risk/predict", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent sensor data for {eng_id} -> Result: {data['severity'].upper()} (Risk Score: {data['risk_score']:.2f})")
                else:
                    print(f"Error {res.status_code}: {res.text}")
            except Exception as e:
                print(f"Request failed: {e}")

            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(simulate_sensor_data())
