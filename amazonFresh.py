import os
import sys
import argparse
import time

from selenium import webdriver
from selenium.common import exceptions

from twilio.rest import Client

#############################################################################################
#Please Read: I am yet to get a succesful slot on Amazon Fresh so I do not know exactly how
# the page looks like when slots are available so I am currently checking only based
# on what I see when there are no slots available.
# This might not be a 100% through check.
# This is different than the amazonPrimeNow.py that actually checks for a positive
# match on text that appears only when a window is available (at the time of this writing)
#############################################################################################

class AutomateGroceryDelivery:
    def __init__(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--user', action="store")
        parser.add_argument('--password', action="store")
        args = parser.parse_args()
        self.username = args.user
        self.password = args.password

        self.my_mobile = "your cell_number"
        self.twilio_num = " registered twilio_number"
        self.text_content = "Slots Available on Amazon Fresh. Order now!"
        self.long_pause = 20
        self.short_pause = 2
        
        # THis is the right way to source sid and token. Put these an env file and source it in python
        # You *can* put them directly here as well but that is **INSCEURE**
        self.account_sid = os.environ['TWILIO_ACCOUNT_SID']
        self.auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.amazon_fresh_url = 'amazon fresh sign in url'
        self.driver = webdriver.Chrome('location of your selenium webdriver')  # Optional argument, if not specified will search path.
        self.driver.maximize_window()

    def send_sms(self):
        # Your Account Sid and Auth Token from twilio.com/console
        print("sending sms...")
        client = Client(self.account_sid, self.auth_token)
        client.messages.create(
            to=self.my_mobile, 
            from_=self.twilio_num,
            body=self.text_content)

    def login(self, redirect = True):
        # login is called from two places:
        # 1.) initial login
        # 2.) when password is asked again for sign in
        if redirect:
            self.driver.get(self.amazon_fresh_url)
        try:
            user_name = self.driver.find_element_by_id('ap_email')
            user_name.clear()
            user_name.send_keys(self.username)
            time.sleep(self.short_pause) # add delay to stop the captcha kickin
            
            continue_btn = self.driver.find_element_by_id('continue')
            continue_btn.click()
            time.sleep(self.short_pause)
        except:
            pass # sometimes only password is asked so expected that username is not present

        password = self.driver.find_element_by_id('ap_password')
        password.clear()
        password.send_keys(self.password)

        signin_btn = self.driver.find_element_by_id('signInSubmit')
        signin_btn.click()

        try:
            # if we find email entry again then this means that we got captcha
            self.driver.find_element_by_id('ap_email')
            time.sleep(self.long_pause) # allow time to enter captcha
            self.login(False)
        except: # handle OTP
            # allow time for optional OTP authentication
            try:
                self.driver.find_element_by_xpath('//*[contains(text(),"Enter OTP")]')
                time.sleep(self.long_pause)
                self.driver.find_element_by_id('auth-signin-button').click()
                time.sleep(self.short_pause)
            except:
                pass

    def goToCheckOutPage(self):
        # go to fresh checkout page
        checkout_btn = self.driver.find_element_by_xpath('//input[starts-with(@name,"proceedToALMCheckout")]')
        checkout_btn.click()
        time.sleep(self.short_pause)

        # Before you checkout page
        continue_btn = self.driver.find_element_by_xpath('//a[@name="proceedToCheckout"]')
        continue_btn.click()
        time.sleep(self.short_pause)

        # see if password is asked again
        # if so then enter it
        try:
            self.login(False) # no redirect to login page # we already at the login screen
        except:
            print("No password asked again... Continuing...")        

    def goCartCheckoutReadyAndNotify(self):
        cart = self.driver.find_element_by_id('nav-cart-count')
        cart.click()
        time.sleep(self.short_pause)
        
        self.goToCheckOutPage()

        # See if slots available
        slot_available = False
        count = 1
        while (not slot_available):
            print("no slots available. Trying again... attempt = ", count)
            # see if we landed on proceed to check out page
            # sometimes after many refreshes you are re-directed to the proceed to checkout page again
            # if so then go to final checkout page
            try:
                self.goToCheckOutPage()
                print("checkout button again...")           
            except:
            # do nothing
                pass
                      
            time.sleep(self.long_pause)
            count+=1

            try:
                self.driver.find_element_by_xpath('//*[contains(text(),"No delivery windows available.")]')
                # if can't find the confirmation that window is available then refresh
                self.driver.refresh()
            except:
                # sometimes the page stops displaying the text that is being checked above. So make it more robust by the check below
                try:
                    # Currently Amazon Fresh shows windows for 3 days.
                    # If no window is available for the given day it has "Not available" text
                    # so we check on that to re-confirm in case the first check above fails
                    numElements = 0
                    numElements = self.driver.find_element_by_xpath('//*[contains(text(),"Not available")]')
                    if numElements >= 3:
                        self.driver.refresh()
                except:
                    # do nothing slot_available will be set below
                    pass

                # unable to find any elements that indicate that slots are not available
                # This is not a 100% solid assumption! But will have to do for now
                slot_available = True
                
        # Delivery slot available! Send sms
        self.send_sms()     


a = AutomateGroceryDelivery()
a.login()
a.goCartCheckoutReadyAndNotify()
