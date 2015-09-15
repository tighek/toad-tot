#!/usr/bin/env python
# client.py

import config as cfg
import sys
import socket

def main(elems):
    try:
        for e in elems:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((cfg.ACTION_IP, cfg.ACTION_PORT))
            client.send(e)
            client.shutdown(socket.SHUT_RDWR)
            client.close()
    except Exception as msg:
        print msg

#########################################################

if __name__ == "__main__":
    main(sys.argv[1:])