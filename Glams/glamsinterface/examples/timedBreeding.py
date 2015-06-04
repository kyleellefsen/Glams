# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 14:22:27 2013

@author: kyle
"""
from glamsinterface.connect import db
from glamsinterface.output import saveToExcel

def getTimedMatings():
    query="""SELECT m.name AS mousename, h1.start_date, h1.end_date, c1.name AS homecage, c2.name AS breedingcage, DATEDIFF(NOW(),h1.start_date) AS daysSinceMating
FROM mice as m 
LEFT JOIN housing as h1 ON h1.mouse_id=m.id
LEFT JOIN housing as h2 ON h2.mouse_id=m.id
LEFT JOIN housing as h3 ON h3.mouse_id=m.id
LEFT JOIN care_taker ON care_taker.cage_id=h1.cage_id
LEFT JOIN lab_members ON lab_members.id=care_taker.lab_member_id
LEFT JOIN cages AS c1 ON c1.id=h1.cage_id
LEFT JOIN cages AS c2 ON c2.id=h2.cage_id
WHERE DATEDIFF(h1.end_date,h1.start_date)=1
AND h2.cage_id=h3.cage_id
AND h2.end_date=h1.start_date
AND h3.start_date=h1.end_date
AND DATEDIFF(NOW(),h1.start_date)<21
ORDER BY c1.name"""
    matings=db.execute(query)
    return matings
    
def main():
    matings=getTimedMatings()
    header=['Mouse name','Start Date','End Date','Home cage','Breeding Cage','Days Since Mating']
    filename='TimedBreeding.xls'
    saveToExcel(header,matings,filename)
    
if __name__=='__main__':
    main()