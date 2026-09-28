from rpicam import Picamera2
from rpicam.encoders import H264Encoder
from rpicam.outputs import FileOutput
import time

def record_video(duration, fps):
    """
    Record a video in MP4 format.
    
    Parameters:
    duration (float): Duration of the video in seconds
    fps (int): Frames per second for the video recording
    """
    picam2 = Picamera2()

    # Video configuration
    video_config = picam2.create_video_configuration(
        main={"size": (1280, 720)},   # 720p
        controls={"FrameRate": fps}   # Use provided FPS
    )
    picam2.configure(video_config)

    encoder = H264Encoder(bitrate=2_000_000)  # 2 Mbps is fine for 720p @ low FPS
    output = FileOutput("output.mp4")

    print(f"Starting recording for {duration} seconds at {fps} FPS...")
    picam2.start_recording(encoder, output)

    # Record for the specified duration
    time.sleep(duration)

    print("Stopping...")
    picam2.stop_recording()
    picam2.close()
    print("Recording complete!")

if __name__ == "__main__":
    record_video(5, 3)
