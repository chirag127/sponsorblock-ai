"""
This module contains the main function that is called when the program is run.
"""

import os
import random
import subprocess
import sys

if "datasets" in os.getcwd() or "deepnote" in os.getcwd():
    WORKING_DIRECTORY = "/work"

elif "/kaggle/input/" in os.getcwd():
    WORKING_DIRECTORY = "/kaggle/working"

elif "/gdrive" in os.getcwd():
    WORKING_DIRECTORY = "/content"
else:
    WORKING_DIRECTORY = os.getcwd()


os.chdir(WORKING_DIRECTORY)

# install gitpython
try:
    import git

    print("gitpython already installed")
except ImportError:
    print("gitpython not installed")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gitpython"])
    import git

except Exception as error:  # pylint: disable=broad-except
    print(error)
    print("Error")


try:
    if os.path.isdir("Auto-sponsorblock-"):
        # delete the old folder
        subprocess.check_call(["rm", "-rf", "Auto-sponsorblock-"])
        print("Deleted old folder")

except Exception as error:  # pylint: disable=broad-except
    print(error)
    print("Error")


REPO_NAME = "Autosb"


# check if the repo is already cloned
if not os.path.isdir(REPO_NAME):
    # clone the repo
    GIT_URL = "https://chirag127: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@github.com/chirag127/Autosb.git"
    git.Repo.clone_from(GIT_URL, REPO_NAME)

# change the working directory to the repo
print("Changing working directory to the repo")
os.chdir(REPO_NAME)
print("Changed working directory to", os.getcwd())


# pull the latest changes
print("Pulling the latest changes")

try:
    repo = git.Repo()
    repo.remotes.origin.pull()

except Exception as error:  # pylint: disable=broad-except
    print(error)
    print("Error")
    # delete the old folder
    try:
        subprocess.check_call(["rm", "-rf", REPO_NAME])
        print("Deleted old folder")
    except Exception as main_error:  # pylint: disable=broad-except
        print(main_error)
        print("Error")

    # clone the repo


print("Pulled the latest changes")


# install the requirements
print("Installing the requirements")
try:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    )
except Exception as error:  # pylint: disable=broad-except
    print(error)
    print("Error")


# add the path to the repo to the system path
sys.path.append(os.getcwd())

from best import main  # pylint: disable=wrong-import-position # noqa: E402

if __name__ == "__main__":
    try:
        os.chdir(WORKING_DIRECTORY)
    except Exception as main_error:  # pylint: disable=broad-except
        print(main_error)
        print("Error")

    try:
        if "/work" in WORKING_DIRECTORY and "kaggle" not in WORKING_DIRECTORY:
            if random.random() > 0.9:
                for _ in range(1, 10000):
                    main()
            else:
                for _ in range(1, 10):
                    main()

        else:
            for _ in range(1, 100):
                main()
    except Exception as main_error:  # pylint: disable=broad-except
        print(main_error)
        print("Error")
