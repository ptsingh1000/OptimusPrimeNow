# OptimusPrimeNow
**OptimusPrimeNow** is designed to help people find the much coveted delivery windows on Amazon Prime during COVID-19 lockdown!
  
## Purpose:
This script automates the process of continuously checking Amazon PrimeNow for availabilty of delivery windows and sends a text msg to the user when a window opens up. Due to COVID-19 necessitated lockdowns, this process has become quite frustrating. At the time of writing this, slots open up very briefly and disappear soon enough.

This also takes into account 2FA authentication and/or captcha process if the user encounters it at login time (this is ofcourse a manual action but this is only encountered, if at all, at startup when we need to login into the account). The assumption is that your cart is not empty. It is highly recommended that you keep all the items you need in your cart so that you can order as soon as you get the notification.

Some timed delays are added in to make sure we do not let the service believe it is a potential DoS attack. You can change these values if you wish.

Familiarity with basics of python is assumed.

## Dependencies:
* Selenium: See https://www.selenium.dev/
  You will need to download the webdriver.
* Twilio: https://www.twilio.com/
  Twilio is used for sending text msgs. Installing and working with it is pretty straight forward. The trial account gives enough balance to get you through (hopefully!)
* python: Given!

## Usage:
### Platforms: Linux, MacOS
On a linux env run: python amazonPrimeNow.py --user [your amazon account username] --password [your password]
Before you run the scripts please fill in the necessary info that has been left blank such as twilio sid and token, cell number etc.

## Finally:
First things first. My total experience of Selenium is limited to developing this script! There are quite a few things that can be improved here but I want to get a working version up and running first rather than perfecting it. Things like putting in a config file to take in time delay params etc.

## Future work:
Fully automate the ordering process. There are a few things to keep in mind before doing this however. To list just one example: All items that were added in cart are not guaranteed to be present at time of check out as many go out of stock. This can at times lead to your cart value dropping lower than the free delievery threshold and may incurr additional charges etc.

## Licensing:
No expert in writing this text too! You are free to use these scripts as you see fit. There is no guarantee that this would work for everyuse case. By using this script you absolve the author of any responsibilities/liabilities/damages that may arise by the usage of this script. Use at your own risk!
  
  
