"""This module contains functions that are used in the main module."""

import contextlib
import json
import os
import platform
import random
import socket
import string
import subprocess
import time
import traceback
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import wraps
from subprocess import PIPE, CalledProcessError, Popen
from urllib.parse import quote

import cpuinfo
import psutil

from config import pto, ttw

PING_TIMEOUT_TIME = pto
TIME_TO_WAIT = ttw


WORKING_DIRECTORY = os.getcwd()

max_max_workers_for_the_pp = 30


def print_status_and_text_from_response(response, video_id=None):
    "prints the status code and text from a response"
    text = response.text
    status = response.status_code

    if len(text) > 200:
        text = f"{text[:200]}..."

    if video_id:
        print(f"""{color.BLUE}Video ID: {video_id}
Response Status Code: {status}
Response Text: {text}{color.END}""")

    else:
        print(f"""{color.BLUE}Response Status Code: {status}
Response Text: {text}{color.END}""")


def get_size(bytes_in_get_size, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes_in_get_size < factor:
            return f"{bytes_in_get_size:.2f}{unit}{suffix}"
        bytes_in_get_size /= factor

    return f"{bytes_in_get_size:.2f}Y{suffix}"


def system_information():  # pylint: disable=too-many-locals, too-many-statements
    """Returns system information."""
    print("=" * 40, "System Information", "=" * 40)
    uname = platform.uname()
    print(f"System: {uname.system}")
    print(f"Node Name: {uname.node}")
    print(f"Release: {uname.release}")
    print(f"Version: {uname.version}")
    print(f"Machine: {uname.machine}")
    print(f"Processor: {uname.processor}")
    print(f"Processor: {cpuinfo.get_cpu_info()['brand_raw']}")
    print(f"Ip-Address: {socket.gethostbyname(socket.gethostname())}")

    # Boot Time
    print("=" * 40, "Boot Time", "=" * 40)
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)  # pylint: disable=invalid-name
    print(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

    # print CPU information
    print("=" * 40, "CPU Info", "=" * 40)
    # number of cores
    print("Physical cores:", psutil.cpu_count(logical=False))
    print("Total cores:", psutil.cpu_count(logical=True))
    # CPU frequencies

    try:
        cpufreq = psutil.cpu_freq()
        print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
        print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
        print(f"Current Frequency: {cpufreq.current:.2f}Mhz")
    except AttributeError:
        print("CPU Frequency is not supported")

    # CPU usage
    print("CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"Core {i}: {percentage}%")
    print(f"Total CPU Usage: {psutil.cpu_percent()}%")

    # Memory Information
    print("=" * 40, "Memory Information", "=" * 40)
    # get the memory details
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%")

    print("=" * 20, "SWAP", "=" * 20)
    # get the swap memory details (if exists)
    swap = psutil.swap_memory()
    print(f"Total: {get_size(swap.total)}")
    print(f"Free: {get_size(swap.free)}")
    print(f"Used: {get_size(swap.used)}")
    print(f"Percentage: {swap.percent}%")

    # Disk Information
    print("=" * 40, "Disk Information", "=" * 40)
    print("Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"=== Device: {partition.device} ===")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        print(f"  Total Size: {get_size(partition_usage.total)}")
        print(f"  Used: {get_size(partition_usage.used)}")
        print(f"  Free: {get_size(partition_usage.free)}")
        print(f"  Percentage: {partition_usage.percent}%")

    # Network information
    print("=" * 40, "Network Information", "=" * 40)
    # get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            print(f"=== Interface: {interface_name} ===")
            if str(address.family) == "AddressFamily.AF_INET":
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == "AddressFamily.AF_PACKET":
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast MAC: {address.broadcast}")
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")


# MINIMUM_SUBSCRIBERS_FOR_AUTOSUB = get_single_float_from_gist(
#     "0185d521be1a3f7198e1bce3a4215784", "msa.txt"
# )
# MINIMUM_VIEWS_FOR_AUTOSUB = get_single_float_from_gist(
#     "0185d521be1a3f7198e1bce3a4215784", "mva.txt"
# )

categories = [
    "sponsor",
    "selfpromo",
    "interaction",
    "intro",
    "outro",
    "preview",
    "music_offtopic",
    "filler",
    "poi_highlight",
    "exclusive_access",
]

ALL_SB_CAT = str(categories).replace("'", '"')

actionTypes = ["skip", "mute", "full", "poi"]

ALL_SB_ACTION_TYPES = str(actionTypes).replace("'", '"')


SB_HOST = "https://api.sponsor.ajay.app"

SB_HOST_1 = "https://sponsor.ajay.app"


def wait_for_time_between_1_and_specified_time(
    specified_time=TIME_TO_WAIT, start_time=1
):
    """waits for a time between 1 and specified time"""
    time_to_wait = random.randint(start_time, specified_time)
    print(f"Waiting for {time_to_wait} seconds")
    time.sleep(time_to_wait)


def execute(cmd):
    """Execute command and return output"""
    try:
        print(f"Executing {cmd}")
        with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as popen:
            for line in popen.stdout:
                print(line, end="")
        if popen.returncode != 0:
            print(f"{color.RED}Error: {popen.returncode} in the fn execute{color.END}")
            raise CalledProcessError(popen.returncode, popen.args)

        print(f"{color.GREEN}Successfully  executed {cmd}{color.END}")
    except Exception as error:  # pylint: disable=broad-except
        print(f"{color.RED}Error: {error}{color.END}")
        print(traceback.format_exc())


def install_requirements_for_recognition():
    """Install requirements for recognition"""
    execute(["sudo", "apt", "update", "-y"])
    # execute(["sudo", "apt", "upgrade", "-y"])
    execute(
        [
            "sudo",
            "apt",
            "install",
            "ffmpeg",
            "python3",
            "python3-dev",
            "curl",
            "git",
            "-y",
        ]
    )
    execute(["pip", "install", "--upgrade", "pip"])

    execute(["sudo", "apt", "autoremove", "-y"])
    execute(
        [
            "pip",
            "install",
            "git+https://github.com/BingLingGroup/autosub.git@dev",
            "ffmpeg-normalize",
            "langcodes",
        ]
    )
    execute(["pip", "install", "python-Levenshtein"])


def measure(func):
    """measures the time taken by a function"""

    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time.time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time.time() * 1000)) - start
            print(
                f"{color.BLUE}time: {max(end_, 0)} ms in {func.__name__} fn {color.END}"
            )

    return _time_it


def search(query):
    """searches for a query in the google search engine"""
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)


