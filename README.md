# MSEdge Creds Dumper

A proof of concept tool that extracts saved credentials from Microsoft Edge's process memory using Windows API calls. Built for educational and authorized purposes only.

This POC is based on the recent finding by [@L1v1ng0ffTh3L4N](https://x.com/L1v1ng0ffTh3L4N) which you can read more about on his Twitter thread [here](https://x.com/L1v1ng0ffTh3L4N/status/2051308329880719730).

I built this program while learning to work with Windows API and Internals. There might be several limitations and bugs to which fixes and contributions are welcome.
## What Does This Do?

This script dumps the full memory of the main Microsoft Edge browser process, then scans through that dump looking for saved website credentials (domains, usernames, and passwords) that are still sitting in memory in plaintext.

It works in two stages:

1. **Memory Dump** — Finds the running Edge process, opens it with full access, and writes a complete memory dump to disk using `MiniDumpWriteDump` from `dbghelp.dll`.
2. **Credential Extraction** — Parses the `.dmp` file using the `minidump` library and runs regex pattern matching across every memory segment to pull out domain/username/password combos.

## How It Works Under the Hood

The tool uses raw Windows API calls through Python's `ctypes` module instead of relying on higher level wrappers. Here's the flow:

1. Enumerate all running processes using `psutil`
2. Identify the main Edge process (not a renderer or GPU subprocess) by checking for the absence of `--type=` in the command line args
3. Call `OpenProcess` with `PROCESS_ALL_ACCESS` to get a handle
4. Create a dump file using `CreateFileW`
5. Write the full process memory with `MiniDumpWriteDump` (using `MiniDumpWithFullMemory` flag)
6. Parse the dump with `minidump` and scan every memory segment for credential patterns

## Requirements

| Dependency | What It's For |
|------------|---------------|
| `psutil` | Finding and enumerating running processes |
| `minidump` | Parsing the `.dmp` memory dump file |
| Python 3.6+ | f strings and modern syntax |
| Windows | Uses `dbghelp.dll` and `kernel32.dll` (Windows only) |
| Admin privileges | Required to open the Edge process with full access |

### Install Dependencies

```bash
pip install psutil minidump
```

## Usage

> ⚠️ **You must run this as Administrator.** The script needs elevated privileges to access Edge's process memory.

1. Make sure Microsoft Edge is open and you're logged into some websites
2. Open a terminal as Administrator
3. Run the script:

```bash
python main.py
```

4. The tool will dump Edge's memory to `edge.dmp` (this file can be large, often 500MB+), scan it, and print any credentials it finds:

```
[DOMAIN]   example.com
[USERNAME] user@email.com
[PASSWORD] supersecretpassword
--------------------------------------------------
```

## Limitations

- Relies on native DLLs
- The dump file can get very large depending on how much memory Edge is using
- Only catches credentials that happen to be in plaintext memory at the time of the dump
- The regex pattern specifically looks for `.com` domains, so it may miss credentials for other TLDs

## Credits

- **Research by:** [@L1v1ng0ffTh3L4N](https://x.com/L1v1ng0ffTh3L4N) — the original technique this tool is based on
- **Built by:** [Kavin Jindal](https://github.com/kavin-jindal)

## Disclaimer

This tool is provided strictly for **educational purposes and authorized security testing**. Do not use it on systems or accounts you don't own or have explicit written permission to test. Unauthorized access to computer systems and data is illegal. I take no responsibility for any misuse of this software.

## License

MIT
