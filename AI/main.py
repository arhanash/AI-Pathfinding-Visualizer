import asyncio
import random
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

app = FastAPI(title="Smart Traffic Insights - AI Simulation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manage websocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

# Centralized State Machine
class TrafficState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.speed = 1.0
        self.isPaused = False
        self.cycles = 0
        self.activeRoadIdx = 0
        self.roads = ['A', 'B', 'C', 'D']
        self.queues = {'A': 12, 'B': 24, 'C': 8, 'D': 15}
        self.totalProcessed = 1245
        self.throughput = 34
        self.emergencyRoad = None
        self.emergencyActive = False
        self.emergencyTimer = 0
        self.simTime = 0
        self.aiActive = True

        # Initialize Chart Data
        self.chartData = {'A': [], 'B': [], 'C': [], 'D': []}
        for i in range(12):
            self.chartData['A'].append(20 + random.random()*20)
            self.chartData['B'].append(25 + random.random()*30)
            self.chartData['C'].append(15 + random.random()*15)
            self.chartData['D'].append(30 + random.random()*20)

    def get_dict(self) -> Dict[str, Any]:
        return {
            "speed": self.speed,
            "isPaused": self.isPaused,
            "cycles": self.cycles,
            "activeRoadIdx": self.activeRoadIdx,
            "roads": self.roads,
            "queues": self.queues,
            "totalProcessed": self.totalProcessed,
            "throughput": self.throughput,
            "emergencyRoad": self.emergencyRoad,
            "emergencyActive": self.emergencyActive,
            "emergencyTimer": self.emergencyTimer,
            "simTime": self.simTime,
            "aiActive": self.aiActive,
            "chartData": self.chartData
        }

state = TrafficState()

async def broadcast_state():
    await manager.broadcast(json.dumps({
        "type": "SIM_STATE",
        "data": state.get_dict()
    }))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # Give connected client initial state immediately
    await websocket.send_text(json.dumps({
        "type": "SIM_STATE",
        "data": state.get_dict()
    }))
    try:
        while True:
            data = await websocket.receive_text()
            cmd = json.loads(data)
            action = cmd.get("action")
            payload = cmd.get("payload", {})
            
            if action == "SET_SPEED":
                state.speed = float(payload.get("speed", 1.0))
            elif action == "TOGGLE_PAUSE":
                state.isPaused = not state.isPaused
            elif action == "TOGGLE_AI":
                state.aiActive = not state.aiActive
            elif action == "RESET_SIM":
                state.reset()
            elif action == "TRIGGER_EMERGENCY":
                road = payload.get("road")
                if road and not state.emergencyActive:
                    state.emergencyActive = True
                    state.emergencyRoad = road
                    state.emergencyTimer = 10 # 10 engine ticks
            elif action == "CANCEL_EMERGENCY":
                state.emergencyActive = False
                state.emergencyRoad = None
                
            # Broadcast the updated state explicitly on command
            await broadcast_state()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background Engine Loop
async def simulation_engine():
    # Base tick rate factor
    base_interval = 1.0
    
    # Tick loop
    while True:
        # Check current speed
        current_speed: float = state.speed
        
        # If speed > 0, sleep inversely proportional to speed
        actual_interval = base_interval / current_speed if current_speed > 0 else 1.0
        await asyncio.sleep(actual_interval)
        
        if state.isPaused:
            continue
            
        # Execute One Tick of logic
        state.simTime += 1
        
        # ---- Logic: Emergency Override Cycle ---- #
        if state.emergencyActive:
            state.emergencyTimer -= 1
            if state.emergencyTimer <= 0:
                state.emergencyActive = False
                state.emergencyRoad = None
        else:
            # Normal cycle rotates every 8 sim seconds
            if state.simTime % 8 == 0:
                state.activeRoadIdx = (state.activeRoadIdx + 1) % 4
                state.cycles += 1

        # ---- Logic: Queue Modification & Throughput ---- #
        activeR = state.emergencyRoad if state.emergencyActive else state.roads[state.activeRoadIdx]
        throughputAdd = 0
        
        for r in state.roads:
            # Random traffic arrival (Simulating YOLO engine detection)
            if random.random() > 0.4:
                incoming = random.randint(0, 2)
                state.queues[r] += incoming
                
            # Subtract cars if road is green
            if r == activeR and state.queues[r] > 0:
                passed = random.randint(1, 4)
                if passed > state.queues[r]:
                    passed = state.queues[r]
                state.queues[r] -= passed
                throughputAdd += passed
                
            # Clamp limits
            state.queues[r] = max(0, min(state.queues[r], 100))
            
        state.totalProcessed += throughputAdd
        
        # Smooth Throughput factor
        if random.random() > 0.8:
            modifier = random.randint(0, 2)
            if random.random() > 0.5:
                state.throughput += modifier
            else:
                state.throughput -= modifier
            # Clamp
            state.throughput = max(15, min(state.throughput, 70))
            
        # Check if we need chart update (every 5 engine ticks for demo)
        if state.simTime % 5 == 0:
            for r in state.roads:
                state.chartData[r].pop(0)
                lastVal = state.chartData[r][-1]
                newVal = lastVal + (random.random() * 10 - 5)
                newVal = max(5, min(newVal, 55))
                state.chartData[r].append(newVal)

        # Emit the results of this tick
        await broadcast_state()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the async background engine
    task = asyncio.create_task(simulation_engine())
    yield
    # Clean up on shutdown
    task.cancel()

app.router.lifespan_context = lifespan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