class color:  # pylint: disable=invalid-name
    """colors for printing"""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    DARK_CYAN = "\033[36m"
    DARK_PURPLE = "\033[35m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def id_generator(
    size=36, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase
):
    """Generates a random string of letters and digits of a given size
    with a given set of characters"""
    return "".join(random.choice(chars) for _ in range(size))


def segment_duration_from_start_and_end(
    start_of_segment_of_segment, end_of_segment_of_segment
):
    """returns the duration of a segment"""
    return end_of_segment_of_segment - start_of_segment_of_segment


def random_choice(user_ids):
    """returns a random user ID from a list of user IDs"""
    return random.choice(user_ids)


full_path = os.path.join(WORKING_DIRECTORY, "ci.txt")
with open(full_path, "r", encoding="utf-8") as file:
    all_channel_ids = file.read().splitlines()


for i in range(len(all_channel_ids)):
    channel_id = all_channel_ids[i]
    # if cid starts wth zhannel/ then replace it with nothing
    if channel_id.startswith("zhannel/"):
        channel_id = channel_id.replace("zhannel/", "")

    all_channel_ids[i] = channel_id


def get_all_auto_channel_ids():
    """returns all the channel IDs from the file"""

    all_auto_channel_ids = read_from_file("all_auto_channel_ids.txt")

    if all_auto_channel_ids is None:
        return []

    all_auto_channel_ids = all_auto_channel_ids.split("\n")

    all_auto_channel_ids = [x.split(",")[0] for x in all_auto_channel_ids]

    all_auto_channel_ids = [x for x in all_auto_channel_ids if x]

    all_auto_channel_ids = [x for x in all_auto_channel_ids if x != ""]

    all_auto_channel_ids = [x for x in all_auto_channel_ids if x.startswith("UC")]

    return all_auto_channel_ids


