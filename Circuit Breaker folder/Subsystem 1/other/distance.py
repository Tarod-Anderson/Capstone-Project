import time
import board
import busio
import adafruit_mlx90640

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)  # warning about freq is OK

mlx = adafruit_mlx90640.MLX90640(i2c)

print("Found MLX90640 with serial:", [hex(i) for i in mlx.serial_number])

# Start with a modest refresh rate to reduce "Too many retries" errors
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ  # 2 frames per second

# Sensor is 24 rows x 32 columns = 768 pixels
HEIGHT = 24
WIDTH = 32
PIXELS = HEIGHT * WIDTH
frame = [0.0] * PIXELS

# --- Human detection tuning parameters ---
HUMAN_MIN_TEMP = 28.0   # °C - lower bound for "warm body" pixels
HUMAN_MAX_TEMP = 40.0   # °C - upper bound to ignore very hot objects
MIN_WARM_PIXELS = 20    # how many warm pixels needed to call it a human (tune this)

center_index = (HEIGHT // 2) * WIDTH + (WIDTH // 2)

while True:
    try:
        # Grab one full frame of temperatures
        mlx.getFrame(frame)

        # Basic stats
        max_temp = max(frame)
        min_temp = min(frame)
        avg_temp = sum(frame) / len(frame)

        # Count pixels in "human-ish" range
        warm_pixels = [
            t for t in frame
            if HUMAN_MIN_TEMP <= t <= HUMAN_MAX_TEMP
        ]
        warm_count = len(warm_pixels)

        # Simple decision rule
        human_detected = (
            warm_count >= MIN_WARM_PIXELS and
            HUMAN_MIN_TEMP <= max_temp <= HUMAN_MAX_TEMP
        )

        # Print some debug info
        print(
            f"Center: {frame[center_index]:5.2f} C | "
            f"Min: {min_temp:5.2f} C  Max: {max_temp:5.2f} C  Avg: {avg_temp:5.2f} C | "
            f"Warm pixels: {warm_count:3d} | "
            f"{'HUMAN DETECTED' if human_detected else 'no human'}"
        )

    except (RuntimeError, ValueError) as e:
        # MLX90640 sometimes glitches; just skip that frame
        print("Frame error:", e)
        time.sleep(0.2)
        continue

    # Slightly longer than 1 / 2 Hz = 0.5 s
    time.sleep(0.6)
