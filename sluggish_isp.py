#!/usr/bin/python

import datetime
import json
import time
import tweepy
import re
import os.path
from enum import Enum
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

CONFIG = "config.json"
MLAB_URL = "https://www.measurementlab.net/p/ndt-ws.html"


class Driver(Enum):
    driver = 0
    chrome = 1
    firefox = 2


class Config(object):

    with open(CONFIG, "r") as f:
        config = json.load(f)

        # get speed related configurations
        download = float(config["bandwidth"]["download"])
        upload = float(config["bandwidth"]["upload"])
        margin = float(config["margin"])
        isp = config["isp"]

        # get twitter configurations
        twitter_token = config["twitter"]["twitter_token"]
        twitter_token_secret = config["twitter"]["twitter_token_secret"]
        twitter_consumer_key = config["twitter"]["twitter_consumer_key"]
        twitter_consumer_secret = config["twitter"]["twitter_consumer_secret"]

        # get log file-name
        log = config["log"]["name"]

        driver_type = None
        binary_path = None

        if Driver.driver.name in config:
            if config[Driver.driver.name]["type"] == Driver.chrome.name:
                driver_type = Driver.chrome
            elif config[Driver.driver.name]["type"] == Driver.firefox.name:
                driver_type = Driver.firefox
                binary_path = config[Driver.driver.name]["binary"]
                if len(binary_path) > 0 and not os.path.isfile(binary_path):
                    driver_type = None
                    binary_path = None

        date = ("Date logged: {:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now()))


class Log(object):

    config = Config()
    def write(self, data):
        with open(self.config.log, "a") as f:
            f.write(data)


class SpeedTest(object):

    def __init__(self, config):
        self.download = ""
        self.upload = ""
        self.latency = ""
        self.jitter = ""
        self.download_rate = ""
        self.upload_rate = ""

        self.log = Log()
        self.config = config
        self.driver = None
        self.wait = None

        try:
            if self.config.driver_type is None:
                self.driver = webdriver.Firefox()
            else:
                # create driver
                if self.config.driver_type == Driver.firefox:
                    if self.config.binary_path is not None:
                        self.driver = webdriver.Firefox(firefox_binary=FirefoxBinary(config.binary_path))
                    else:
                        self.driver = webdriver.Firefox()
                elif self.config.driver_type == Driver.chrome:
                    self.driver = webdriver.Chrome()
            self.wait = WebDriverWait(self.driver, 5)
        except WebDriverException as ex:
            self.log.write("{:%Y-%b-%d %H:%M:%S} Driver creation failed".format(datetime.datetime.now()))
            self.log.write(str(ex))

    def valid_driver(self):
        return self.driver is not None

    def run_test(self):
        if self.driver is None or self.wait is None:
            return

        self.driver.get(MLAB_URL)
        try:
            button = self.wait.until(EC.element_to_be_clickable(
                (By.ID, "start-button")
            ))
            button.click()
        except TimeoutException:
            self.log.write("Failed to find \"start\" button")

    def store_test_value(self):
        if self.driver is None:
            return

        try:
            self.upload = str(self.driver.find_element_by_id("upload-speed").text)
            self.upload_rate = str(self.driver.find_element_by_id("upload-speed-units").text)

            self.download = str(self.driver.find_element_by_id("download-speed").text)
            self.download_rate = str(self.driver.find_element_by_id("download-speed-units").text)

            self.latency = self.driver.find_element_by_id("latency").text
            self.jitter = self.driver.find_element_by_id("jitter").text
        except TimeoutException:
            self.log.write("Could not find speed test related values")

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver is not None:
            self.driver.quit()


class Twitter(object):

    def __init__(self):
        self.config = Config()
        self.log = Log()
        auth = tweepy.OAuthHandler(self.config.twitter_consumer_key, self.config.twitter_consumer_secret)
        auth.set_access_token(self.config.twitter_token, self.config.twitter_token_secret)

        try:
            self.api = tweepy.API(auth)
        except:
            self.log.write("--" + self.config.date + " --\n"
                           "Twitter authentication Failed\n"
                           "-----------------------------\n")


class Output(object):

    def __init__(self, config, speedtest, twitter):
        self.config = config
        self.log = Log()
        self.twitter = twitter
        self.speedtest = speedtest
        self.margin = self.config.margin
        self.isp = self.config.isp

        # download configuration and speed-test data
        self.config_download = self.config.download
        self.speedtest_download = self.speedtest.download
        self.speedtest_download_rate = self.speedtest.download_rate

        # upload configuration and speed-test data
        self.config_upload = self.config.upload
        self.speedtest_upload = self.speedtest.upload
        self.speedtest_upload_rate = self.speedtest.upload_rate

    def test_results(self):
        # If driver creation failed, speedtest data would be empty, identify cause behind this
        if self.speedtest_download == "" or self.speedtest_upload == "":
            print("(err) Speed test values invalid\n")
            self.log.write("(err) Speed test values invalid\n")
            return

        st_download = float(self.speedtest_download) if len(re.findall("[0-9]+", self.speedtest_download)) > 0 else 0
        st_upload = float(self.speedtest_upload) if len(re.findall("[0-9]+", self.speedtest_upload)) > 0 else 0

        download_in_mbps = convert_to_mbps(st_download, self.speedtest_download_rate)
        upload_in_mbps = convert_to_mbps(st_upload, self.speedtest_upload_rate)

        downunder_download_rate = download_in_mbps < ( self.config_download * self.margin )
        downunder_upload_rate = upload_in_mbps < ( self.config_upload * self.margin )

        self.speedtest_download = "{0:.2f}".format(download_in_mbps)
        self.speedtest_upload = "{0:.2f}".format(upload_in_mbps)
        print("(debug) Download:", self.speedtest_download,self.speedtest_download_rate,"Upload:",self.speedtest_upload,self.speedtest_upload_rate)

        if(downunder_download_rate or downunder_upload_rate):
            print("(info) Going to tweet about it...")
            try:
                tweet_str = ("Hey " + self.isp + ", what gives! I pay for " +
                           str(int(self.config_download)) + "/" +
                           str(int(self.config_upload)) + " Mbps. Why am I only getting " +
                           str(self.speedtest_download) + "/" +
                           str(self.speedtest_upload) + " Mbps?")

                print("(info) Tweet:", tweet_str, "(Size:", len(tweet_str), "chars )")
                self.twitter.api.update_status(tweet_str)

                self.log.write("-- " + self.config.date + " --\n" +
                               "- ERROR: Bandwidth not in spec - \n" +
                               "Download: " + self.speedtest_download + " Mbps \n" +
                               "Upload: " + self.speedtest_upload + " Kbps \n" +
                               "Latency: " + self.speedtest.latency + " msec round trip time \n" +
                               "Jitter: " + self.speedtest.jitter + " msec \n" +
                               "-------------------- \n")
            except:
                self.log.write("-- " + self.config.date + " --\n" +
                               "Twitter post / logging failed \n" +
                               "-------------------- \n")
        else:
            self.log.write("-- " + self.config.date + " --\n" +
                                  "- Bandwidth in spec - \n" +
                                  "Download: " + str(self.speedtest_download) + " Mbps \n" +
                                  "Upload: " + str(self.speedtest_upload) + " Kbps \n" +
                                  "Latency: " + str(self.speedtest.latency) + " msec round trip time \n" +
                                  "Jitter: " + str(self.speedtest.jitter) + "\n" +
                                  "-------------------- \n")


def convert_to_mbps(st_amt, st_rate):
    if st_rate.lower() == "kb/s":
        return float(st_amt)/1024
    elif st_rate.lower() == "mb/s":
        return float(st_amt)
    else:
        return 0


if __name__ == "__main__":
    _config_data = Config()
    _speedtest = SpeedTest(_config_data)
    _speedtest.run_test()
    if _speedtest.valid_driver():
        time.sleep(60)
    _speedtest.store_test_value()
    _twitter = Twitter()
    output = Output(_config_data, _speedtest, _twitter)
    output.test_results()
