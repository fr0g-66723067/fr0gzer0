import logging
import ST7789
import time
from PIL import Image, ImageDraw

# Initialize logging and display
logging.basicConfig(level=logging.DEBUG)
disp = ST7789.ST7789()
disp.Init()
disp.clear()
disp.bl_DutyCycle(50)

# Menu structure
menu_items = [
    {"name": "Item 1", "action": "action1"},
    {"name": "Item 2", "action": "action2"},
    {"name": "Submenu", "submenu": [
        {"name": "Subitem 1", "action": "subaction1"},
        {"name": "Subitem 2", "action": "subaction2"}
    ]},
    {"name": "Item 3", "action": "action3"}
]

current_menu = menu_items
current_index = 0
menu_stack = []

def display_logo():
    image = Image.open('frog-logo-240x240.jpg')
    disp.ShowImage(image)
    time.sleep(3)

def display_menu():
    disp.clear()
    image = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image)
    for i, item in enumerate(current_menu):
        if i == current_index:
            draw.text((10, i*20), "> " + item["name"], fill="WHITE")
        else:
            draw.text((10, i*20), item["name"], fill="WHITE")
    disp.ShowImage(image)

def handle_input():
    global current_menu, current_index, menu_stack
    while True:
        if disp.digital_read(disp.GPIO_KEY_UP_PIN) == 0:
            current_index = (current_index - 1) % len(current_menu)
            display_menu()
            time.sleep(0.3)
        elif disp.digital_read(disp.GPIO_KEY_DOWN_PIN) == 0:
            current_index = (current_index + 1) % len(current_menu)
            display_menu()
            time.sleep(0.3)
        elif disp.digital_read(disp.GPIO_KEY_PRESS_PIN) == 0:  # Enter
            if "submenu" in current_menu[current_index]:
                menu_stack.append((current_menu, current_index))
                current_menu = current_menu[current_index]["submenu"]
                current_index = 0
                display_menu()
            else:
                print(f"Action: {current_menu[current_index]['action']}")
            time.sleep(0.3)
        elif disp.digital_read(disp.GPIO_KEY1_PIN) == 0:  # Back
            if menu_stack:
                current_menu, current_index = menu_stack.pop()
                display_menu()
            time.sleep(0.3)

# Display logo then show menu
display_logo()
display_menu()
handle_input()