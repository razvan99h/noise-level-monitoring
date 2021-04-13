# Noise Level Monitoring IoT Application

The Noise Level Monitoring IoT Application purpose is to provide users a visual status of the noise level present in a room. 

It is suitable for people concerned about noise levels in certain rooms (e.g.: managers in companies, parents), people with hearing disabilities or people wearing headphones. 

The visual feedback is provided directly by three LEDs (green, yellow and red) that turn on accordingly depending on the noise level in the room. The green LEDs stands for little noise, the yellow one for moderate noise, and the red one for loud noise.
The application can be turned on and off via a push button.

The IoT app is based on a Raspberry Pi 4 connected to a USB microphone for collecting decibel levels.

## Pictures

[(Watch demo video on YouTube)][demo-yt]

[demo-yt]: https://www.youtube.com/watch?v=O2gvVv_8YzE

![Demo](demo.gif?raw=true "Demo")
![Picture 1](p1.jpg?raw=true "Picture 1")
![Picture 2](p2.jpg?raw=true "Picture 2")
![Picture 3](p3.jpg?raw=true "Picture 3")

<sub><it>**Disclaimer*: no resistors can be seen in the photos, but they should be included in the project in order not to damage the components.<sub>

## Schematics

![Schematics](schematics.png?raw=true "Schematics")


## Pre-requisites

- Raspberry Pi 3 or 4
- USB microphone (or a USB headset with a microphone)
- The following individual components:
  - 1 breadboard
  - jumper wires
  - 1 push button
  - 4 resistors (0.22-1 kΩ)
  - 3 LEDs (green, yellow, red)
    
## Running the application

To run the application, follow these steps below:

- Connect the push button and the three LEDs to the GPIO pins according to the presented schematics
- Connect the USB microphone and the power source to the Raspberry Pi
- Find the Raspberry Pi IP address on your local network and connect to it via ssh (e.g.: **`ssh pi@192.168.100.92`**)
- Clone this repository locally on the Raspberry Pi
- Make sure Python 3 is installed (run **`python3 --version`**) on the Raspberry Py. If not, install it via **`sudo apt-get install python3`**
- Make sure pip is installed (run **`pip --version`**) on the Raspberry Py. If not, install it via **`sudo apt-get install python-pip`**
- Install the following packages via pip (**`pip install package_name`): pyaudio, scipy
- Once everything is installed, navigate to the folder in which the **`noise_monitoring.py`** file is found
- Run the command **`python3 noise_monitoring.py`**
- Push the physical button to start monitoring!

Additionally, you can:
- Adjust the duration for which the application performs a recording to evaluate the noise level, the middle and upper noise level threshold 
  from the command line by specifying the corresponding numeric values in the command line (e.g.: **`python3 noise_monitoring.py 1 30 50`**)   
- Make the application run at the start-up of the Raspberry Pi by adding the following line to the end of the **`/etc/rc.local`** file: **`python3 noise_monitoring.py`**
