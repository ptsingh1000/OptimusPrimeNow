import os
import sys
import argparse
import time

from selenium import webdriver
from selenium.common import exceptions

from twilio.rest import Client

class AutomateGroceryDelivery:
    def __init__(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--user', action="store")
        parser.add_argument('--password', action="store")
        args = parser.parse_args()
        self.username = args.user
        self.password = args.password

        self.my_mobile = "your cell number here"
        self.twilio_num = "registered twilio number here"
        
        # This is the right way to source sid and token. Put these an env file and source it in python
        # You *can* put them directly here as well but that is **INSCEURE**
        self.account_sid = os.environ['TWILIO_ACCOUNT_SID']
        self.auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.amazon_prime_url = 'prime now sign in page_url here'
        self.driver = webdriver.Chrome('optional path_to_driver')  # Optional argument, if not specified will search PATH.
        self.driver.maximize_window()
        self.long_pause = 20
        self.short_pause = 2

    def send_sms(self):
        # Your Account Sid and Auth Token from twilio.com/console
        print("sending sms...")
        client = Client(self.account_sid, self.auth_token)

        client.messages.create(
            to=self.my_mobile, 
            from_=self.twilio_num,
            body="Slots Available on Amazon PrimeNow. Order now!")


    def login(self, redirect = True):

        # login is called from two places:
        # 1.) initial login
        # 2.) when password is asked again for sign in
        if redirect:
            self.driver.get(self.amazon_prime_url)
        try:
            user_name = self.driver.find_element_by_id('ap_email')
            user_name.clear()
            user_name.send_keys(self.username)
            time.sleep(self.short_pause) # add delay to stop the captcha kickin
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

    def goCartCheckoutReadyAndNotify(self):
        # might need to change this class search text in some cases. start by removing partial text
        # ex: just search for "page_header_cart_button__cart-icon-count" below if does not work
        # if that does not work you will need to inspect the cart element on top right of the page
        # that shows the cart with the number of items in the cart.
        cart = self.driver.find_element_by_xpath('//span[starts-with(@class,"page_header_cart_button__cart-icon-count__3J3sx")]')#page_header_cart_button__cart-icon-count__3J3sx
        cart.click()
        time.sleep(self.short_pause)
        # go to checkout page
        checkout_btn = self.driver.find_element_by_xpath('//span[contains(text(),"Proceed to checkout")]') #Proceed to checkout
        checkout_btn.click()
        time.sleep(self.short_pause)
        # see if password is asked again
        # if so then enter it
        try:
            self.login(False) # no redirect to login page # we already at the login screen
        except:
            print("No password asked again... Continuing...")

 
        # See if slots available
        slot_available = False
        count = 1
        while (not slot_available):
            print("no slots available. Trying again... attempt = ", count)
            # see if we landed on proceed to check out page
            # sometimes after many refreshes you are re-directed to the proceed to checkout page again
            # if so then go to final checkout page
            try:
                cb = self.driver.find_element_by_xpath('//span[contains(@class, "cart-checkout-button")]')
                cb.click()
                print("checkout button again...")
                # see if password is asked again
                # if so then enter it
                try:
                    self.login(False) # no redirect to login page # we already at the login screen
                except:
                    print("No password asked again... Continuing...")                
            except:
            # do nothing
                pass
                      
            time.sleep(self.long_pause)
            count+=1

            try:
                self.driver.find_element_by_xpath('//*[contains(text(),"Be sure to chill any perishables upon delivery")]')
                slot_available = True
            except:
                # if can't find the confirmation that window is available refresh
                self.driver.refresh()                

        # Delivery slot available! Send sms
        self.send_sms()     


a = AutomateGroceryDelivery()
a.login()
a.goCartCheckoutReadyAndNotify()
