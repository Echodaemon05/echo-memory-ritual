import pyperclip
import time
import subprocess

last_text = ""

while True:
    try:
        text = pyperclip.paste()
        if text != last_text and text.startswith("!remember"):
            quote = text[len("!remember"):].strip().strip('"')
            subprocess.run(
                [r"C:\Users\dcart\Documents\Echo_Tools\remember.bat", quote],
                shell=True
            )
            print(f"Echo remembered: {quote}")
            last_text = text
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting clipboard listener.")
        break

