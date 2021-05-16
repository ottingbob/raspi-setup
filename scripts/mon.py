import subprocess
import sys
from typing import List, Optional
from pathlib import Path

MON_DIRECTORY = "/tmp/mon"
MON_CPU_FILE = f"{MON_DIRECTORY}/cpu_info.json"

cmd = "sensors"
sensors_output = subprocess.run(cmd, capture_output=True, text=True)
if sensors_output.returncode != 0:
    print(f"Unable to run {cmd} command")
    sys.exit(1)


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


def to_json(cpu_info_list: List[CPUTempInfo] = []) -> str:
    json_resp = ""
    end = len(cpu_info_list)
    i = 0
    json_resp = '{"items":['
    while i < end:
        data = cpu_info_list[i]
        line = data.to_json()
        if i + 1 != end:
            line += ","
        json_resp += line
        i += 1
    json_resp += ']}'
    return json_resp


def parse_temp_info(text_block: List[str]) -> Optional[CPUTempInfo]:
    if len(text_block) == 0:
        return None
    cpui = CPUTempInfo()
    for line in text_block:
        cpui.parse_text(line)
    return cpui


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

# Create or move on for directory
Path(MON_DIRECTORY).mkdir(exist_ok=True)
# Write json to file location
json_data = to_json(cpu_data)
with open(MON_CPU_FILE, mode="w") as write_file:
    write_file.write(json_data)
