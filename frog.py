import csv
import logging
import ST7789
import time
import subprocess
import os

from PIL import Image, ImageDraw, ImageFont

# Initialize logging and display
logging.basicConfig(level=logging.DEBUG)
disp = ST7789.ST7789()
disp.Init()
disp.clear()
disp.bl_DutyCycle(5)

# Global variable to hold the airodump-ng process
airodump_process = None
angryoxide_process = None
display_state = True


def display_logo():
    image = Image.open('frog-logo-240x240.jpg')
    disp.ShowImage(image)
    time.sleep(3)


def start_airodump():
    global airodump_process
    # Ensure no previous instance is running
    if airodump_process is not None:
        print("Airodump-ng is already running.")
        return
    # Start airodump-ng with output directed to a log file in JSON format
    command = ["sudo", "airodump-ng", "-i", "wlan1", "--write-interval", "1", "--output-format", "csv", "-w",
               "/home/user/airodump_output/fr0gzer0"]
    airodump_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print("Airodump-ng started.")


def stop_airodump():
    global airodump_process
    if airodump_process is None:
        print("Airodump-ng is not running.")
        return
    # Terminate the process
    airodump_process.terminate()
    airodump_process = None
    print("Airodump-ng stopped.")


def start_angryoxide_2():
    start_angryoxide(2)


def start_angryoxide_5():
    start_angryoxide(5)


def start_angryoxide(ghz):
    global angryoxide_process
    # Ensure no previous instance is running
    if angryoxide_process is not None:
        print("angryoxide is already running.")
        return
    command = ["sudo", "angryoxide", "--interface", "wlan1", f"-b {ghz}", "--output",
               "/home/user/angryoxide_output/fr0gzer0"]
    angryoxide_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print("angryoxide started.")


def stop_angryoxide():
    global angryoxide_process
    if angryoxide_process is None:
        print("angryoxide is not running.")
        return
    # Terminate the process
    angryoxide_process.terminate()
    angryoxide_process = None
    print("angryoxide stopped.")


# Modify the existing display_menu function to support scrolling and displaying long lists
def display_menu():
    disp.clear()
    image = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype("Font/Font02.ttf", 36)
    text_color = (0, 255, 0)  # White color

    # Calculate the number of items that can fit on the screen
    max_items = disp.height // (font.getsize("Test")[1] + 10)  # Adjust spacing based on font size
    start_index = max(0, current_index - max_items + 1)
    end_index = min(len(current_menu), start_index + max_items)

    for i, item in enumerate(current_menu[start_index:end_index], start=start_index):
        y_position = (i - start_index) * (font.getsize("Test")[1] + 10)  # Adjust spacing based on font size
        if i == current_index:
            draw.text((10, y_position), "> " + item["name"], fill=text_color, font=font)
        else:
            draw.text((10, y_position), item["name"], fill=text_color, font=font)

    disp.ShowImage(image)


def toggle_display():
    global display_state
    display_state = not display_state
    if display_state:
        disp.bl_DutyCycle(5)
        display_state = True
        display_menu()
    else:
        disp.bl_DutyCycle(0)
        display_state = False


menu_items = [
    {"name": "recon", "submenu": [
        {"name": "wifi", "submenu": [
            {"name": "airodump", "submenu": [
                {"name": "start", "action": start_airodump},
                {"name": "stop", "action": stop_airodump}
            ]}
        ]}
    ]},
    {"name": "attack", "submenu": [
        {"name": "wifi", "submenu": [
            {"name": "angryoxide-2ghz", "submenu": [
                {"name": "start", "action": start_angryoxide_2},
                {"name": "stop", "action": stop_angryoxide}
            ]},
            {"name": "angryoxide-5ghz", "submenu": [
                {"name": "start", "action": start_angryoxide_5},
                {"name": "stop", "action": stop_angryoxide}
            ]}
        ]}
    ]},
    {"name": "Show logo", "action": display_logo},
]

current_menu = menu_items
current_index = 0
menu_stack = []


def handle_input():
    global current_menu, current_index, menu_stack
    last_press_time = time.time()
    debounce_time = 0.3  # Adjust this value as needed

    while True:
        now = time.time()
        if disp.digital_read(disp.GPIO_KEY_UP_PIN) != 0 and (now - last_press_time) > debounce_time:
            current_index = (current_index - 1) % len(current_menu)
            display_menu()
            last_press_time = now
        elif disp.digital_read(disp.GPIO_KEY_DOWN_PIN) != 0 and (now - last_press_time) > debounce_time:
            current_index = (current_index + 1) % len(current_menu)
            display_menu()
            last_press_time = now
        elif disp.digital_read(disp.GPIO_KEY_PRESS_PIN) != 0 and (now - last_press_time) > debounce_time:  # Enter
            if "submenu" in current_menu[current_index]:
                menu_stack.append((current_menu, current_index))
                current_menu = current_menu[current_index]["submenu"]
                current_index = 0
                display_menu()
            elif callable(current_menu[current_index].get("action")):  # Check if action is callable
                current_menu[current_index]["action"]()  # Execute the function
            last_press_time = now
        elif disp.digital_read(disp.GPIO_KEY1_PIN) != 0 and (now - last_press_time) > debounce_time:  # Back
            if menu_stack:
                current_menu, current_index = menu_stack.pop()
                display_menu()
            last_press_time = now
        elif disp.digital_read(disp.GPIO_KEY3_PIN) != 0 and (now - last_press_time) > debounce_time:
            toggle_display()
            last_press_time = now
        time.sleep(0.1)  # Small delay to prevent high CPU usage


# Display logo then show menu
display_logo()
display_menu()
handle_input()
