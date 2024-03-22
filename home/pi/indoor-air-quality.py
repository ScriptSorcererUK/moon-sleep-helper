#!/usr/bin/env python

# from https://github.com/pimoroni/bme680-python?tab=readme-ov-file

import subprocess
import time
import RPi.GPIO as GPIO
import bme680
import time

print("""indoor-air-quality.py - Estimates indoor air quality.

Runs the sensor for a burn-in period, then uses a
combination of relative humidity and gas resistance
to estimate indoor air quality as a percentage.

Press Ctrl+C to exit!

""")

# Show a happy face so we know the program has started
# from https://docs.python.org/3.5/library/subprocess.html#subprocess.run
subprocess.run(['python LCD.py face.jpg'], shell=True)

# Tell the Pi to listen for button presses on these pins
# from http://razzpisampler.oreilly.com/ch07.html
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except (RuntimeError, IOError):
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# start_time and curr_time ensure that the
# burn_in_time (in seconds) is kept track of.

start_time = time.time()
curr_time = time.time()
burn_in_time = 60

burn_in_data = []

try:
    # Collect gas resistance burn-in values, then use the average
    # of the last 50 values to set the upper limit for calculating
    # gas_baseline.
    print('Collecting gas resistance burn-in data for 1 min\n')
    while curr_time - start_time < burn_in_time:
        curr_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            burn_in_data.append(gas)
            print('Gas: {0} Ohms'.format(gas))
            time.sleep(1)

    gas_baseline = sum(burn_in_data[-50:]) / 50.0

    # Set the humidity baseline to 40%, an optimal indoor humidity.
    hum_baseline = 40.0

    # This sets the balance between humidity and gas reading in the
    # calculation of air_quality_score (25:75, humidity:gas)
    hum_weighting = 0.25

    print('Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n'.format(
        gas_baseline,
        hum_baseline))

    # Show a happy face so we know the initial testing has finished
    subprocess.run(['python LCD.py face.jpg'], shell=True)

    # repeat forever listening for button presses
    while True:
        #see if the left button was pressed
        left = GPIO.input(16)
        if left == False:
            print("Left pressed")
            # plays the sound file through the speaker (waits until it has finished)
            # sound file from https://www.partnersinrhyme.com/soundfx/watersounds.shtml
            subprocess.run(['aplay beach3.wav'], shell=True)
            time.sleep(1)
            print("Done")
            #then go back to listening for button presses again

        #see if the right button was pressed
        right = GPIO.input(20)
        if right == False:
            print("Right pressed")
            #collect data from the sensor
            if sensor.get_sensor_data() and sensor.data.heat_stable:
                gas = sensor.data.gas_resistance
                gas_offset = gas_baseline - gas

                hum = sensor.data.humidity
                hum_offset = hum - hum_baseline

                # Calculate hum_score as the distance from the hum_baseline.
                if hum_offset > 0:
                    hum_score = (100 - hum_baseline - hum_offset)
                    hum_score /= (100 - hum_baseline)
                    hum_score *= (hum_weighting * 100)

                else:
                    hum_score = (hum_baseline + hum_offset)
                    hum_score /= hum_baseline
                    hum_score *= (hum_weighting * 100)

                # Calculate gas_score as the distance from the gas_baseline.
                if gas_offset > 0:
                    gas_score = (gas / gas_baseline)
                    gas_score *= (100 - (hum_weighting * 100))

                else:
                    gas_score = 100 - (hum_weighting * 100)

                # Calculate air_quality_score.
                air_quality_score = hum_score + gas_score

                print('Gas: {0:.2f} Ohms,humidity: {1:.2f} %RH,air quality: {2:.2f}'.format(
                    gas,
                    hum,
                    air_quality_score))

                time.sleep(1)
                #simple comparison if the air quality is bad or not
                #simple as this is just a prototype. The future version would collect data from the last 10-12 hours and store it all
                if air_quality_score > 90:
                    #show the thumbs up image if the air is good
                    subprocess.run(['python LCD.py goodair.jpg'], shell=True)
                else:
                    #show the thumbs down image if the air is bad
                    subprocess.run(['python LCD.py badair.jpg'], shell=True)
                print("Done")

                #then go back to listening for button presses again
except:
    pass
