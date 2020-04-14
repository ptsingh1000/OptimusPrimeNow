import os
import sys
import argparse
import time
import json
import logging

from os import path
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
        self.text_content = "Slots Available on Amazon PrimeNow. Order now!"
        self.long_pause = 30
        self.short_pause = 2

        #Create and configure logger 
        logging.basicConfig(filename="amazon_prime_now.log", 
                            format='%(asctime)s %(message)s', 
                            filemode='w')
        #Creating an object 
        self.logger = logging.getLogger() 
        #Setting the threshold of logger to INFO 
        self.logger.setLevel(logging.INFO)
        
        # This is the right way to source sid and token. Put these an env file and source it in python
        # You *can* put them directly here as well but that is **INSCEURE**
        self.account_sid = os.environ['TWILIO_ACCOUNT_SID']
        self.auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.cookies_file = 'prime_now_session_cookies.data'
        self.amazon_prime_base_url = 'https://primenow.amazon.com/'
        self.amazon_prime_signin_url = self.amazon_prime_base_url + 'your location specific remainder url'
        self.amazon_prime_cart_url = self.amazon_prime_base_url + 'cart?ref_=pn_sf_nav_cart'
        self.driver = webdriver.Chrome('optional path_to_driver')  # Optional argument, if not specified will search path.
        self.driver.maximize_window()
        self.cookies_set = False
        self.load_cookies()        

    def save_cookies(self, overwrite = False):
        if overwrite or path.exists(self.cookies_file) == False: # either overwrite mode or first time run
            cookies = self.driver.get_cookies()
            cookies_json_str = json.dumps(cookies)
            f = open(self.cookies_file, "w")
            f.write(cookies_json_str)
            f.close()

    def get_cookies(self):
        if path.exists(self.cookies_file):
            f = open(self.cookies_file, "r")
            cookies = json.loads(f.read())
            self.logger.info("returning cookies...")
            return cookies
        else:
            return None

    def load_cookies(self):
        cookies = self.get_cookies()
        if cookies:
            self.driver.get(self.amazon_prime_base_url)
            for cookie in cookies:
                #expiry is no longer accepted when adding so remove it
                #TODO: Do we need to worry about cookies getting expired??
                if 'expiry' in cookie:
                    del cookie['expiry']
                self.driver.add_cookie(cookie)

            self.cookies_set = True
        self.logger.info("succesfully loaded cookies..")
            

    def send_sms(self, msg = None):
        # Your Account Sid and Auth Token from twilio.com/console
        self.logger.info("sending sms...")
        
        text_content = self.text_content
        if msg:
            text_content = msg

        client = Client(self.account_sid, self.auth_token)

        client.messages.create(
            to = self.my_mobile, 
            from_ = self.twilio_num,
            body = text_content)

    def login(self, redirect = True):
        # login is called from two places:
        # 1.) initial login
        # 2.) when password is asked again for sign in
        self.logger.info("logging in...")
        if redirect:
            self.driver.get(self.amazon_prime_signin_url)
 
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
            self.login(redirect = False)
        except: # handle OTP
            # allow time for optional OTP authentication
            try:
                self.driver.find_element_by_xpath('//*[contains(text(),"Enter OTP")]')
                self.logger.info("OTP entry required. Waiting for " + str(self.long_pause) + " secs.")
                time.sleep(self.long_pause)
                self.driver.find_element_by_id('auth-signin-button').click()
                time.sleep(self.short_pause)
            except:
                pass #OTP not asked

        # save cookies at the end of login
        self.save_cookies()

    def execute(self):
        if self.cookies_set:
            self.logger.info("Going to cart directly...")
            self.driver.get(self.amazon_prime_cart_url)
            time.sleep(self.short_pause)
        else:
        # if running for the first time it will come here
            self.logger.info("Script ran for the first time. Starting with home page.")
            self.login()
            cart = self.driver.find_element_by_xpath('//span[starts-with(@class,"page_header_cart_button__cart-icon-count__")]')
            cart.click()

        # go to checkout page
        time.sleep(self.short_pause)
        checkout_btn = self.driver.find_element_by_xpath('//span[contains(text(),"Proceed to checkout")]') #Proceed to checkout
        checkout_btn.click()
        self.logger.info("Proceeding to checkout...")
        time.sleep(self.short_pause)
        
        # see if password is asked again (by trying to login. will go to except block if not asked)
        # if so then enter it
        try:
            self.login(redirect = False) # no redirect to login page # we already at the login screen
        except:
            self.logger.info("No password asked again... Continuing...")

        # saving all the cookies stored until now
        # Also refreshes the cookies in each run of the script
        self.save_cookies(overwrite=True)
 
        # See if slots available
        slot_available = False
        count = 1
        while (not slot_available):
            self.logger.info("No slots available. Trying again... attempt = " + str(count))
            # see if we landed on proceed to check out page
            # sometimes after many refreshes you are re-directed to the proceed to checkout page again
            # therefore we need to check for it and if so then go to final checkout page again
            try:
                cb = self.driver.find_element_by_xpath('//span[contains(@class, "cart-checkout-button")]')
                cb.click()
                self.logger.info("checkout button again...")
                # see if password is asked again
                # if so then enter it
                try:
                    self.login(redirect = False) # no redirect to login page # we already at the login screen
                except:
                    self.logger.info("No password asked again... Continuing...")                
            except:
                # do nothing as we are on right page
                pass
                      
            time.sleep(self.long_pause)
            count+=1

            # Check if any slots available. Prime now displays the below msg if that is the case
            try:
                self.driver.find_element_by_xpath('//*[contains(text(),"Be sure to chill any perishables upon delivery")]')
                slot_available = True
            except:
                # if can't find the confirmation that window is available refresh
                self.driver.refresh()                

        # Delivery slot available! Send sms
        self.send_sms()
        self.save_cookies(overwrite = True) # saving all the cookies stored until now   


a = AutomateGroceryDelivery()
a.execute()