def write_video_id_in_cache(video_id, segment_type="auto"):
    """writes a video ID in the cache file"""
    filename = f"already_run_{segment_type}.txt"
    filename = f"already_run/{filename}"
    cwd = os.getcwd()
    filename = os.path.join(cwd, filename)

    append_to_file(filename, f"{video_id}\n")


def write_video_id_in_cache_file(video_id, segment_type="auto", channel_id=None):
    """writes a video ID in the cache    file"""

    if channel_id and channel_id in all_channel_ids:
        write_video_id_in_cache(video_id, segment_type)

    else:
        write_video_id_in_cache(video_id, "recent")


def user_ids_from_segment_type(segment_type="auto"):
    """returns a list of user IDs from a file"""
    filename = f"user_ids/ui_{segment_type}.txt"
    cwd = os.getcwd()
    filename = os.path.join(cwd, filename)
    with open(filename, "r", encoding="utf-8") as file:
        user_ids = file.read().splitlines()

    if len(user_ids) < 5000:
        user_ids = [id_generator() for _ in range(6400)]

    random.shuffle(user_ids)

    return user_ids[:2] + [id_generator() for _ in range(50)]


def end_of_video(duration):
    """
    returns the end of the video in seconds
    make sure to add a second to the duration and
    duration is divided by 10 until it is less than 0.10
    """
    original_duration = duration
    while duration > 0.10:
        duration = duration / 10
    duration = round(duration, 3)

    return original_duration + duration + 1


def yt_link_with_segments(video_id, silence_segments):
    """returns a YouTube link with segments"""
    json_data = quote(json.dumps(silence_segments))
    return f"https://www.youtube.com/watch?v={video_id}#segments={json_data}"


def difference_between_two_lists(list1, list2):
    """returns the difference between two lists with fastest way possible"""
    return list(set(list1) - set(list2))


def return_segment(
    start_of_segment, end_of_segment, category="sponsor", action_type="skip"
):
    """returns a segment in the format of a dictionary"""
    return {
        "segment": [start_of_segment, end_of_segment],
        "category": category,
        "actionType": action_type,
    }


def get_total_segment_time(segments):
    """returns the total time of the segments"""
    return sum(segment["segment"][1] - segment["segment"][0] for segment in segments)


def merge_segments(segments, max_time_difference=20):
    """merge the segments"""

    if segments == []:
        return []

    segments = sorted(segments, key=lambda x: x["segment"][0])

    i = 0
    while i < len(segments) - 1:
        time_difference_between_segments = (
            segments[i + 1]["segment"][0] - segments[i]["segment"][1]
        )

        if time_difference_between_segments < max_time_difference:
            if segments[i + 1]["segment"][1] > segments[i]["segment"][1]:
                segments[i]["segment"][1] = segments[i + 1]["segment"][1]
            segments.pop(i + 1)
        else:
            i += 1

    return segments


def return_de_duped_list(list_to_de_dupe):
    """Return list of de_duped items in given list."""
    de_duped_list = []
    for item in list_to_de_dupe:
        if item not in de_duped_list:
            de_duped_list.append(item)
    return de_duped_list


def process_responses(video_ids, category, action_type, responses):
    """Process responses for Intro , Outro , Midle and prints the results."""
    print(f"Processing responses for category: {category} action_type: {action_type}")
    with ThreadPoolExecutor(max_workers=100):
        for i, response in enumerate(responses):
            if response.ok:
                print(f"Successfully {action_type}ed video id: {video_ids[i]}")
                write_video_id_in_cache(video_ids[i], category)
            elif response.status_code in [409, 403]:
                print(f"Video id: {video_ids[i]} already {action_type}ed")
                write_video_id_in_cache(video_ids[i], category)
            else:
                print(f"Failed to {action_type} video id: {video_ids[i]}")
                print_status_and_text_from_response(response)


