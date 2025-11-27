CI: GitHub Actions build
------------------------
This repository includes a GitHub Actions workflow that builds a Windows single-file EXE using PyInstaller when commits are pushed to `main` or a PR targets `main`.
Where to find the build
- After a successful run, the built EXE and a sample `time_config.json` are available as workflow artifacts under the GitHub Actions run page:
  - Artifact: `time-check-config-exe` (contains `time-check-config.exe`)
  - Artifact: `time-check-config-sample` (contains `time_config.json`)

Notes
- The workflow runs on `windows-2019` to match Windows Server 2019 compatibility.
- The program still expects `time_config.json` to be external — place the config next to the EXE on the target machine or pass `--config <path>`.
# time-check-config

This version of the time-check tool reads `legal_times` and `tolerance` from an external JSON configuration file and evaluates a user-supplied time against those legal values.

Files added
- `time-check-config.py`: CLI script and library functions.
- `time_config.json`: Default configuration file.

Overview
- Input format: `hh:mm:ss.ms` (hours:minutes:seconds.milliseconds). Example: `00:00:05.500`.
- Configuration: JSON file with the following fields:
  - `legal_times`: array of numbers (seconds) e.g. `[5, 10, 15]`.
  - `tolerance`: number (seconds) allowed deviation for a match.

Default config
The default config file `time_config.json` contains:

```
{
  "legal_times": [5, 10, 15, 30, 60, 90, 120],
  "tolerance": 0.6
}
```

Usage
- Run the CLI with a time and optionally a config path:

```
python time-check-config.py 00:00:05.500

python time-check-config.py 00:00:05.500 --config my_config.json
```

- On success (within tolerance) the output will be:

```
Closest legal time: <seconds>/<hh:mm:ss>
```

- If no legal time is near enough:

```
Timer rejected: deviation exceeds tolerance.
```

Running tests
- The script includes `unittest` coverage. Run tests with:

```
python time-check-config.py --test
```

Tests now print a short human-readable description before each test runs. This helps reviewers and contributors
understand each test's purpose at a glance.

Example test run (verbose):

```
python time-check-config.py --test --verbose

TEST: test_exact_match - Confirm exact input times map to exact legal times.
test_exact_match (__main__.TestTimeCheckConfig.test_exact_match) ... ok
TEST: test_invalid_config - Verify loader raises ValueError for malformed config types.
test_invalid_config (__main__.TestTimeCheckConfig.test_invalid_config) ... ok
TEST: test_load_config - Verify config loader reads and validates a correct JSON config.
test_load_config (__main__.TestTimeCheckConfig.test_load_config) ... ok
TEST: test_outside_tolerance - Confirm inputs beyond tolerance are rejected (no match).
test_outside_tolerance (__main__.TestTimeCheckConfig.test_outside_tolerance) ... ok
TEST: test_within_tolerance - Ensure inputs slightly off a legal time but within tolerance still match.
test_within_tolerance (__main__.TestTimeCheckConfig.test_within_tolerance) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.02s

OK
```

Building a Windows executable (single-file) and keeping the config external
---------------------------------------------------------------------

You can create a standalone Windows executable using `PyInstaller`. The built EXE will *not* contain the
configuration file — the program looks for `time_config.json` in this order:

- If `--config <path>` is provided, that path is used.
- Current working directory: `.\time_config.json`.
- Directory next to the executable/script: `time_config.json` next to `time-check-config.exe`.

This means you can ship `time-check-config.exe` and place `time_config.json` alongside it (or specify a path with `--config`).

Example build steps (Windows PowerShell):

```powershell
cd C:\mayte-timer-check
# create a virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# install PyInstaller
pip install pyinstaller
# build a single-file exe (replace `time-check-config.py` with the script name)
pyinstaller --onefile --name time-check-config time-check-config.py

# After building, the EXE will be at: dist\time-check-config.exe
```

Run the EXE (config next to exe):

```powershell
cd dist
.\time-check-config.exe 00:00:05.500

# or explicitly point to a config file elsewhere:
.\time-check-config.exe 00:00:05.500 --config C:\path\to\time_config.json
```

Notes and compatibility
- PyInstaller must be run on Windows to build a Windows EXE for best results (building on Linux/macOS produces platform-specific binaries).
- Windows Server 2019 compatibility: build on a 64-bit Windows machine with a compatible Python version (3.8-3.12 are commonly supported by recent PyInstaller releases). If you must run the build on a different OS, use a Windows CI runner or container.
- The EXE reads the external `time_config.json`; do not bundle it inside the EXE if you need to edit config without rebuilding.


Design notes
- `load_config(path)` validates the config and returns a `(legal_times, tolerance)` tuple.
- `parse_time(time_str)` is strict: it requires `hh:mm:ss.ms` and integer components.
- `get_closest_legal_time(time_str, legal_times, tolerance)` converts the input to seconds and finds the closest legal value using the given tolerance.

Next steps (suggested)
- Add CLI flags to override `tolerance` on the command line.
- Accept other input time formats (e.g., `mm:ss.ms` or `ss.ms`).
- Add integration tests that run the CLI end-to-end.
