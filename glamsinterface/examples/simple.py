# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 14:05:55 2013

@author: kyle
"""

from glamsinterface.connect import db

def main():
    mice=db.execute("SELECT name FROM mice")
    print(mice)

if __name__=='__main__':
    main()