def return_current_file_location():
    """Return current file location."""
    return os.path.dirname(os.path.abspath(__file__))


def append_to_file(file_name, data):
    """Append data to file."""
    try:
        with open(file_name, "a", encoding="utf-8") as file:
            file.write(data)

    except FileNotFoundError:
        print(f"File {file_name} not found")
        write_to_file(file_name, data)

    except Exception as error:  # pylint: disable=broad-except
        print(f"Error in append_to_file: {error}")
        if "Disk quota exceeded" in str(error):
            print("Disk quota exceeded. Please delete some files from the disk")
            print(f"{error}")

            delete_unnecessary_files()

        else:
            time_to_sleep = random.random() * 2
            time.sleep(time_to_sleep)
            print(f"Sleeping for {time_to_sleep} seconds")

        append_to_file(file_name, data)


def delete_unnecessary_files():
    """Delete unnecessary files."""
    delete_all_files_in_directory("/tmp")

    delete_all_files_in_directory("audio")

    delete_all_files_in_directory("models")

    delete_all_files_in_directory("subtitles")

    delete_all_files_in_directory("video_info")

    # try to delete already_run/already_run_without_words.txt

    try:
        os.remove("already_run/already_run_without_words.txt")
    except FileNotFoundError:
        pass
    except Exception as error:  # pylint: disable=broad-except
        print(f"Error in delete_unnecessary_files: {error}")

    if "work" in os.getcwd():
        delete_all_files_in_directory("already_run")


def delete_all_files_in_directory(directory):
    """Delete all files in a directory."""
    try:
        print(f"deleting all files in {directory}")
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"Deleted file: {file_path}")
            except Exception as error:  # pylint: disable=broad-except
                print(f"Error in delete_all_files_in_directory: {error}")
        print(f"deleted all files in {directory}")
    except Exception as error:  # pylint: disable=broad-except
        print(f"Error in delete_all_files_in_directory: {error}")


def write_to_file(file_name, data):
    """Write data to file."""
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(data)
    except FileNotFoundError:
        print(f"File {file_name} not found")
        create_upper_directory(file_name)
        write_to_file(file_name, data)
    except Exception as error:  # pylint: disable=broad-except
        print(f"Error in write_to_file: {error}")
        time_to_sleep = random.random() * 3
        print(f"Sleeping for {time_to_sleep} seconds")
        time.sleep(time_to_sleep)
        write_to_file(file_name, data)


def create_upper_directory(file_name):
    """Create upper directory if it does not exist."""
    try:
        os.makedirs(os.path.dirname(file_name))
    except FileExistsError:
        print(f"Directory {os.path.dirname(file_name)} already exists")
    except Exception as error:  # pylint: disable=broad-except
        print(f"Error in create_upper_directory: {error}")
        print("retrying in 1 second")
        time.sleep(random.random() * 3)
        create_upper_directory(file_name)


def read_from_file(file_name):
    """Read data from file."""
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return _extracted_from_read_from_file_7(file_name)
    except Exception as error:  # pylint: disable=broad-except
        print(f"Error in read_from_file: {error}")
        print("retrying in 1 second")
        time.sleep(1)
        read_from_file(file_name)


# T ODO Rename this here and in `read_from_file`
def _extracted_from_read_from_file_7(file_name):
    with contextlib.suppress(Exception):
        print("got file not found error")
        folder_name = os.path.dirname(file_name)

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
    print(f"File {file_name} not found")
    write_to_file(file_name, "")


def sync_with_github():
    """Syncs with github"""
    try:
        subprocess.call(["git", "pull"])
    except Exception as error:  # pylint: disable=broad-except
        print(error)


def return_already_run_videos(segment_type="auto"):
    """Returns a list of all videos that have already been run."""
    filename = f"already_run/already_run_{segment_type}.txt"

    try:
        already_run_videos = read_from_file(filename).splitlines()
    except Exception as error:  # pylint: disable=broad-except
        print(f"Error in return_already_run_videos: {error}")
        already_run_videos = []

    return already_run_videos


