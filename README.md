Sluggish ISP
---
Execute run speed tests and tweet about your ISP's degraded service.

Details
----
Python script uses selenium webdriver to scrap speedtest results and tweets them at configured ISP.

Script result includes:
- Download speed (Mbps)
- Upload speed (Mbps)
- Latency (msec)
- Jitter (msec)

Speed tests are done against [MLAB](http://www.measurementlab.net/tools/ndt/), but webdriver scraps [embeded iFrame](http://www.measurementlab.net/tools/ndt/p/ndt-ws.html).

Tweety python library is used for twitting composed message against ISP.
Account tokens and secrets would have to be configured from [here]( https://dev.twitter.com/).

Twitter Handles:
---
Configure whichever ISP you belong to, below are some of the twitter handles:

| ISP | Twitter Handle |  
| --- | --- |   
| Axxess | @Axxess |
| MWeb | @MWEBHelp |
| Afrihost | @Afrihost |

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
