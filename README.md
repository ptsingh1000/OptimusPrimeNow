# OptimusPrimeNow
**OptimusPrimeNow** is designed to help people find the much coveted delivery windows on Amazon Prime and Amazon Fresh during COVID-19 lockdown automatically! :smiley:

## Scripts:
* ### amazonPrimeNow.py
  Use this to order from Amazon Prime Now
* ### amazonFresh.py
  Use this to order from Amazon Fresh
  
## Purpose:
These script automate the process of continuously checking Amazon Prime Now and Amazon Fresh for availabilty of delivery windows and sends a text msg to the user when a window opens up. Due to COVID-19 necessitated lockdowns, this process has become quite frustrating in recent days. At the time of writing this, slots open up very briefly and disappear soon enough. I spent few days to look for slots only to get frustrated by repeated checking and finding nothing. As they say: **"Frustration is the mother of all inventions!"** (actually probably I said this :wink:), this constant frustration led me to write up this script. I hope I can save you some of it and more importantly help you stay safe and indoors!

They also take into account 2FA authentication, if enabled, and/or captcha process if the user encounters it at login time (this is of course a manual action from the user but this is only encountered, if at all, at startup when we need to login into the account). The scripts assume that your cart is not empty when it is run. It is highly recommended that you keep all the items you need in your cart so that you can order as soon as you get the notification. I have seen slots disappear in less than a minute or two at times!

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
### Browser: Google Chrome
On a linux env run: python amazonPrimeNow.py --user [your amazon account username] --password [your password]
Before you run the script please fill in the necessary info that has been left blank such as twilio sid and token, cell number etc.
* Start the Selenium webdriver
* Export the twilio env variables if you are storing the credentials in an env file (**highly recommended**): source ./[env_file]

## Finally:
First things first. My total experience of Selenium is limited to developing this script! There are quite a few things that can be improved here but I want to get a working version up and running first rather than perfecting it. Things like putting in a config file to take in time delay params etc. Next Selenium is supposed to be used as a testing framework. I have tried to test this script to cover some variety of workflows but there can be some gotchas that I might have missed so don't be surprised if this does not work exactly the way it is supposed to on the first run! There are a lot of moving pieces here such as your amazon landing page might be slightly different; the websites themselves are dynamic and they constantly evolve which can result in some checks that work as of now fail. You might have to do some minor tweaks here and there!

## Future work:
Fully automate the ordering process. There are a few things to keep in mind before doing this however. To list just one example: All items that were added in cart are not guaranteed to be present at time of check out as many go out of stock. This can at times lead to your cart value dropping lower than the free delievery threshold and may incurr additional charges etc.

## Licensing:
No expert in writing this text too! You are free to use this script as you see fit. There is no guarantee that this would work for everyuse case. By using this script you absolve the author of any responsibilities/liabilities/damages **(feel free to let your imagination insert more similar negative words here)** that may arise by the usage of this script. Use at your own risk!
  
 ## Stay Safe! 
