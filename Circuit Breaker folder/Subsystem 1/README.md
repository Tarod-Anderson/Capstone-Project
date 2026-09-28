# Subsystem 1 README

This folder contains the multisensing subsystem code for the project.

## Multisensing Folder

The `multisensing` folder contains code for compiling C code into a shared library and executing Python code that calls all three sensors.

### Compiling the Shared Library

To compile the C code into a shared library (`libdistance.so`), run:

gcc tof_lib.c \
    Platform/platform.c \
    VL53L7CX_ULD_API/src/vl53l7cx_api.c \
    VL53L7CX_ULD_API/src/vl53l7cx_plugin_detection_thresholds.c \
    VL53L7CX_ULD_API/src/vl53l7cx_plugin_motion_indicator.c \
    VL53L7CX_ULD_API/src/vl53l7cx_plugin_xtalk.c \
    -IPlatform \
    -IVL53L7CX_ULD_API/inc \
    -fPIC -shared \
    -o libdistance.so

### Executing the Python Pipeline

To execute the Python code that calls all three sensors:

sudo python3 main_pipeline.py



## TOF ASCII Program

The `tof_ascii_8x8.c` program provides an ASCII visualization of the Time-of-Flight sensor data.

### Compiling the TOF ASCII Program

To compile the TOF ASCII program:

gcc tof_ascii_8x8.c \
    tof_lib.c \
    Platform/platform.c \
    VL53L7CX_ULD_API/src/vl53l7cx_api.c \
    VL53L7CX_ULD_API/src/vl53l7cx_plugin_detection_thresholds.c \
    VL53L7CX_ULD_API/src/vl53l7cx_plugin_motion_indicator.c \
    VL53L7CX_ULD_API/src/vl53l7cx_plugin_xtalk.c \
    -IPlatform \
    -IVL53L7CX_ULD_API/inc \
    -lm \
    -o tof_ascii_8x8

### Running the TOF ASCII Program

To execute the compiled program:

sudo ./tof_ascii_8x8

### The other folder contains all other scripts I have wrote, these worked as the bare bones as I figured out how to interface all the sensors. 

