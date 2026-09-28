/*******************************************************************************
* VL53L7CX Continuous Ranging Example (2 Hz + Average Distance)
*******************************************************************************/

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <math.h>

#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>

#include "vl53l7cx_api.h"
#include "platform.h"

int example1(VL53L7CX_Configuration *pDev)
{
    uint8_t status, isAlive, isReady, i;
    VL53L7CX_ResultsData Results;

    printf("Checking if VL53L7CX is alive...\n");

    status = vl53l7cx_is_alive(pDev, &isAlive);
    if(!isAlive || status)
    {
        printf("VL53L7CX not detected at address 0x%02X\n",
               pDev->platform.address);
        return status ? status : 255;
    }

    /* Initialize sensor */
    status = vl53l7cx_init(pDev);
    if(status)
    {
        printf("VL53L7CX ULD init failed (status=%u)\n", status);
        return status;
    }

    printf("VL53L7CX ULD ready! (version %s)\n", VL53L7CX_API_REVISION);

    /* Set frequency = 2 Hz */
    status = vl53l7cx_set_ranging_frequency_hz(pDev, 2);
    if(status)
    {
        printf("Failed to set 2 Hz ranging (status=%u)\n", status);
        return status;
    }
    printf("Ranging frequency set to 2 Hz\n");

    /* Start ranging */
    printf("Starting ranging... (Ctrl+C to stop)\n");
    status = vl53l7cx_start_ranging(pDev);
    if(status)
    {
        printf("Start ranging failed (status=%u)\n", status);
        return status;
    }

    /*********************************/
    /*   INFINITE LOOP STARTS HERE   */
    /*********************************/

    while(1)
    {
        status = vl53l7cx_check_data_ready(pDev, &isReady);
        if(status)
        {
            printf("check_data_ready error (status=%u)\n", status);
            break;
        }

        if(isReady)
        {
            vl53l7cx_get_ranging_data(pDev, &Results);

            uint32_t sum_mm = 0;
            uint8_t valid = 0;

            /* 4x4 -> 16 zones */
            for(i = 0; i < 16; i++)
            {
                uint8_t idx = VL53L7CX_NB_TARGET_PER_ZONE * i;
                uint8_t zone_status = Results.target_status[idx];
                int16_t dist_mm     = Results.distance_mm[idx];

                if(zone_status != 255 && dist_mm > 0)
                {
                    sum_mm += dist_mm;
                    valid++;
                }
            }

            if(valid > 0)
            {
                double avg = (double)sum_mm / valid;
                printf("Frame %3u | Avg distance = %.1f mm | Valid zones = %u\n",
                       pDev->streamcount, avg, valid);
            }
            else
            {
                printf("Frame %3u | No valid targets\n", pDev->streamcount);
            }
        }

        /* Poll every ~5 ms */
        VL53L7CX_WaitMs(&(pDev->platform), 5);
    }

    /* If loop breaks, stop cleanly */
    vl53l7cx_stop_ranging(pDev);
    printf("Stopped ranging.\n");

    return 0;
}


/*********************************/
/*   MAIN FUNCTION (Raspberry Pi) */
/*********************************/

int main(void)
{
    VL53L7CX_Configuration Dev;

    memset(&Dev, 0, sizeof(Dev));

    printf("Opening I2C bus /dev/i2c-1...\n");

    Dev.platform.i2c_fd = open("/dev/i2c-1", O_RDWR);
    if(Dev.platform.i2c_fd < 0)
    {
        perror("Failed to open /dev/i2c-1");
        return -1;
    }

    Dev.platform.address = 0x29;

    if(ioctl(Dev.platform.i2c_fd, I2C_SLAVE, Dev.platform.address) < 0)
    {
        perror("Failed to set I2C slave address");
        close(Dev.platform.i2c_fd);
        return -1;
    }

    printf("I2C ready (7-bit address 0x%02X)\n\n", Dev.platform.address);

    int status = example1(&Dev);

    close(Dev.platform.i2c_fd);

    printf("Program exited with status = %d\n", status);
    return status;
}
