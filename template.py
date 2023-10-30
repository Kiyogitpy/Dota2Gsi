import cv2
import numpy as np
import pyautogui

# Reduced resolution template
template = cv2.imread('Images/template.png', cv2.IMREAD_GRAYSCALE)
template = cv2.resize(template, (0,0), fx=0.5, fy=0.5)  # Reduce the resolution by half

def capture_screen(region=None):
    screenshot = pyautogui.screenshot(region=region)
    screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    # Reduce the resolution of the screen capture
    screen = cv2.resize(screen, (0,0), fx=0.5, fy=0.5)
    return screen

def find_template_on_screen(threshold=0.8):
    screen = capture_screen(region=(135, 950, 130, 90))
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if loc[0].size:
        return True
    return False
