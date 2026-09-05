from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psutil
import platform
import os
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
                    temperatures[entry.label or sensor_name] = round(
                        entry.current, 1
                    )

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
        "load": round(os.getloadavg()[0], 2),
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


@app.get("/api/processes")
def get_processes():
    processes = []

    for proc in psutil.process_iter(
        ["pid", "name", "username", "cpu_percent", "memory_percent", "status"]
    ):
        try:
            info = proc.info

            processes.append({
                "pid": info["pid"],
                "name": info["name"] or "unknown",
                "user": info["username"] or "-",
                "cpu": round(info["cpu_percent"] or 0, 1),
                "memory": round(info["memory_percent"] or 0, 1),
                "status": info["status"] or "-"
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(key=lambda x: x["cpu"], reverse=True)

    return {
        "count": len(processes),
        "processes": processes[:50]
    }


@app.get("/api/storage")
def get_storage():
    """
    Return useful Linux storage information.

    Only real Linux filesystems are reported.
    Windows/NTFS partitions that are not mounted are ignored.
    Docker/virtual filesystems are ignored.
    """

    storage = []

    excluded_fs_types = {
        "tmpfs",
        "devtmpfs",
        "overlay",
        "squashfs",
        "proc",
        "sysfs",
        "cgroup",
        "cgroup2",
        "devpts",
        "mqueue",
        "shm",
        "autofs",
        "efivarfs",
        "pstore",
        "securityfs",
        "debugfs",
        "tracefs",
        "fusectl",
        "configfs",
        "hugetlbfs",
        "ramfs"
    }

    # The API container cannot see the host mount namespace directly.
    # / is nevertheless backed by the host's root filesystem.
    try:
        root_usage = psutil.disk_usage("/")

        storage.append({
            "device": "/dev/nvme0n1p4",
            "mountpoint": "/",
            "filesystem": "ext4",
            "total_gb": round(root_usage.total / (1024 ** 3), 2),
            "used_gb": round(root_usage.used / (1024 ** 3), 2),
            "free_gb": round(root_usage.free / (1024 ** 3), 2),
            "usage_percent": round(root_usage.percent, 1)
        })
    except (PermissionError, FileNotFoundError, OSError):
        pass

    # Add mounted filesystems that are genuinely visible to the container,
    # while excluding Docker's special mounts.
    try:
        for partition in psutil.disk_partitions(all=False):
            try:
                device = partition.device
                mountpoint = partition.mountpoint
                fstype = (partition.fstype or "").lower()

                if not mountpoint:
                    continue

                if mountpoint in {
                    "/",
                    "/etc/hosts",
                    "/etc/hostname",
                    "/etc/resolv.conf"
                }:
                    continue

                if fstype in excluded_fs_types:
                    continue

                # Never display Windows partitions in SircuitLab.
                if fstype in {"ntfs", "ntfs3", "exfat"}:
                    continue

                usage = psutil.disk_usage(mountpoint)

                storage.append({
                    "device": device,
                    "mountpoint": mountpoint,
                    "filesystem": partition.fstype or "unknown",
                    "total_gb": round(usage.total / (1024 ** 3), 2),
                    "used_gb": round(usage.used / (1024 ** 3), 2),
                    "free_gb": round(usage.free / (1024 ** 3), 2),
                    "usage_percent": round(usage.percent, 1)
                })

            except (
                PermissionError,
                FileNotFoundError,
                OSError
            ):
                continue

    except Exception:
        pass

    # Remove duplicate devices/mounts.
    unique = []
    seen = set()

    for item in storage:
        key = (item["device"], item["mountpoint"])

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    return {
        "count": len(unique),
        "filesystems": unique
    }

