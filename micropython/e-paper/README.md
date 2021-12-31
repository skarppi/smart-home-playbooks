# UI and driver for e-paper display

Standalone ESP32 e-paper display driver and UI for temperature sensor readings.

### E-paper driver

This repository contains driver for [Waveshare 3.7 inch e-paper display 18381](https://www.waveshare.com/3.7inch-e-paper.htm). 
The driver is originally copied from [Waveshare repository](https://github.com/waveshare/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd3in7.py) 
and adapted to Micropython running on [ESP32 driver board 15823](https://www.waveshare.com/e-Paper-ESP32-Driver-Board.htm). Some performance optimizations
were also done to improve refresh rate by sending data in one large bytearray instead of individual bytes.

It's quite easy to copy the changes over another display driver. The UI also needs changes since it's optimized for 280x480 pixels display supporting partial refresh.

### UI

Subscribes to MQTT topics and refresh display periodically.

![screenshot](https://github.com/skarppi/smart-home/raw/master/micropython/e-paper/screenshot.jpg "Screenshot")