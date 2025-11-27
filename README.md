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

Design notes
- `load_config(path)` validates the config and returns a `(legal_times, tolerance)` tuple.
- `parse_time(time_str)` is strict: it requires `hh:mm:ss.ms` and integer components.
- `get_closest_legal_time(time_str, legal_times, tolerance)` converts the input to seconds and finds the closest legal value using the given tolerance.

Next steps (suggested)
- Add CLI flags to override `tolerance` on the command line.
- Accept other input time formats (e.g., `mm:ss.ms` or `ss.ms`).
- Add integration tests that run the CLI end-to-end.
