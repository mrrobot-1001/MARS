import asyncio
import httpx
import random
import time
from datetime import datetime, timezone

API_BASE_URL = "http://localhost:8000"

async def simulate_sensor_data():
    print(f"Starting sensor simulation... pointing to {API_BASE_URL}")
    async with httpx.AsyncClient() as client:
        # Check health first
        try:
            r = await client.get(f"{API_BASE_URL}/health")
            print(f"Backend Health: {r.status_code} {r.json()}")
        except Exception as e:
            print(f"Failed to connect to backend: {e}")
            return

        segments = [f"SEG-{i:03d}" for i in range(1, 10)]

        while True:
            # Generate random payload
            seg_id = random.choice(segments)
            speed = random.uniform(60, 140)
            vibration = random.uniform(0.1, 0.9)
            
            payload = {
                "segment": {
                    "segment_id": seg_id,
                    "line_id": "LINE-A",
                    "region": "central",
                    "asset_type": "track",
                    "age_years": random.randint(5, 50),
                    "maintenance_score": random.uniform(0.3, 0.9),
                    "curvature_degree": random.uniform(0, 5),
                    "max_permitted_speed": 120
                },
                "events": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "segment_id": seg_id,
                        "train_id": f"TRN-{random.randint(1000, 9999)}",
                        "speed": speed,
                        "acceleration": random.uniform(-1, 1),
                        "vibration_vertical": vibration,
                        "vibration_lateral": vibration * 0.7,
                        "track_temperature": random.uniform(10, 45)
                    }
                ]
            }

            try:
                # Fire request to track-risk endpoint
                res = await client.post(f"{API_BASE_URL}/track-risk/predict", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent sensor data for {seg_id} -> Result: {data['severity'].upper()} (Risk Score: {data['risk_score']:.2f})")
                else:
                    print(f"Error {res.status_code}: {res.text}")
            except Exception as e:
                print(f"Request failed: {e}")

            # Wait 2 seconds before sending next reading
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(simulate_sensor_data())
