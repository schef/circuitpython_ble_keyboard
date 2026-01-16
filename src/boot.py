import time
import supervisor

# Give USB time to settle after cable insertion
time.sleep(0.5)

# Optional: disable autoreload for stability
supervisor.disable_autoreload()
