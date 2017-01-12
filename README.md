Sluggish ISP
---
Execute run speed tests and tweet about their degraded service.

Details
----
Python script uses selenium webdriver to scrap speedtest results and tweets them at configured isp.

Script result includes:
- Download speed (Mbps)
- Upload speed (Mbps)
- Latency (msec)
- Jitter (msec)

Dependencies
---
- tweepy
- selenium
- geckodriver
- chromedriver

Setup and Execution
---
* To execute this script, install Dependencies:
```
pip install -r requirements.txt
```

* To execute script,
```
python sluggish_isp.py
```

Status
---
Work in progress ...
