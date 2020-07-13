# ChatterPi
Flexible Audio Servo Controller using Raspberry Pi (for talking skulls, etc.)
Mike McGurrin

Developed on a Raspberry Pi Model 3 A+ and tested on the 3 A+ and a Pi Zero W. Given that it runs on a Pi Zero, I believe it will run on any Pi. The orgiginal version had a code section in the audio processing that ran too slowly for the Pi Zero, but the loop and list processing has been replaced with using a numpy array and it now works on the Zero.

# Introduction

ChatterPi is a software package that turns a Raspberry Pi into an audio servo controller. In other words, the Pi outputs commands to control a servo based on the volume of the audio input. The input can be either stored audio files (in either mono or stereo .wav format) or from an external source, such as a microphone or line level input. One of the uses is to drive animatronic props, such as a skull or a talking bird.

See the documentation for additional information.

# Background: A Brief History of Talking Skull Control

A common prop that still makes a good impact is a talking object, whether a skull or animal. Some lower cost commercial props use a motor and spring. Another approach is to pre-program a complete sequence to match the vocals, but this is very time consuming and if you want to change the vocals, or even just edit them slightly, you need to reprogram the entire sequence. For that reason, the use of an audio servo controller to drive a servomotor controlling the jaw is a very popular approach. There are several variations. One of the earliest use hardware to detect when the audio exceeded a threshold, and then began moving the jaw towards a fully open position, and when the audio went below the threshold, it would begin closing the jaw. &quot;Scary Terry&quot; Simmons may have been the first to develop an [electronic hardware board](http://www.scary-terry.com/audioservo/audioservo.htm) to do this, and [Cowlacious Designs](https://www.cowlacious.com/categories/Scary-Terry-Audio-Servo-Driver/) has continued to improve and sell commercial versions, with many added features such as a built in audio player, various triggering options, and the ability to control LEDs as eyes.

Later, someone named Mike (no relation) combined an Arduino with a hardware volume level board to produce the [Jawduino](http://buttonbanger.com/?page_id=137). This went from having just 2 levels to 4. The original project just took audio in and controlled the servo, but others added extensions to play stored mp3 files and/or randomly move additional servos (for example, [http://batbuddy.org/resources/Halloweenstuff/TalkingSkull.php](http://batbuddy.org/resources/Halloweenstuff/TalkingSkull.php)).

A few years ago, Steve Bjork from Haunt Hackers combined dedicated hardware with a propeller microcontroller to increase the number of levels to almost 256 and also to filter out low and high frequencies that don&#39;t tend to result in jaw movement for spoken sound. The result is the [Wee Little Talker](http://www.haunthackers.com/weelittletalker/index.shtml). This commercial board also has an onboard mp3 player, can be triggered externally, control LED &#39;eyes,&quot; and adds a wide array of features including a voice feedback menu system.

It occurred to me that with current single board computer capabilities and powerful software libraries, it should be possible to incorporate most of the best features of all of these into a single, software-based system running on a Raspberry Pi. The result is ChatterPi. ChatterPi was developed from scratch using the Python language, but ideas for capabilities and features were freely borrowed from previous audio servo controller projects.

# Features
ChaterPi includes the following features

- Audio signal volume controls servo
- Can be started by an external trigger, such as a PIR motion detector
- Can be set to start periodically via an internal timer
- Audio can be from wav files or external input
- Can send an output trigger to start another device when it is triggered
- Output to light LED "eyes" (e.g., for a skull)

Additional features are planned. 

# Software Overview

Knowledge or understanding of the software code is not required to operate or use the ChatterPi. Those who are not interested can skip this section of the documentation.

The ChatterPi package consists of four Python 3 modules and one configuration file.

The configuration file, config.ini, holds all of the user selectable parameters, including which pins are used for which functions, whether the audio source is the microphone input or stored .wav files, which servo control mode should be used, and the servo threshold levels. The config.py program simply reads these values and makes them available in memory during runtime.

Most of the processing occurs in the main.py and audio.py modules. The main.py program handles triggering (either my time, an external trigger such as a PIR, or immediately upon startup, with the method specified in the config.ini file. It uses the GPIO Zero and PiGPIO libraries to monitor the triggering sensor and send output to the output trigger and led pins. PiGPIO is used as the GPIO layer underneath GPIO Zero because it uses DMA control for the Pulse Width Modulation (PWM) control used to the control the servo. Some other libraries, including the default one used by GPIO Zero, use software PWM, which is adequate for tasks such as controlling the brightness of LEDs, but not precise enough for servo control.

Unless the triggering mode is START, the file enters an infinite loop waiting for either a timer to expire (TIMER mode) or the external trigger to be generated (PIR mode). The wait functions meet the requirements and during development, interrupt driven approaches interfered with the audio output, probably due to timing conflicts. In TIMER mode, the timer is restarted after either the audio file finishes playing (if the source is FILES) or after a configurable pre-set time (if the source is MICROPHONE).

When triggered, an event handler is called that, depending upon the settings, sets off the TRIGGER\_OUT to trigger another prop or device and turns on the LED eyes or other low power device. Then, if the audio source is FILES, it will select the next .wav file to be played and call audio.py, passing the name of the .wav file to be played. If the audio source is MICROPHONE, audio.py is called without passing a file name. When the call to audio.py returns, the event handler turns the LED eyes off and returns.

Audio playback, audio analysis, and servo control are all performed by the audio.py module. It defines one class, AUDIO. When the audio.play function is called, it checks on whether the audio source is MICROPHONE or FILES and opens a PyAudio stream appropriately. The stream call runs in a separate thread (this is automatically handled by PyAudio). For each chunk of the input stream, a callback function is called. This callback function is where the audio stream volume is analyzed. The average volume for each chunk is calculated, and the servo is commanded to the appropriate position based on that average volume and the threshold levels that the user has specified in the config file. The wave library is used to read the wave files from storage, and the struct library is used to help deconstruct the wave data to calculate volume and to help to separately analyze the left and right channels for stereo files. The number of levels, the specific thresholds, and whether or not a bandpass filter is applied before calculating the volume is based on the STYLE setting set by the user in the config file. In addition to the official documentation, I found a slide presentation, [Introduction to PyAudio](https://slides.com/jeancruypenynck/introduction-to-pyaudio/embed#/), by Jean Cruypenynck to be very helpful.

If the STYLE is set to 2, then bandpassFilter.py is called to process the digital audio stream and return a modified stream with the bandpass filter applied. The program is very short and simple. It uses two functions from the scipy signal processing library to filter out audio input below 500 Hz and over 2500 Hz. No bandpass filter is applied for STYLE 0 or STYLE 1.

# Using ChatterPi

This section describes how to set up and install both the hardware and software for using ChatterPi, and for using it.

## Hardware

The software was developed on a Raspberry Pi 3 Model A+. It should certainly run on a Pi 3B+ or a Pi 4. I don't know about a Pi 2, and it does NOT run correctly on a Pi Zero. 

In addition to the Raspberry Pi, you&#39;ll need a USB sound card. This is needed for several reasons. First, if you plan to use an external sound source, you need a way to get audio into your Pi. Second, besides not producing very good sound, the audio out connector may share timing with the Pulse Width Modulation (PWM) code that is needed to drive the servo, creating conflicts. Use of an inexpensive USB sound card solves both issues. I&#39;ve used one from Adafruit that sells for less than $5 and works well (see [https://www.adafruit.com/product/1475](https://www.adafruit.com/product/1475)). You will need TRS (standard stereo) plugs or an adapter to go into the headphone and microphone jacks on the sound card. The card does not work with a TRRS (combination microphone / stereo headphone plug. You only need a microphone or other external sound source if you wish to use one. Otherwise you can use audio .wav files that you save on the Raspberry Pi. You still need the USB sound card for audio output, however.

That&#39;s all you need for the audio servo controller. Of course, you&#39;ll need a power supply and a servo that you want to control, such as a servo-equipped talking skull, and a passive infrared sensor (PIR) if you want to trigger your prop using one. I used this one ([https://www.parallax.com/product/555-28027](https://www.parallax.com/product/555-28027)) from Parallax for development, as I had a spare one already. ChatterPi can also be set to trigger off of a repeating timer or to just turn on and run if you don&#39;t want to use an external sensor.

The default PIN selection (which can be changed in the config.ini file) are:

- Jaw servo: 18
- PIR input trigger: 23
- Trigger out: 16
- Eyes: 25

## Software Installation and Setup

This section assumes you have a Raspberry Pi with Raspbian installed and either running with a keyboard and display or in headless mode remoted to another system. There are good instructions on the Internet already on how to get a Raspberry Pi up and running. You also need to have the Pi connected to the Internet to download software.

ChatterPi is written in Python 3, and Python 3 comes already installed with Raspbian. Hower, in addition to the ChatterPi modules, you&#39;ll need to install and initialize several other libraries that are not included out of the box in Raspbian. These are:

- GPIO Zero : This is already installed if you have loaded the full Raspbian operating system, which is recommended. This is the library ChatterPi uses to control the General-Purpose Input/Output (GPIO) pins on the Raspberry Pi. It is very user friendly for programming.
- PiGPIO: this is the underlying pin control library that is used &quot;underneath the covers&quot; of Gpio Zero.
- PortAudio: A library for audio playback and recording.
- PyAudio: The wrapper that lets Python programs access PortAudio.
- Scipy: A Python library for scientific and technical computing. ChatterPi uses its bandwidth filter function in some modes.

Here&#39;s how to go about setting this up. On the Raspberry Pi, open a command line. It&#39;s always a good idea to be sure all the packages on your system are up to date. Type the following:

$ sudo apt-get update

$ sudo apt-get upgrade

If you are running the full Raspbian installation, you can skip these steps. If you are running Raspbian Lite (untested), type:

$ sudo apt update

Then install the package for Python 3:

$ sudo apt install python3-gpiozero

To install PiGPIO, type:

$ sudo apt install pigpio

$ sudo systemctl enable pigpiod

$ sudo apt-get install python3-pigpio
The first command downloads and install PiGPIO, while the second command ensures that it starts running in the background whenever the Pi starts. The 3rd command loads the required python package. 

To install PortAudio:

$ sudo apt-get install portaudio19-dev

To install PyAudio

$ sudo apt-get install python3-pyaudio

To install Scipy, use the command:

$ sudo apt-get install python3-scipy

## Audio Device Setup and Volume Control

The easiest way to select the USB sound card for audio input and output is through the volume control on the PI&#39;s desktop. Right click on the volume (speaker) icon on the upper right of the screen and select USB Audio Device for input and output. You can also use this control to adjust the volume.

To adjust the volume from the command line, type:

$ alsamixer

Do not set the microphone input or speaker output levels too high, as you may generate too much noise or feedback.

If your USB card does not show up, then that card does not have hardware support. Google &quot;raspberry pi software volume control&quot; to find out how to control the volume via the command line.

Last step: reboot your Pi to make sure all the changes take effect.

_Congratulations, your ChatterPi is now all setup and ready for use!

## Operation

**QuickStart:** Over time, you should explore and experiment with the many parameters can be changed in the config.ini file. However, the number of parameters can seem intimidating, so this section will get you up and running with a minimum of work. Initial default values have been set for all the parameters, the source is set to use audio files, and a sample audio file is included, so you do not need your own audio file or a microphone to get started. The trigger is set to TIMER mode, so an external sensor such as a PIR is not needed.

First, install the ChatterPi files in /home/pi/chatterpi. If you know the upper and lower limits for your servo, open the config.ini file for editing and set the SERVO\_MIN and SERVO\_MAX values (in microseconds) the values for your servo. Then save the file. Now go to the terminal window and go to the /home/pi/chatterpi directory. Then run ChatterPi:

$ cd /home/pi/chatterpi

$ python3 main.py

You&#39;ll see a lot of warnings and errors concerning &quot;ALSA&quot; but don&#39;t worry about them. Believe it or not, this is normal. Every 10 seconds, the audio will play and the servo will move in sync. _Congratulations!_

Control-C will stop the program.

**Detailed Instructions:** The ChatterPi files should be installed in /home/pi/chatterpi. Within the chatterpi directory there is a subdirectory called vocals. The sound files you wish to play should be placed in that folder. The files must be 16 bit .wav files (the most common type) and can be either mono or stereo files. You must use the naming convention v##.wav, where xx ranges from 01 to 10. The purpose is so that you can have the prop play different audio tracks, in a set order, one each time the prop is triggered. The first time the prop is triggered it will play the lowest numbered file, and cycle through the list, skipping any missing numbers, and starting over again with the first track after all have been played. If you only want to play one track, that&#39;s fine, just name it v01.wav. If you need to edit your files, or you have mp3 or other format files that you need to convert to .wav to work with ChatterPi, the free and excellent [Audacity](https://www.audacityteam.org/) software can do this and much more.

**Use of Separate Tracks in Stereo Files:** If you just have a mono or stereo sound file that you want to play and control the servo, you can skip this section. However there are some tricks that can be used with stereo .wav files to improve the fidelity of your jaw motion in some scenarios. The jaw motion is actually controlled exclusively by the right channel of stereo .wav files. The audio output sent to the speakers can be set using the OUTPUT\_CHANNELS parameter to be either LEFT (only) or BOTH (both left and right channels. The reason for providing this option is that some haunters want to do something different with the right channel. One option is to record the desired complete audio output (the voice along, with music or other sounds) on the left channel (channel 0) and record a separate track of just sounds or signal tones, to drive the servo but not be played out through the speakers, on the right channel (channel 1). That way you can more precisely control the servo action and have it, for example, not open wide when a loud &quot;ssssss&quot; sound occurs. To do this, set the OUTPUT\_CHANNELS parameter to LEFT, since you do not want to play the right channel through the speakers. Another option is to provide the voice on the right channel, and any accompanying audio or other sounds on the left. In this case, set the OUTPUT CHANNELS to BOTH. The right channel, as always, will control the servo, but both the voice and accompanying music will be sent out to the speakers.

**Configuration:** The options and parameters for ChatterPi are set in the config.ini file, which should be edited and saved with your desired settings prior to running the program. ChatterPi comes with a default config.ini file. It is recommended that you save a backup copy under another name. That way, you can always revert back to a working configuration file. Config.ini is divided into 5 sections, which we will now walk through. A copy of the contents of the default config.ini file is provided in Appendix B. There are a lot of parameters you can change, in order to provide flexibility, however you do not have to set or change them all. Simply focus on the parameters of interest to you. As described in the **QuickStart** section, you can run ChatterPi with the default settings right out of the box.

[SERVO]

This section has four parameters. SERVO\_MIN and SERVO\_MAX are the minimum and maximum values to set your servo to, to avoid going beyond it or the prop&#39;s limit. This is provided in microseconds (the time of the pulse signals).

MIN\_ANGLE and MAX\_ANGLE are the open and closed position for your servo, in degrees. If your jaw is _closed_ when the servo is commanded to a high value and _open_ when the servo is commanded to a minimum value, you should set the MAX\_ANGLE to the value for closed and the MIN\_ANGLE to the value for open.

[CONTROLLER]

This section selects the &quot;style&quot; to be used for controlling the servo and the threshold values for each style. There are 3 styles, numbered 0, 1, and 2. Style 0 operates like a Scary Terry style audio servo controller. It begins to open the jaw fully when the audio input volume exceeds the threshold, and begins completely closing the jaw when the volume is below that threshold.

Style 1 operates like the jawduino. The servo is commanded to open 1/3rd of the way if the first threshold is exceeded, 2/3rds if the 2nd threshold is exceeded, and completely if the third threshold is exceeded.

Style 2 functions like style 1, but first applies a bandpass filter to filter out low and high frequencies, since in speech, these do not tend to cause jaw movements.

The audio volume of each sample of the audio input is an integer that may range from 0 to 32767. The thresholds should similarly be set to integer values in this range.

[AUDIO]

This section specifies the source for the audio input (either FILES or MICROPHONE). Files must be 16 bit .wav files, either monophone or stereo. External input can be either from a microphone or line in from another source.

The OUTPUT\_CHANNELS specifies, for stereo files, whether both channels should be sent to the speaker (BOTH) or just the left channel (LEFT). See the subsection above titled **Use of Separate Tracks in Stereo Files** for more information on why and how you may want to use this feature. If you have not done any special editing on your files, leave it set to BOTH.

When you are using .wav files the software can determine when it has reached the end of the file. If you are using external input by setting SOURCE to MICROPHONE, the software has no way to determine when an audio stream has ended. The MIC\_TIME setting, in seconds, specifies how long to keep the audio stream running form the external input when ChatterPi is triggered. I&#39;ve found that the input levels on my setup are lower when using a microphone so I have to lower my trigger levels.

The AMBIENT parameter is not currently used. It will be used in a future release.

There is one other parameter in this section, the BUFFER\_SIZE. This parameter is not currently used. 

[PROP]

The parameters in the PROP section control how the prop is triggered and what else may be triggered or turned on at the same time.

PROP\_TRIGGER takes one of three values, PIR, TIMER, or START. PIR will have ChatterPi start the audio and controlling the servo whenever the PIR\_PIN is sent a 3V signal from another device. Often, this may be a Passive Infrared (PIR) motion detector sensor, but it can be anything you&#39;d like. When set to TIMER, ChatterPi starts the audio and controls the servo every time the timer expires. The delay time, in seconds, between the end of one activation and the start of the next is set by the DELAY parameter. START is only a valid setting when the SOURCE is MICROPHONE. It turns on the audio input and servo control immediately upon start up and leaves it open and running until the program is ended.

EYES may be set to ON or OFF, to control whether or not the EYES\_PIN is set high when the prop is triggered and stay high until the audio input ends.

TRIGGER\_OUT may be set to ON or OFF to control whether or not the TRIGGER\_OUT\_PIN is set to high for 0.5 seconds when the prop is triggered. This can be used to trigger another device or prop.

Unless you are using the pins for some other purpose, it is fine to leave EYES and TRIGGER\_OUT set to ON, even if you are not using them.

[PINS]

This section specifies which GPIO pins are used for the servo control channel (JAW\_PIN), the input trigger (PIR\_PIN), the LED &quot;eyes&quot; output (EYES\_PIN), and the trigger output (TRIGGER\_OUT\_PIN).

**Running the Program:** To run the program, you can start main.py from the command line by going to the chatterpi directory and typing:

$ python3 main.py

There will be a large number of ALSA warnings and errors displayed on the screen. Believe it or not, this is normal, and ChatterPi will run properly. Control-C will stop the program.

## Run Automatically On Boot

Your ChatterPi is hopefully now up and running and you have adjusted the parameters. If you want to start ChatterPi from the Pi&#39;s command line or GUI, you&#39;re good to go. But for use in a prop, you may want to configure your Pi to automatically begin running ChatterPi on boot, with no need for user interaction. To do this, move the chatterpi.service file in the chatterpi directory to /lib/system/system. Then type:

$ sudo systemctl enable chatterpi.service

This tells the operating system to run chatterpi at the end of the boot sequence. See[https://www.raspberrypi.org/documentation/linux/usage/systemd.md](https://www.raspberrypi.org/documentation/linux/usage/systemd.md) for more information and commands you can use form the command line to restart or stop ChatterPi when it is set to run automatically on boot.

# Project Roadmap

ChatterPi is already fully functional, with a wide array of options However there several capabilities and convenience features that I plan to add. The next release will add:

- A stand-alone utility program with a graphical user interface for editing the configuration file.

Beyond the next release, there are several items on the added capabilities list that may be added in one or more releases (one or two may even sneak into the next release):

- Ambient tracks: Have ambient soundtracks that play between activations. This idea is borrowed from the Wee Little Talker.
- A stand-alone utility program to allow the user to automatically maximize the volume levels on each .wav file to just below distortion and save the new files. This minimizes the need to re-tune the sensitivity settings and ensures that each .wav file has the same volume level, if desired.
- Add a &quot;TUNING&quot; mode so the user can adjust type of triggering, triggering levels, and the servo max and min positions on the fly, while the program is running. This will make it easier to tune these parameters, since currently one must stop the program, change the settings, and then rerun the program to see the effects of any changes.
- Add the ability to use .mp3 files. Simply playing MP3 files on a Raspberry Pi is easy, but they must be processed in real-time as a stream to drive the servo controller.
- Use the timer function in PIR mode as a delay before re-triggering is allowed.
- Find a way to run correctly on a Pi Zero

I would welcome anyone who wanted to work on adding any of these advanced features.




