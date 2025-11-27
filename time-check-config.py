import argparse
import sys
import json
import os

def parse_time(time_str):
    parts = time_str.split(':')
    if len(parts) != 3:
        raise ValueError("Time format must be hh:mm:ss.ms")

    hours_str, minutes_str, sec_ms_str = parts
    sec_parts = sec_ms_str.split('.')
    if len(sec_parts) != 2:
        raise ValueError("Seconds and milliseconds should be separated by a '.'")

    seconds_str, ms_str = sec_parts
    try:
        hours = int(hours_str)
        minutes = int(minutes_str)
        seconds = int(seconds_str)
        ms = int(ms_str)
    except ValueError:
        raise ValueError("Time components must be integers")

    total_seconds = hours * 3600 + minutes * 60 + seconds + ms / 1000.0
    return total_seconds


def get_closest_legal_time_from_seconds(input_seconds, legal_times, tolerance=0.6):
    closest_legal = None
    smallest_delta = None
    for legal in legal_times:
        delta = abs(input_seconds - legal)
        if smallest_delta is None or delta < smallest_delta:
            smallest_delta = delta
            closest_legal = legal

    if smallest_delta is not None and smallest_delta <= tolerance:
        return closest_legal
    else:
        return None


def get_closest_legal_time(time_str, legal_times, tolerance=0.6):
    input_seconds = parse_time(time_str)
    return get_closest_legal_time_from_seconds(input_seconds, legal_times, tolerance)


def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    legal_times = cfg.get('legal_times')
    tolerance = cfg.get('tolerance')
    if not isinstance(legal_times, list) or not all(isinstance(x, (int, float)) for x in legal_times):
        raise ValueError('`legal_times` must be a list of numbers in the config')
    if not isinstance(tolerance, (int, float)):
        raise ValueError('`tolerance` must be a number in the config')
    return legal_times, float(tolerance)


# ------------------
# Unit tests
# ------------------
import unittest
import tempfile


class TestTimeCheckConfig(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file
        self.temp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        cfg = {
            'legal_times': [5, 10, 15, 30, 60, 90, 120],
            'tolerance': 0.6
        }
        json.dump(cfg, self.temp)
        self.temp.close()
        self.config_path = self.temp.name
        # Human-friendly test descriptions printed for each test run.
        # These will appear on stdout when running tests (useful for newcomers).
        TEST_DESCRIPTIONS = {
            'test_load_config': 'Verify config loader reads and validates a correct JSON config.',
            'test_exact_match': 'Confirm exact input times map to exact legal times.',
            'test_within_tolerance': 'Ensure inputs slightly off a legal time but within tolerance still match.',
            'test_outside_tolerance': 'Confirm inputs beyond tolerance are rejected (no match).',
            'test_invalid_config': 'Verify loader raises ValueError for malformed config types.'
        }
        desc = TEST_DESCRIPTIONS.get(self._testMethodName, '')
        if desc:
            print(f"TEST: {self._testMethodName} - {desc}")

    def tearDown(self):
        try:
            os.unlink(self.config_path)
        except Exception:
            pass

    def test_load_config(self):
        legal_times, tolerance = load_config(self.config_path)
        self.assertEqual(legal_times, [5, 10, 15, 30, 60, 90, 120])
        self.assertAlmostEqual(tolerance, 0.6)

    def test_exact_match(self):
        legal_times, tolerance = load_config(self.config_path)
        self.assertEqual(get_closest_legal_time('00:00:05.000', legal_times, tolerance), 5)
        self.assertEqual(get_closest_legal_time('00:00:10.000', legal_times, tolerance), 10)

    def test_within_tolerance(self):
        legal_times, tolerance = load_config(self.config_path)
        self.assertEqual(get_closest_legal_time('00:00:05.500', legal_times, tolerance), 5)
        self.assertEqual(get_closest_legal_time('00:00:10.600', legal_times, tolerance), 10)

    def test_outside_tolerance(self):
        legal_times, tolerance = load_config(self.config_path)
        self.assertIsNone(get_closest_legal_time('00:00:05.700', legal_times, tolerance))

    def test_invalid_config(self):
        # write an invalid config
        bad = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        bad.write('{"legal_times": "not-a-list", "tolerance": "x"}')
        bad.close()
        with self.assertRaises(ValueError):
            load_config(bad.name)
        os.unlink(bad.name)


# ------------------
# Main functionality
# ------------------
def main():
    parser = argparse.ArgumentParser(
        description='Evaluate a time value (hh:mm:ss.ms) against legal times from a config file.'
    )
    parser.add_argument('time', nargs='?', help='Time in hh:mm:ss.ms format')
    parser.add_argument('--config', default=None, help='Path to JSON config file (if omitted, searches CWD then executable directory)')
    parser.add_argument('--test', action='store_true', help='Run unit tests')
    parser.add_argument('--verbose', action='store_true', help='Run tests in verbose mode')
    args = parser.parse_args()

    if args.test:
        # Run unit tests
        if args.verbose:
            unittest.main(argv=[sys.argv[0]], verbosity=2)
        else:
            unittest.main(argv=[sys.argv[0]])
        return

    if not args.time:
        parser.error('the following arguments are required: time')

    # Load config
    # Resolve config path: prefer explicit `--config`, then CWD, then exe/script dir
    def resolve_config_path(provided_path=None):
        if provided_path:
            return provided_path
        # check current working directory first
        cwd_path = os.path.join(os.getcwd(), 'time_config.json')
        if os.path.exists(cwd_path):
            return cwd_path
        # next check directory of the running exe/script
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(base_dir, 'time_config.json')
        return exe_path

    config_path = resolve_config_path(args.config)
    try:
        legal_times, tolerance = load_config(config_path)
    except Exception as e:
        print(f'Error loading config ({config_path}): {e}')
        sys.exit(2)

    try:
        result = get_closest_legal_time(args.time, legal_times, tolerance)
        if result is None:
            print('Timer rejected: deviation exceeds tolerance.')
        else:
            print(f'Closest legal time: {result}/{seconds_to_hms(int(result))}')
    except ValueError as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    main()
