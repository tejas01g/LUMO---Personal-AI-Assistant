import datetime

from config import SCREENSHOT_DIR


def get_time() -> str:
    return datetime.datetime.now().strftime("%A, %d %B %Y, %I:%M %p")


def take_screenshot() -> str:
    from PIL import ImageGrab

    name = f"screenshot_{datetime.datetime.now():%Y%m%d_%H%M%S}.png"
    path = SCREENSHOT_DIR / name
    ImageGrab.grab().save(path)
    return f"Screenshot saved: {path}"


def battery_status() -> str:
    import psutil

    b = psutil.sensors_battery()
    if b is None:
        return "Battery ki info nahi mili."
    state = "charging" if b.power_plugged else "charging nahi ho rahi"
    return f"Battery {round(b.percent)}% hai, {state}."


def set_volume(action: str, steps: int = 5) -> str:
    import pyautogui

    action = action.strip().lower()
    steps = max(1, min(int(steps), 25))   # har step lagbhag 2% volume
    if action in ("up", "increase"):
        pyautogui.press("volumeup", presses=steps)
        return f"Volume badha diya ({steps} steps)."
    if action in ("down", "decrease"):
        pyautogui.press("volumedown", presses=steps)
        return f"Volume kam kar diya ({steps} steps)."
    if action == "mute":
        pyautogui.press("volumemute")
        return "Volume mute/unmute toggle kar diya."
    return "action 'up', 'down' ya 'mute' hona chahiye."


def set_brightness(level: int) -> str:
    import screen_brightness_control as sbc

    level = max(0, min(int(level), 100))
    sbc.set_brightness(level)
    return f"Brightness {level}% kar di."