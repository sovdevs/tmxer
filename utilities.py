from datetime import datetime
from fs import path
import re


def get_timestamp():
    # Get current time
    current_time = datetime.utcnow()
    # Round down to the nearest 10 seconds
    rounded_seconds = current_time.second // 10 * 10
    # Create a new datetime object with the rounded down seconds
    rounded_time = current_time.replace(second=rounded_seconds, microsecond=0)
    # Return the time as a string
    return rounded_time.strftime("%Y-%m-%d %H:%M:%S")


def make_filename_friendly(filename):
    # Remove invalid characters
    filename = re.sub(r'[\\/:\*\?"<>|]', "", filename)

    # Replace reserved characters
    filename = filename.replace("\\", "-")

    # Remove leading/trailing whitespace and replace remaining whitespace with a hyphen
    filename = re.sub(r"\s+", "-", filename.strip())

    # Normalize case (optional)
    filename = filename.lower()

    return filename
