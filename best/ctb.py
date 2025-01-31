# Physical: {X=695,Y=668};
# Physical: {X=634,Y=823};

import pyautogui

from time import sleep


def main():
    pyautogui.moveTo(695, 668)
    pyautogui.click()

    pyautogui.moveTo(634, 823)
    pyautogui.click()
    pyautogui.hotkey("ctrl", "tab")


if __name__ == "__main__":

    sleep(5)

    for _ in range(10):
        main()
        sleep(1)
