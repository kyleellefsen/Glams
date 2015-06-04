# -*- coding: utf-8 -*-
"""
Created on Mon Dec 09 16:31:27 2013

@author: kyle
"""

from glamsinterface.connect import db
from glamsinterface.output import saveToExcel


def getExperiments(lab_member_name):
    query="""SELECT r.date as experiment_date, 
                    m.name AS mousename,
                    m.DOB,
                    DATEDIFF(r.date,m.DOB) AS age,
                    r.description,
                    r.notes
            FROM mice as m
            LEFT JOIN experiments as r ON m.id=r.mouse_id
            LEFT JOIN lab_members            ON lab_members.id=r.lab_member_id
            WHERE lab_members.name='{0}' 
            ORDER BY r.date""".format(lab_member_name)
    experiments=db.execute(query)
    return experiments

def getaName():
    lab_members=db.execute("SELECT name FROM lab_members")
    return lab_members[0][0]
    
def main():
    experimenter=getaName()
    experiments=getExperiments(experimenter)
    filename='Experiment_Log.xls'
    header=['Experiment Date','Mouse Name','DOB','Age at Experiment (days)','Description','Notes']
    saveToExcel(header,experiments,filename)
    
if __name__=='__main__':
    main()