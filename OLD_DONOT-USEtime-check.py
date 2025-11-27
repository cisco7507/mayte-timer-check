import argparse
import sys

def parse_time(time_str):
    """
    Parse a time string in the format hh:mm:ss.ms into total seconds.

    Parameters:
        time_str (str): Time in "hh:mm:ss.ms" format.

    Returns:
        float: Total seconds.

    Raises:
        ValueError: If the input format is incorrect.
    """
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


def get_closest_legal_time(time_str, legal_times, tolerance=0.6):
    """
    Compare the input time (converted to seconds) with a list of legal times.
    If the absolute difference between the input time and the closest legal time
    is within the tolerance, return that legal time. Otherwise, return None.

    Parameters:
        time_str (str): Time in "hh:mm:ss.ms" format.
        legal_times (list of float): Predefined legal times (in seconds).
        tolerance (float): Maximum allowed deviation in seconds.

    Returns:
        float or None: The closest legal time if within tolerance; otherwise None.
    """
    input_seconds = parse_time(time_str)
    
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


def seconds_to_hms(seconds):
    """
    Convert seconds (an integer) into a string in hh:mm:ss format.

    Parameters:
        seconds (int): The seconds value to convert.

    Returns:
        str: The time formatted as hh:mm:ss.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# --------------
# Unit tests
# --------------
import unittest

class TestTimeComparison(unittest.TestCase):
    def setUp(self):
        self.legal_times = [5, 10, 15, 30, 60, 90, 120]
    
    def test_exact_match(self):
        self.assertEqual(get_closest_legal_time("00:00:05.000", self.legal_times), 5)
        self.assertEqual(get_closest_legal_time("00:00:10.000", self.legal_times), 10)
        self.assertEqual(get_closest_legal_time("00:00:15.000", self.legal_times), 15)
        self.assertEqual(get_closest_legal_time("00:00:30.000", self.legal_times), 30)
        self.assertEqual(get_closest_legal_time("00:01:00.000", self.legal_times), 60)
        self.assertEqual(get_closest_legal_time("00:01:30.000", self.legal_times), 90)
        self.assertEqual(get_closest_legal_time("00:02:00.000", self.legal_times), 120)
    
    def test_within_tolerance(self):
        self.assertEqual(get_closest_legal_time("00:00:05.500", self.legal_times), 5)
        self.assertEqual(get_closest_legal_time("00:00:10.600", self.legal_times), 10)
        self.assertEqual(get_closest_legal_time("00:00:15.500", self.legal_times), 15)
        self.assertEqual(get_closest_legal_time("00:00:30.500", self.legal_times), 30)
        self.assertEqual(get_closest_legal_time("00:01:00.500", self.legal_times), 60)
        self.assertEqual(get_closest_legal_time("00:01:30.500", self.legal_times), 90)
        self.assertEqual(get_closest_legal_time("00:02:00.500", self.legal_times), 120)
    
    def test_outside_tolerance(self):
        self.assertIsNone(get_closest_legal_time("00:00:05.700", self.legal_times))
        self.assertIsNone(get_closest_legal_time("00:00:10.700", self.legal_times))
        self.assertIsNone(get_closest_legal_time("00:00:15.700", self.legal_times))
        self.assertIsNone(get_closest_legal_time("00:00:30.700", self.legal_times))
        self.assertIsNone(get_closest_legal_time("00:01:00.700", self.legal_times))
        self.assertIsNone(get_closest_legal_time("00:01:30.700", self.legal_times))
        self.assertIsNone(get_closest_legal_time("00:02:00.700", self.legal_times))
    
    def test_invalid_format(self):
        with self.assertRaises(ValueError):
            parse_time("00:00:10")  # Missing the '.ms' part

    def test_seconds_to_hms(self):
        self.assertEqual(seconds_to_hms(5), "00:00:05")
        self.assertEqual(seconds_to_hms(10), "00:00:10")
        self.assertEqual(seconds_to_hms(15), "00:00:15")
        self.assertEqual(seconds_to_hms(30), "00:00:30")
        self.assertEqual(seconds_to_hms(60), "00:01:00")
        self.assertEqual(seconds_to_hms(90), "00:01:30")
        self.assertEqual(seconds_to_hms(120), "00:02:00")


# ------------------
# Main functionality
# ------------------
if __name__ == '__main__':
    # If the user passes the "--test" flag, run the unit tests.
    if "--test" in sys.argv:
        sys.argv.remove("--test")
        unittest.main()
    else:
        parser = argparse.ArgumentParser(
            description="Evaluate a time value (hh:mm:ss.ms) against legal times."
        )
        parser.add_argument("time", help="Time in hh:mm:ss.ms format")
        args = parser.parse_args()

        # Predefined legal times in seconds.
        legal_times = [5, 10, 15, 30, 60, 90, 120]
    
        try:
            result = get_closest_legal_time(args.time, legal_times)
            if result is None:
                print("Timer rejected: deviation exceeds tolerance.")
            else:
                # Append the converted seconds (hh:mm:ss) after a "/"
                print(f"Closest legal time: {result}/{seconds_to_hms(result)}")
        except ValueError as e:
            print(f"Error: {e}")
            