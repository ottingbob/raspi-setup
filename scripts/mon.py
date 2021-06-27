import platform
import subprocess
import sys
from datetime import datetime
from os import uname, popen
from pathlib import Path
from typing import List, Optional

MON_DIRECTORY = "/tmp/mon"
MON_CPU_FILE = f"{MON_DIRECTORY}/cpu_info.json"
MON_MEM_FILE = f"{MON_DIRECTORY}/mem_info.json"

# TODO: Need to update this image as two of the servers have been
#   updated locally
ubuntu_platform = "Linux-5.4.0-1034-raspi-aarch64-with-glibc2.29"
rasbian_platform = "Linux-5.10.17-v7l+-armv7l-with-debian-10.9"
supported_platforms = [ubuntu_platform, rasbian_platform]
node_name = uname()[1]

current_platform = platform.platform()
if current_platform not in supported_platforms:
    print("Unable to run script on unsupported platform:", current_platform)


def now_timestamp_str() -> str:
    now = datetime.now()
    return now.strftime("%H:%M:%S-CST::%m_%d_%Y")


class CPUTempInfo:

    name: str
    # Usually either `Virtual device` or `ISA adapter`
    adapter: str
    # Typically this is one or the other
    temp1: str
    # Really only seen the value of `N/A` here
    in0: str

    expected_keys: List[str] = ['Adapter', 'temp1', 'in0']

    def __init__(self):
        self.name = ""
        self.adapter = ""
        self.temp1 = ""
        self.in0 = ""

    def set_field(self, found_key: str, value: str):
        if found_key == self.expected_keys[0]:
            self.adapter = value
        elif found_key == self.expected_keys[1]:
            self.temp1 = value
        else:
            self.in0 = value

    def parse_text(self, text: str):
        found_key = False
        for ekey in self.expected_keys:
            if text.startswith(ekey):
                value = text[len(ekey) + 1:].strip()
                self.set_field(ekey, value)
                found_key = True
                break
        if not found_key:
            self.name = text

    def _add_fields(self, modify: str = "") -> str:
        name = "" if self.name == "" else f'"name": "{self.name}"'
        adapter = "" if self.adapter == "" else f'"adapter": "{self.adapter}"'
        temp1 = "" if self.temp1 == "" else f'"temp1": "{self.temp1}"'
        in0 = "" if self.in0 == "" else f'"in0": "{self.in0}"'

        def add_field(append: str = "", field: str = "") -> str:
            if field != "":
                append = append + f"{field}, "
            return append

        fields = [name, adapter, temp1, in0]
        for field in fields:
            modify = add_field(modify, field)
        return modify

    def to_json(self) -> str:
        resp_str = self._add_fields('{')
        if len(resp_str) > 1:
            resp_str = resp_str[:-2]
        return resp_str + "}"

    def __str__(self) -> str:
        base_resp = "CPUTempInfo<"
        resp_str = self._add_fields(base_resp)
        # Remove trailing whitespace and comma if any
        if len(resp_str) > len(base_resp):
            resp_str = resp_str[:-2]
        resp_str += ">"

        return resp_str


# TODO: Add Container class
# Add fields to class: timestamp, nodeName
class CPUTempResults:

    cpu_temps: List[CPUTempInfo] = []
    timestamp: str = ""

    def __init__(self, temps: List[CPUTempInfo] = []):
        self.cpu_temps = temps
        # Get current time
        self.timestamp = now_timestamp_str()

    def to_json(self) -> str:
        json_resp = '{'
        json_resp += f'"timestamp": "{self.timestamp}",'
        json_resp += f'"node_name": "{node_name}",'
        json_resp += '"items":['
        i = 0
        end = len(self.cpu_temps)
        while i < end:
            data = self.cpu_temps[i]
            line = data.to_json()
            if i + 1 != end:
                line += ","
            json_resp += line
            i += 1
        json_resp += ']}'
        return json_resp


class MemInfo:

    TOTAL_COL = 0
    USED_COL = 1
    FREE_COL = 2

    total: float
    used: float
    free: float

    def get_sys_mem_info(self):
        mem_info = popen('free -t').readlines()[-1].split()[1:]
        self.total = self.bytes_to_mb(int(mem_info[self.TOTAL_COL]))
        self.used = self.bytes_to_mb(int(mem_info[self.USED_COL]))
        self.free = self.bytes_to_mb(int(mem_info[self.FREE_COL]))

    # Keep 3 decimal places in mb conversion
    def bytes_to_mb(self, byte_size: int = 0) -> float:
        # TODO: Need to verify this method:
        # https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
        return round(byte_size / float(1 << 10), 3)

    def to_json(self) -> str:
        timestamp = now_timestamp_str()
        json_resp = "{"
        json_resp += f'"timestamp": "{timestamp}",'
        json_resp += f'"node_name": "{node_name}",'
        json_resp += f'"total_memory_mb": {self.total},'
        json_resp += f'"used_memory_mb": {self.used},'
        json_resp += f'"free_memory_mb": {self.free}'
        json_resp += "}"
        return json_resp


def parse_temp_info(text_block: List[str]) -> Optional[CPUTempInfo]:
    if len(text_block) == 0:
        return None
    cpui = CPUTempInfo()
    for line in text_block:
        cpui.parse_text(line)
    return cpui


# Based on the platform we run a different command
cpu_temp_res: CPUTempResults = CPUTempResults()
if current_platform == ubuntu_platform:
    cmd = "sensors"
    sensors_output = subprocess.run(cmd, capture_output=True, text=True)
    if sensors_output.returncode != 0:
        print(f"Unable to run {cmd} command")
        sys.exit(1)
    # Parse the text of the sensors command
    text_block: List[str] = []
    cpu_data: List[CPUTempInfo] = []
    for line in sensors_output.stdout.split('\n'):
        if len(line) == 0:
            cpu_ti = parse_temp_info(text_block)
            if cpu_ti is not None:
                cpu_data.append(cpu_ti)
            text_block = []
            continue
        text_block.append(line)
    cpu_temp_res = CPUTempResults(temps=cpu_data)
elif current_platform == rasbian_platform:
    cmd = "/opt/vc/bin/vcgencmd measure_temp"
    measure_temp_output = subprocess.run(cmd.split(' '),
                                         capture_output=True,
                                         text=True)
    if measure_temp_output.returncode != 0:
        print(f"Unable to run {cmd} command")
        sys.exit(1)
    # Since we are already here we can wrap this up pretty quick
    temp = measure_temp_output.stdout[len("temp="):-1]
    info = CPUTempInfo()
    info.name = "__DEFAULT_ADAPTER__"
    info.adapter = "__DEFAULT_ADAPTER__"
    info.temp1 = temp
    cpu_temp_res = CPUTempResults(temps=[info])

# Get Node memory information
mi = MemInfo()
mi.get_sys_mem_info()

# Create or move on for directory
Path(MON_DIRECTORY).mkdir(exist_ok=True)

# Write cpu temp json to file location
cpu_temp_data = cpu_temp_res.to_json()
with open(MON_CPU_FILE, mode="w") as write_file:
    write_file.write(cpu_temp_data)

# Write memory info json to file location
mem_data = mi.to_json()
with open(MON_MEM_FILE, mode="w") as write_file:
    write_file.write(mem_data)
