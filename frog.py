import logging
import ST7789
import time
from PIL import Image, ImageDraw, ImageFont

# Initialize logging and display
logging.basicConfig(level=logging.DEBUG)
disp = ST7789.ST7789()
disp.Init()
disp.clear()
disp.bl_DutyCycle(50)


def display_logo():
    image = Image.open('frog-logo-240x240.jpg')
    disp.ShowImage(image)
    time.sleep(3)


# Menu structure
menu_items = [
    {"name": "Item 1", "action": "action1"},
    {"name": "Show Image", "action": display_logo},  # Reference to the function
    {"name": "Submenu", "submenu": [
        {"name": "Subitem 1", "action": "subaction1"},
        {"name": "Subitem 2", "action": "subaction2"}
    ]},
    {"name": "Item 3", "action": "action3"}
]

current_menu = menu_items
current_index = 0
menu_stack = []


def display_menu():
    disp.clear()
    image = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype("Font/Font02.ttf", 36)
    text_color = (0, 255, 0)  # Green color in RGB

    # Calculate the height of the text with the current font size
    text_height = font.getsize("Test")[1] + 10  # Adding 10 pixels as margin

    for i, item in enumerate(current_menu):
        y_position = i * text_height  # Calculate the y position based on the text height
        if i == current_index:
            draw.text((10, y_position), "> " + item["name"], fill=text_color, font=font)
        else:
            draw.text((10, y_position), item["name"], fill=text_color, font=font)
    disp.ShowImage(image)


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
        time.sleep(0.1)  # Small delay to prevent high CPU usage


# Display logo then show menu
display_logo()
display_menu()
handle_input()