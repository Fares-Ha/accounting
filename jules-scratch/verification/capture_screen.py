import mss
import mss.tools

def capture_screenshot(filename="screenshot.png"):
    with mss.mss() as sct:
        # Get information of monitor 1
        monitor_number = 1
        mon = sct.monitors[monitor_number]

        # The screen part to capture
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"],
            "mon": monitor_number,
        }

        # Grab the data
        sct_img = sct.grab(monitor)

        # Save to the picture file
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
        print(f"Screenshot saved to {filename}")

if __name__ == "__main__":
    capture_screenshot("jules-scratch/verification/verification.png")