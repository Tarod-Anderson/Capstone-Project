from picamera2 import Picamera2
import time
import os

def main():
    # Make an output folder
    output_dir = "Images"
    os.makedirs(output_dir, exist_ok=True)

    # How many photos and how fast?
    num_photos = 15 # total photos to take
    fps = 3 # photos per second
    interval = 1.0 / fps

    picam2 = Picamera2()

    # Choose a mode (lower resolution = faster)
    config = picam2.create_still_configuration(
        main={"size": (1280, 720)}  # you can change this
    )
    picam2.configure(config)

    picam2.start()
    time.sleep(1)  # let the camera warm up

    print(f"Starting capture: {num_photos} photos at ~{fps} FPS")
    start_time = time.time()

    for i in range(num_photos):
        t0 = time.time()
        filename = os.path.join(output_dir, f"frame_{i:04d}.jpg")
        picam2.capture_file(filename)
        print(f"Captured {filename}")

        # Keep roughly consistent timing
        elapsed = time.time() - t0
        sleep_time = interval - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

    total_time = time.time() - start_time
    print(f"Done. Captured {num_photos} frames in {total_time:.2f} seconds.")

    picam2.stop()

if __name__ == "__main__":
    main()
