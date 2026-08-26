from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psutil
import platform
import socket
import time

app = FastAPI(title="SircuitLab Home Server API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "project": "SircuitLab Home Server",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


def get_temperature():
    temperatures = {}

    try:
        sensors = psutil.sensors_temperatures()

        for sensor_name, entries in sensors.items():
            for entry in entries:
                if entry.current is not None:
                    temperatures[entry.label or sensor_name] = round(entry.current, 1)

    except Exception:
        pass

    return temperatures


@app.get("/system")
def system_info():

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    battery = psutil.sensors_battery()

    battery_info = None

    if battery is not None:
        battery_info = {
            "percent": round(battery.percent, 1),
            "charging": battery.power_plugged,
            "seconds_left": battery.secsleft
        }

    uptime_seconds = int(time.time() - psutil.boot_time())

    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_release": platform.release(),
        "kernel": platform.version(),

        "cpu": {
            "usage_percent": psutil.cpu_percent(interval=0.5),
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True)
        },

        "memory": {
            "usage_percent": memory.percent,
            "used_gb": round(memory.used / (1024 ** 3), 2),
            "total_gb": round(memory.total / (1024 ** 3), 2)
        },

        "disk": {
            "usage_percent": disk.percent,
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "total_gb": round(disk.total / (1024 ** 3), 2)
        },

        "battery": battery_info,

        "temperature": get_temperature(),

        "uptime_seconds": uptime_seconds,

        "network": {
            "bytes_sent": psutil.net_io_counters().bytes_sent,
            "bytes_received": psutil.net_io_counters().bytes_recv
        }
    }
