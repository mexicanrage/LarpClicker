# LarpClicker
A simple more or less functional autoclicker for wayland

# Installation
```sh
git clone https://github.com/mexicanrage/LarpClicker.git | cd LarpClicker | sudo ./installer.sh
```

# Guide
```Alt + T``` to toggle the autoclicker, the default autoclicker will be simulating left clicks while you hold the right click

The autoclicker will try to detect your mouse and keyboard automatically, however, the automatic detection is not perfect so it is recommended that you write the name of the devices that are not automatically recognized within the "config" file, example:
```
CLICK_DELAY_MS=1 <- You can also change the click delay in ms inside this file
KEYBOARD_DEVICE="Hangsheng R75 QMK"
MOUSE_DEVICE=Unknown
```
*Note that the name of the devices is written in quotes, but if it is unknown it simply says "Unknown"*

To activate the autoclicker you only need to use the ```larpclicker``` command that will be created by default in /usr/bin
