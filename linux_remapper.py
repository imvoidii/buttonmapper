import sys
from evdev import InputDevice, categorize, ecodes, UInput

# 1. CHANGE THIS to match your actual keyboard device path
# You can find your keyboard path by running 'ls -l /dev/input/by-id/'
KEYBOARD_PATH = '/dev/input/event3'

# 2. Define your key mappings {ORIGINAL_KEY: NEW_KEY}
# Refer to evdev's ecodes for exact key names (e.g., ecodes.KEY_A)
KEY_MAP = {
    ecodes.KEY_CAPSLOCK: ecodes.KEY_ESC,  # Remap CapsLock to Escape
    ecodes.KEY_A: ecodes.KEY_Z,           # Remap A to Z
    ecodes.KEY_Z: ecodes.KEY_A,           # Remap Z to A
}

def main():
    try:
        # Connect to your physical keyboard
        keyboard = InputDevice(KEYBOARD_PATH)

        # Grab exclusive control so the system doesn't receive duplicate key presses
        keyboard.grab()

        # Create a virtual keyboard to send the remapped keys
        # We clone the capabilities of the physical keyboard so it supports all events
        with UInput.from_device(keyboard, name="Virtual-Remapped-Keyboard") as vdev:
            print(f"Successfully remapping {keyboard.name}. Press Ctrl+C in terminal to stop.")

            # Loop through hardware key events continuously
            for event in keyboard.read_loop():
                if event.type == ecodes.EV_KEY:
                    data = categorize(event)

                    # Check if the pressed key is in our mapping dictionary
                    if data.scancode in KEY_MAP:
                        new_scancode = KEY_MAP[data.scancode]
                        # Send the remapped key with the original state (0=up, 1=down, 2=hold)
                        vdev.write(ecodes.EV_KEY, new_scancode, event.value)
                        vdev.syn()
                    else:
                        # Forward all other keys completely untouched
                        vdev.write(ecodes.EV_KEY, event.code, event.value)
                        vdev.syn()

    except PermissionError:
        print("Error: You must run this script with root privileges (sudo).")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Device not found at {KEYBOARD_PATH}. Check your path.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting and releasing keyboard.")

if __name__ == "__main__":
    main()
