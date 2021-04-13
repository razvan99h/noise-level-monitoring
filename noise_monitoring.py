import math
import sys
import threading
import time
import wave
from contextlib import contextmanager
from ctypes import *

import RPi.GPIO as GPIO
import pyaudio
from scipy.io.wavfile import read


# import matplotlib.pyplot as plt
# import numpy as np
# from scipy.io import wavfile


# def _plot_audio(wav_filename, show_time=1):
#     # debugging purposes only
#     sample_rate, data = wavfile.read(wav_filename)
#     length = data.shape[0] / sample_rate
#     time_spent = np.linspace(0., length, data.shape[0])
#     plt.plot(time_spent, data[:, 0], label="Left channel")
#     plt.plot(time_spent, data[:, 1], label="Right channel")
#     plt.legend()
#     plt.xlabel("Time [s]")
#     plt.ylabel("Amplitude")
#     plt.show()
#     time.sleep(show_time)
#     plt.close()

@contextmanager
def _no_alsa_err():
    # Function needed to suppress pyaudio warnings that appear on Raspberry Pi
    _ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

    def _py_error_handler(filename, line, function, err, fmt):
        pass

    _c_error_handler = _ERROR_HANDLER_FUNC(_py_error_handler)
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(_c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)


def _mean(array):
    # Computes the arithmetic mean of an array of numbers
    # needed because statistics from Python use int64 under the hood
    return sum(array) / len(array)


def record_audio(
        chunk=1024,
        audio_format=pyaudio.paInt16,
        channels=2,
        rate=44100):
    # Records an audio of record_seconds length and saves it
    with _no_alsa_err():
        p = pyaudio.PyAudio()
    stream = p.open(format=audio_format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("\n- recording...")

    frames = []
    for i in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    print("- done recording!")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(wav_output_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(audio_format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()


def mean_decibel_level():
    # Computes the mean decibel level found in the recorded audio
    _, wav_data = read(wav_output_file)
    mean_channels_squared = [_mean(part) ** 2 for part in wav_data]
    return int(20 * math.log10(math.sqrt(_mean(mean_channels_squared))))


def read_cmd_args():
    # Validates and reads the command line arguments
    # Arguments should consist of three numeric values:
    # recording_seconds, middle_decibel_level_threshold, upper_decibel_level_threshold
    global record_seconds
    global middle_decibel_level_threshold
    global upper_decibel_level_threshold
    if len(sys.argv) == 1:
        return
    if len(sys.argv) != 4:
        print("Invalid number of arguments"
              "\nArguments should be: recording_seconds, middle_decibel_level_threshold, upper_decibel_level_threshold"
              "\n\nPlease provide all three of them or none for default values")
        quit()
    for i in range(1, len(sys.argv)):
        try:
            x = float(sys.argv[i])
            if x < 0:
                raise ValueError
        except ValueError:
            print("Invalid arguments. Please provide positive numeric values")
            quit()
    record_seconds = float(sys.argv[1])
    middle_decibel_level_threshold = float(sys.argv[2])
    upper_decibel_level_threshold = float(sys.argv[3])


def setup():
    # Configures the GPIO pin setup, turns off all LEDs and starts a thread for listening to button clicks
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(green_led, GPIO.OUT)
    GPIO.setup(yellow_led, GPIO.OUT)
    GPIO.setup(red_led, GPIO.OUT)
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    turn_off_all()
    check_button_thread = threading.Thread(target=check_button_state)
    check_button_thread.start()


def check_button_state():
    # Thread function that checks for button presses for starting or stopping the application
    global turned_on
    while True:
        button_pressed = not GPIO.input(button)
        if button_pressed:
            if turned_on:
                print("\nTURNING OFF...\n")
                time.sleep(2)
                turn_off_all()
            else:
                print("\nTURNING ON...\n")
            turned_on = not turned_on
            time.sleep(2)


def turn_off_all():
    # Turn off all LEDs
    GPIO.output(green_led, GPIO.HIGH)
    GPIO.output(yellow_led, GPIO.HIGH)
    GPIO.output(red_led, GPIO.HIGH)


def turn_on_led(decibel_level):
    # Turns on the LED corresponding to the decibel level, and the other two LEDs off.
    # green LED for small level, yellow LED or medium level, red LED for high level
    # if the application is not started from the button, does nothing
    if not turned_on:
        return
    if decibel_level <= middle_decibel_level_threshold:
        GPIO.output(green_led, GPIO.LOW)
        GPIO.output(yellow_led, GPIO.HIGH)
        GPIO.output(red_led, GPIO.HIGH)
    elif middle_decibel_level_threshold < decibel_level <= upper_decibel_level_threshold:
        GPIO.output(green_led, GPIO.HIGH)
        GPIO.output(yellow_led, GPIO.LOW)
        GPIO.output(red_led, GPIO.HIGH)
    elif decibel_level > upper_decibel_level_threshold:
        GPIO.output(green_led, GPIO.HIGH)
        GPIO.output(yellow_led, GPIO.HIGH)
        GPIO.output(red_led, GPIO.LOW)


def run():
    # Main function
    read_cmd_args()
    setup()
    while True:
        if turned_on:
            record_audio()
            # _plot_audio()
            decibel_level = mean_decibel_level()
            print('  Mean dB value for recording: {0}'.format(decibel_level))
            turn_on_led(decibel_level)


green_led = 12
yellow_led = 10
red_led = 8
button = 16
turned_on = False

wav_output_file = 'output.wav'
record_seconds = 1
middle_decibel_level_threshold = 50
upper_decibel_level_threshold = 65

run()
