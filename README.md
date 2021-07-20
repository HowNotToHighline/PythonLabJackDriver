# Python LabJack Driver

This is a quick and dirty script I wrote to use a LabJack as dyno for Ryan from HowNotToHighline. It was written in an hour or two (including learning how the LabJack library worked), so it's not the nicest piece of code I've ever written.

The script is based on LabJack for the analog interface and tkinter for displaying the peak force. A separate thread is started for doing the semi-realtime analog processing. The latest version is using the LabJack stream interface, though Ryan is still (as far as I know) using an older version that uses polling. The polling version is limited to about 200Hz, though that seems to be a LabJack limitation (due to oversampling, they have documented it pretty well).

I consider this a temporary solution. I'm already working on another c++ based system, so I'm not going to actively work on this script, though I plan on at least keep it working.
