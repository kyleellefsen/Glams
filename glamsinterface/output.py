# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 12:55:44 2013

@author: kyle
"""
from xlwt import * #this is for saving things to Excel. Not strictly necessary
import datetime

def saveToExcel(header,mysqlresults,filename):
    """This function will save the results of your mysql query to an excel file
    
    header: a list of strings which will go in the first row of the excel file
    mysqlresults: a list of lists, typically the object returned by the db.execute() function
    filename: the name of the output file.  Ends in .xls
    """
    
    
    defaultstyle=easyxf('font: name Calibri;')
    headerstyle=easyxf('font: height 260, color red;')    
    datestyle = XFStyle()
    datestyle.num_format_str = 'YYYY.MM.DD'    
    column_style=[defaultstyle for i in header]
    dateidx=[i for i, x in enumerate(mysqlresults[0]) if type(x) is datetime.datetime or type(x) is datetime.date] #gets the indecies where the entry is a date
    for i in dateidx:
        column_style[i]=datestyle
    
    
    book=Workbook('utf-8')
    ws = book.add_sheet('A test sheet')
    ws.col_default_width=200

    for i in range(len(header)):
        ws.write(0,i,header[i],headerstyle)
        c=ws.col(i)
        c.width=256*20   # set the column width to be 20 characters wide
    for j in range(len(mysqlresults)):
        for i in range(len(mysqlresults[0])):
            ws.write(j+1,i,mysqlresults[j][i],column_style[i])
    book.save(filename)
    return 'Save successful'