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
Account tokens and secrets would have to be configured from [here](https://dev.twitter.com/).

Twitter Handles:
---
Configure whichever ISP you belong to, below are some of the twitter handles:

| ISP | Twitter Handle |  
| --- | --- |   
| Axxess | @AxxessDSL |
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
* (Optional) To upgrade packages
```
pip install -r requirements.txt --upgrade
```
* Define virtual environment and activate virtual-environment
```
pyvenv-3.5 env
source env/bin/activate
```

* To execute script,
```
python sluggish_isp.py
```

* Deactivate virtual-environment
```
deactivate
```

Output
---
```
▶ pyvenv-3.5 env
source env/bin/activate
(env)
▶ python sluggish_isp.py
(debug) Download: 0.33 kb/s Upload: 0.20 kb/s
(info) Going to tweet about it...
(info) Tweet: Hey @AxxessDSL, what gives! I pay for 4/1 Mbps. Why am I only getting 0.33/0.20 Mbps? (Size: 85 chars)
(env)
```
