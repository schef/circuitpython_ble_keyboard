import supervisor
import usb_cdc
import storage
import time

# Give USB time to settle after cable insertion
time.sleep(0.5)
if hasattr(supervisor, "disable_autoreload"):
    supervisor.disable_autoreload()

if supervisor.runtime.usb_connected:
    print("[BOOT] USB connected")
    usb_cdc.enable(console=True, data=False)
else:
    print("[BOOT] USB not connected")
    #usb_cdc.disable()
    storage.disable_usb_drive()