def dummy_print(*args, **kwargs):
    """dummy print"""
    print(*args, **kwargs)


def is_english(string_to_check):
    """Check if the title is english."""

    # convert to lower case
    string_to_check = string_to_check.lower()

    if "in assamese" in string_to_check:
        print("it have assamese")
        return False

    elif "in bangla" in string_to_check:
        print("it have bangla")
        return False

    elif "in bengali" in string_to_check:
        print("it have bengali")
        return False

    elif "in bhojpuri" in string_to_check:
        print("it have bhojpuri")
        return False

    elif "in gujarati" in string_to_check:
        print("it have gujarati")
        return False

    elif "in kannada" in string_to_check:
        print("it have kannada")
        return False

    elif "in kashmiri" in string_to_check:
        print("it have kashmiri")
        return False

    elif "in konkani" in string_to_check:
        print("it have konkani")
        return False

    elif "in maithili" in string_to_check:
        print("it have maithili")
        return False

    elif "in malayalam" in string_to_check:
        print("it have malayalam")
        return False

    elif "in manipur" in string_to_check:
        print("it have manipur")
        return False

    elif "in marath" in string_to_check:
        print("it have marath")
        return False

    elif "in nepal" in string_to_check:
        print("it have nepal")
        return False

    elif "in oriya" in string_to_check:
        print("it have oriya")
        return False

    elif "in punjabi" in string_to_check:
        print("it have punjabi")
        return False

    elif "in sanskrit" in string_to_check:
        print("it have sanskrit")
        return False

    elif "in sindhi" in string_to_check:
        print("it have sindhi")
        return False

    elif "in sinhala" in string_to_check:
        print("it have sinhala")
        return False

    elif "in tamil" in string_to_check:
        print("it have tamil")
        return False

    elif "in telugu" in string_to_check:
        print("it have telugu")
        return False

    elif "in thai" in string_to_check:
        print("it have thai")
        return False

    elif "suicide squad" in string_to_check:
        print("it have suicide squad")
        return False

    elif "bgmi" in string_to_check:
        print("it have bgmi")
        return False

    elif "free fire" in string_to_check:
        print("it have free fire")
        return False

    elif "giveaway" in string_to_check:
        print("it have giveaway")
        return False

    elif "gold digger" in string_to_check:
        print("it have gold digger")
        return False

    elif "gta" in string_to_check:
        print("it have gta")
        return False

    elif "hijab" in string_to_check:
        print("it have hijab")
        return False

    elif "gaming" in string_to_check:
        print("it have gaming")
        return False

    elif "minecraft" in string_to_check:
        print("it have minecraft")
        return False

    elif "Telugu" in string_to_check:
        print("it have telugu")
        return False

    elif "Daily Current Affairs" in string_to_check:
        print("it have Daily Current Affairs")
        return False

    elif "iphone" in string_to_check:
        print("it have iphone")
        return False

    elif "ipad" in string_to_check:
        print("it have ipad")
        return False

    elif "ipod" in string_to_check:
        print("it have ipod")
        return False

    elif "AirPods" in string_to_check:
        print("it have AirPods")
        return False

    elif "Apple Watch" in string_to_check:
        print("it have Apple Watch")
        return False

    elif "apple" in string_to_check:
        print("it have apple")
        return False

    elif "google pixel" in string_to_check:
        print("it have Google Pixel")
        return False

    elif "ios" in string_to_check:
        print("it have ios")
        return False

    elif "moto" in string_to_check:
        print("it have Moto")
        return False

    elif "ios" in string_to_check:
        print("it have ios")
        return False

    elif "game" in string_to_check:
        print("it have game")
        return False

    elif "samsung" in string_to_check:
        print("it have Samsung")
        return False

    elif "world cup" in string_to_check:
        print("it have world cup")
        return False

    elif "t20" in string_to_check:
        print("it have t20")
        return False

    elif "iit" in string_to_check:
        print("it have iit")
        return False
    return True


if __name__ == "__main__":
    print(is_english("大树君 you"))
