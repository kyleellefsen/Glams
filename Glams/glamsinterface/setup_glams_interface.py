# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 14:55:58 2013

@author: kyle
"""
import os.path
import glamsinterface
filename=os.path.join(os.path.dirname(glamsinterface.__file__),'config.txt')

def main():
    if os.path.isfile(filename):
        print("""\n\n****WARNING****\n\nYou must delete your 'config.txt' file before running this script again.\nYour config file is located in {0} """.format(os.path.dirname(glamsinterface.__file__)))
    else:
        mysql_IP_address=raw_input('Enter the ip address of your mysql server (leave blank if running on this computer): ')
        if mysql_IP_address=='':
            mysql_IP_address='localhost'
        user=raw_input('Enter the name of the user you created (with read-only privileges) to access the mysql database: ')
        database=raw_input('Enter the name of the MySQL database (e.g. glams): ')
        if database=='':
            database='glams'
        password=raw_input("Enter the password for user '{}':".format(user))
        port=raw_input("Enter the port to access your mysql server (leave blank for the default '3306'): ")
        if port=='':
            port='3306'
        
        config="""mysql_IP_address={0}
user={1}
database={2}
password={3}
port={4}""".format(mysql_IP_address,user,database,password,port)
        
        f=open(filename, 'w')
        f.write(config)
        f.close()
        print("Created 'config.txt' file")
        

        
    

if __name__=='__main__':
    main()
