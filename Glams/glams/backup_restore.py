# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 18:06:27 2013
@author: Kyle Ellefsen

This script allows you to back up or restore your database.  
On Windows 7, you should be able to execute this file and back up your database.  On other operating systems, edit the paths to mysql and mysqldump, then run this file.  
"""

import os, datetime
os.chdir(os.path.split(os.path.realpath(__file__))[0])
from glams.databaseInterface.connect import importconfig


#### EDIT THESE PATHS IF THEIR LOCATION DIFFERS ON YOUR SYSTEM ####
pathToMysqldump="C:\\Program Files\\MySQL\\MySQL Server 5.6\\bin\\mysqldump"
pathToMysql="C:\\Program Files\\MySQL\\MySQL Server 5.6\\bin\\mysql"
#####################################################################


### GET database connection info from config.txt
config=importconfig()
user=str(config['user'])
database=str(config['database'])
password=str(config['password'])

def backupDB():
    if not os.path.exists('glams_backups'):
        os.makedirs('glams_backups')
    outputFile='glams_backup_'+datetime.datetime.today().strftime("%Y.%m.%d.%H.%m.%S")+'.sql'
    command='\"\"{0}\" -u {1} -p{2} {3} >glams_backups\\{4}\"'.format(pathToMysqldump, user, password, database, outputFile)
    value=os.system(command)
    print(value)

def restore(filename):
    command='\"\"{0}\" -u {1} -p{2} {3} < {4}\"'.format(pathToMysql, user, password, database, filename)
    value=os.system(command)
    print(value)
    
if __name__=='__main__':
    backupDB()