Model of local client + web server for visualization
================================

Client connects to the mqtt broker with follwoing subsciptions (example):
--Cpu temperature (--ct)
--Cpu load (--cl)
--Virtual memory (--memo)

Local server runs on 127.0.0.1:5000 for data visualization in browser

Requirements:
---------------

- paho
- enum
- flask
- numpy
- pandas
- ipaddress
- argparse


How To Run:
------------

1. $ python localClientMain.py --host 192.168.0.14 --ct --cl True --memo True
2. For viewing browser data go to http://127.0.0.1:5000/
  

