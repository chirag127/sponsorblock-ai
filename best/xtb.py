# Physical: {X=640,Y=473}
# Physical: {X=609,Y=632}

import pyautogui

from time import sleep


def main():
    pyautogui.moveTo(640, 473)
    pyautogui.click()

    pyautogui.moveTo(609, 632)
    pyautogui.click()
    pyautogui.hotkey("ctrl", "tab")


if __name__ == "__main__":

    sleep(5)

    for _ in range(10):
        main()
        sleep(1)
