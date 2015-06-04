# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 15:52:22 2013

@author: kyle
"""
from glams.databaseInterface.connect import db, db2
import mysql.connector.errors as mysqle
import urllib2, datetime
import threading
from lxml import etree
from glams.website.database.forms import getResident

lock=threading.Lock()

def getAllColumns(table):
    if table=='mice':
        return ['id','name','strain','genotyped','sex','life_status','breeding_status','DOB','DOD','cause_of_death','tag','notes']
    elif table=='genetics':
        return ['mouse_id','gene_id','zygosity']
    elif table=='lineage':
        return ['mother_id','father_id','child_id']
    elif table=='experiments':
        return ['mouse_id','lab_member_id','date','description']
    elif table=='care_taker':
        return ['cage_id','lab_member_id']
    elif table=='housing':
        return ['mouse_id', 'cage_id', 'start_date', 'end_date']
    elif table=='lab_members':
        return ['id', 'name', 'password', 'email']
    elif table=='genes':
        return ['id', 'name', 'default_presence']
    elif table=='cages':
        return ['id', 'name', 'notes', 'active', 'date_activated', 'date_inactivated', 'location','expectingpl','cagegroup']
    elif table=='transplants':
        return ['donor_id', 'recipient_id', 'date', 'notes']
    else:
        columns=db.execute("SHOW COLUMNS FROM "+table)
        col=[]
        for c in columns:
            col.append(c[0])
        return col    
def date2str(d):
    if d is None:
        return ''
    else:
        return d.isoformat().strip().split('T')[0]
def str2date(s):
    s=s.split('-')
    return datetime.datetime(int(s[0]),int(s[1]),int(s[2]))
def getAge(DOB):
    if type(DOB) != type(datetime.datetime.today()):
        return 'no DOB'
    else:
        return 'P'+str((datetime.datetime.today()-DOB).days)


        
    
class Mouse:
    def __init__(self,username,mouseID=''):
        self.username=username
        if mouseID != '':
            self.getFromDB(mouseID)
    def getFromDB(self,mouseID):
        self.d=db2.execute("SELECT m.id, m.name AS mousename, m.strain, m.sex, m.life_status, m.breeding_status, m.DOB, m.DOD, m.cause_of_death, m.tag, IF(EXISTS(SELECT * from experiments WHERE mouse_id=m.id), 'reserved','notreserved') AS reserved, m.notes AS mouse_notes, m.genotyped, cages.name AS cagename, mom.name AS mother, dad.name AS father, lab_members.name AS reserve_lab_member, experiments.date AS reserve_date, experiments.description AS reserve_description FROM mice AS m LEFT JOIN housing ON housing.mouse_id=m.id LEFT JOIN cages ON cages.id=housing.cage_id LEFT JOIN lineage ON lineage.child_id=m.id LEFT JOIN mice AS mom ON lineage.mother_id=mom.id LEFT JOIN mice AS dad ON lineage.father_id=dad.id LEFT JOIN experiments ON experiments.mouse_id=m.id LEFT JOIN lab_members ON experiments.lab_member_id=lab_members.id LEFT JOIN genetics ON genetics.mouse_id=m.id WHERE m.id=%s ",(mouseID,))  
        if self.d ==[]:
            return "This mouse does not exist"
        self.d=self.d[0]
        
        self.d['experiments']=db.execute("SELECT lab_members.name AS reserve_lab_member, mr.date AS reserve_date, mr.description AS reserve_description, mr.notes AS reserve_notes, mr.status AS reserve_status, mr.filenames AS reserve_filenames  FROM experiments AS mr LEFT JOIN lab_members ON mr.lab_member_id=lab_members.id WHERE mr.mouse_id=%s ORDER BY reserve_date ASC",(self.d['id'],))
        for i in range(len(self.d['experiments'])):
            self.d['experiments'][i]=list(self.d['experiments'][i])
            self.d['experiments'][i][1]=date2str(self.d['experiments'][i][1])
        self.d['experiments'].append(['','','','','',''])        
        # e.g. self.d['genes']=[('PV-Cre', '+-'), ('i-tdTomato', '++')]  
        self.d['genes']=db.execute("SELECT genes.name, zygosity FROM genetics LEFT JOIN genes ON genes.id=genetics.gene_id WHERE genetics.mouse_id=%s",(self.d['id'],))
        self.d['genes'].append(['',''])
        cages=db.execute("SELECT cages.name, h.start_date, h.end_date, h.currentcage FROM housing AS h LEFT JOIN cages ON h.cage_id=cages.id WHERE h.mouse_id=%s ORDER BY h.start_date DESC",(self.d['id'],))
        cages.append(tuple(['','','','']))
        for key in self.d:
            if self.d[key] is None:
                self.d[key]=''
            elif self.d[key]==1 and key!='id':
                self.d[key]='Yes'
            elif self.d[key]==0:
                self.d[key]='No'
        if self.d['DOB'] != '': self.d['DOB']=date2str(self.d['DOB']);
        if self.d['DOD'] != '': self.d['DOD']=date2str(self.d['DOD']);
        if self.d['reserve_date'] != '': self.d['reserve_date']=date2str(self.d['reserve_date']);

        self.d['oldcages']=[]
        self.d['currentcage']=['','']
        for cage in cages:
            if cage[3]==1:
                self.d['currentcage']=[cage[0],date2str(cage[1])]
            elif cage[1] != '' and cage[2] !='':
                self.d['oldcages'].append([cage[0],date2str(cage[1]),date2str(cage[2])])
        self.d['oldcages'].append(['','',''])
    def transfer(self,newcage):
        print(newcage)
        with lock: ## sometimes the javascript calls ajax/moveMouse twice, and they execute concurrently.  This prevents multiple cherrypy threads from calling this function while it is being executed. 
            cage_id=db.execute("SELECT name, start_date FROM housing INNER JOIN cages ON housing.cage_id=cages.id WHERE mouse_id=%s AND currentcage=1",(self.d['id'],))
            today=datetime.datetime.now()
            if cage_id==[]:
                db.execute("INSERT INTO housing SET mouse_id=%s, cage_id=(SELECT id FROM cages WHERE name=%s), start_date=%s, currentcage=1",(self.d['id'],newcage,date2str(today)))
                answer= "{0} placed in {1} on {2}".format(self.d['mousename'],newcage,date2str(today))
            else:
                print(cage_id)
                oldcage=cage_id[0][0]
                if oldcage==newcage:
                    return "{} still in cage {}".format(self.d['mousename'],newcage)
                start_date=cage_id[0][1]
                if date2str(start_date)==date2str(today): #if the old cage's start_date was today, erase mention of the previous cage.  Animals have to have been in a cage for 1 day or more for the record to be kept.  
                    db.execute("UPDATE housing SET cage_id=(SELECT id FROM cages WHERE name=%s) WHERE mouse_id=%s AND currentcage=1",(newcage, self.d['id']))
                else: # if the pretransfer cage didn't have today as its first day:
                    db.execute("UPDATE housing SET currentcage=0, end_date=%s WHERE mouse_id=%s AND currentcage=1",(date2str(today),self.d['id'])) #
                    db.execute("INSERT INTO housing SET mouse_id=%s, cage_id=(SELECT id FROM cages WHERE name=%s), start_date=%s, currentcage=1",(self.d['id'],newcage,date2str(today)))
                ### now merge entries which have the same mouse, cage, and where one entry's stop date is another entries start date.
                overlapping_cages=db.execute("""SELECT h1.cage_id, h2.start_date AS common_date, h1.start_date from housing as h1 INNER JOIN housing AS h2 ON h1.mouse_id=h2.mouse_id AND h1.end_date=h2.start_date AND h1.cage_id=h2.cage_id WHERE h1.mouse_id=%s""",(self.d['id'],))
                for cage in overlapping_cages:
                    db.execute("DELETE FROM housing WHERE mouse_id=%s AND cage_id=%s AND end_date=%s ",(self.d['id'], cage[0], date2str(cage[1])))
                    db.execute("UPDATE housing SET start_date=%s WHERE mouse_id=%s AND cage_id=%s AND start_date=%s ",(date2str(cage[2]), self.d['id'], cage[0], date2str(cage[1])))
                answer= "{0} transfered from {1} to {2} on {3}".format(self.d['mousename'],oldcage,newcage,date2str(today))
            return answer+','+ etree.tostring(getResident(self.d), pretty_print=True)
            
    def removeFromCage(self):
        db.execute("UPDATE housing SET end_date=%s, currentcage=0 WHERE mouse_id=%s AND currentcage=1",(date2str(datetime.datetime.now()),self.d['id']))
        return '{0} is now cageless'.format(self.d['mousename'])
        
    def delete(self):
        db.execute("DELETE FROM mice WHERE id=%s",(self.d['id'],))
        return "Deleted mouse {}".format(self.d['name'])
    def editOldMouse(self,d):
        queries=[]
        ###### check for errors first #######
        if d['mousename'] is None:
            return "You must enter a name"
        d['mousename']=d['mousename'].lower()
        if ' ' in d['mousename']:
            return 'You cannot have spaces in mouse names'
        d['name']=d['mousename']
        id_theif=db.execute("SELECT id FROM mice WHERE name=%s",(d['mousename'],),commit=False)
        if  id_theif != [] and id_theif[0][0]!=int(d['id']):
            return "The name '{}' is already in use. id={},id={}".format(d['mousename'],id_theif[0][0],d['id'])     
        old=self.d
        s=''
        parameters=[]
        for col in set(getAllColumns('mice')) & set(d.keys()):
            if d[col] is not None:
                s+=" m.{}=%s,".format(col)
                parameters.append(d[col])
            else:
                s+=" m.{}=NULL,".format(col)
        s=s[:-1]
        parameters.append(self.d['id'])
        queries.append(['UPDATE mice as m SET {0} WHERE id=%s'.format(s),tuple(parameters)])
                
        ###   LINEAGE   ###
        if d['mother'] == old['mother'] and d['father'] == old['father']:
            pass
        elif d['mother'] is None and d['father'] is None:
            queries.append(["DELETE FROM lineage WHERE child_id = %s",(self.d['id'],)])
        elif (d['mother'] is not None and d['father'] is None) or (d['father'] is not None and d['mother'] is None):
            return 'You need to enter both a mother and a father'
        elif db.execute("SELECT id FROM mice WHERE name=%s",(d['mother'],))==[]:
            return "The mother does not exist"
        elif db.execute("SELECT id FROM mice WHERE name=%s",(d['father'],))==[]:
            return "The father does not exist"
        elif old['mother']=='' and old['father']=='':
            queries.append(["INSERT INTO lineage SET mother_id=(SELECT id FROM mice WHERE name=%s), father_id=(SELECT id FROM mice WHERE name=%s), child_id =(SELECT id FROM mice WHERE name=%s) ",(d['mother'],d['father'],d['mousename'])])
        else:
            queries.append(["UPDATE lineage SET mother_id=(SELECT id FROM mice WHERE name=%s), father_id=(SELECT id FROM mice WHERE name=%s) WHERE child_id =(SELECT id FROM mice WHERE name=%s) ",(d['mother'],d['father'],d['mousename'])])
        ### HOUSING   ###
        if old['currentcage']==['','']:
            if d['cagename'] is not None:
                if db.execute("SELECT id FROM cages WHERE name=%s",(d['cagename'],))==[]:
                    return 'The cage you selected does not exist'
                elif d['startDate'] is None:
                    return "You must add an 'occupied' date for the current cage"
                else:
                    queries.append(["INSERT INTO housing SET mouse_id=(SELECT id FROM mice WHERE name=%s), cage_id=(SELECT id FROM cages WHERE name=%s), start_date=%s, currentcage=1",(d['mousename'],d['cagename'],d['startDate'])])
        elif d['cagename'] == old['currentcage'][0] and d['startDate'] == old['currentcage'][1]: #if the current cage and start date for that cage haven't changed, do nothing
            pass
        elif d['cagename'] is None:
            queries.append(["DELETE FROM housing WHERE mouse_id=%s and currentcage=1",(self.d['id'],)])
        elif d['startDate'] is None:
            return "Your mouse needs to have a date occupied for the current cage"
        elif db.execute("SELECT id FROM cages WHERE name=%s",(d['cagename'],))==[]:
            return 'The cage you selected does not exist'
        elif d['startDate'] is None:
            return "You must add an 'occupied' date for the current cage"
        else:
            queries.append(["UPDATE housing SET cage_id=(SELECT id FROM cages WHERE name=%s), start_date=%s WHERE currentcage=1 AND mouse_id=(SELECT id FROM mice WHERE name=%s)",(d['cagename'],d['startDate'],d['mousename'])])
        
        d['oldcages']=[]
        for cage in d.keys():
            if cage.startswith('oldcagename'):
                n=str(cage.split('oldcagename')[1])
                if d['oldcagename'+n] is not None:
                    if d['startDate'+n] is None or d['endDate'+n] is None:
                        return 'You must add two dates for old cages'
                    if d['startDate'+n]>=d['endDate'+n]:
                        return 'Your cage end date must be greater than the start date'
                    if d['cagename'] is not None and (d['startDate']<=d['startDate'+n] or d['startDate']<d['endDate'+n]):
                        return 'The current cage start date must be after all the other start dates and end dates.'
                    if db.execute("SELECT id from cages WHERE name=%s",(d['oldcagename'+n],))==[]:
                        return 'The cage "{}" does not exist'.format(d['oldcagename'+n])
                    d['oldcages'].append([d['oldcagename'+n], d['startDate'+n], d['endDate'+n]])
        if sorted(d['oldcages'])!=sorted(old['oldcages']):
            queries.append(["DELETE FROM housing WHERE mouse_id=%s AND currentcage=0",(self.d['id'],)])
            n=0
            for cage in d['oldcages']:
                n=n+1
                if db.execute("SELECT id FROM cages WHERE name=%s",(cage[0],))==[]:
                    return "The cage '{}' does not exist".format(cage[0])
                else:
                    queries.append(["INSERT INTO housing SET mouse_id=(SELECT id FROM mice WHERE name=%s), cage_id=(SELECT id FROM cages WHERE name=%s), start_date=%s, end_date=%s, currentcage=0 ",(d['mousename'], d['oldcagename'+str(n)], d['startDate'+str(n)], d['endDate'+str(n)])])

        ### EXPERIMENTS
        newex=[]
        dt=datetime.datetime.today()
        today=datetime.datetime(dt.year,dt.month,dt.day)
        for reserve in d.keys():
            if reserve.startswith('reserve_lab_member'):
                n=reserve.split('reserve_lab_member')[1]
                if d['reserve_lab_member'+n] is not None:
                    try:
                        str2date(d['reserve_date'+n])
                    except (ValueError,AttributeError):
                        return "You must include a calendar date of the format '2016-08-02'"
                    if d['mousename']!=old['mousename']:
                        return "You can't edit a mouse's name if it already has an experiment."
                    if d['reserve_date'+n] is None or d['reserve_description'+n] is None or d['reserve_status'+n] is None:
                        return 'Your experiment needs a date, a type, and a status'
                    if str2date(d['reserve_date'+n])>today and d['reserve_status'+n]=='completed':
                        return "You can't have 'completed' an experiment scheduled for {0}.".format(d['reserve_date'+n])
                    if str2date(d['reserve_date'+n])<today and d['reserve_status'+n]=='planned':
                        return "You can't have a planned experiment scheduled for {0}.".format(d['reserve_date'+n])
                    # there was a bug in the following 3 lines of commented code which deleted all the other users experiments.  I need to fix this in the future but don't have time right now. 
                    #                    if d['reserve_lab_member'+n] != self.username:
                    #                        if len(old['experiments'])>=n and d['reserve_lab_member'+n] != old['experiments'][int(n)-1][0]:
                    #                            return "You can't record or plan experiments for other lab members."
                    else:
                        newex.append([d['reserve_lab_member'+n],d['reserve_date'+n],d['reserve_description'+n],d['reserve_notes'+n], d['reserve_status'+n], d['reserve_filenames'+n]])
                        
                        
        if newex != ['','','','','','']:
            if sorted(self.d['experiments'])==sorted(newex)[:-1]:
                pass
            elif self.d['experiments']!=['','','','','','']:
                queries.append(["DELETE FROM experiments WHERE mouse_id=%s",(self.d['id'],)])
            for x in newex:
                queries.append(["INSERT INTO experiments SET mouse_id=%s, lab_member_id=(SELECT id FROM lab_members WHERE name=%s),date=%s, description=%s, notes=%s, status=%s, filenames=%s ",(self.d['id'],x[0],x[1],x[2],x[3],x[4],x[5])])

        ### GENETICS ###
        newgenes=[]
        for gene in d.keys():
            if gene.startswith('gene'):
                n=gene.split('gene')[1]
                if d['gene'+n] is not None:
                    if d['zygosity'+n] is not None:
                        newgenes.append([d['gene'+n],d['zygosity'+n]])
                    else:
                        return "Select the zygosity of {}".format(d['gene'+n])
        if newgenes != ['','']:
            if sorted(self.d['genes'])==sorted(newgenes):
                pass
            elif self.d['genes']!=['','']:
                queries.append(["DELETE FROM genetics WHERE mouse_id=%s",(self.d['id'],)])
            if len([i[0] for i in newgenes]) > len(set([i[0] for i in newgenes])):
                return 'Your list of genes is not unique'
            for gene in newgenes:
                    queries.append(["INSERT INTO genetics SET mouse_id=%s, gene_id=(SELECT id FROM genes WHERE name=%s), zygosity=%s",(self.d['id'],gene[0],gene[1])])
       

        ### Actually perform the queries. Hopefully there aren't any errors here, as they won't show up in the browser.  
        for query in queries:
            db.execute(query[0],query[1],commit=True)
            
        ### KICK OUT OF HOME IF MOUSE IS SAC'D
        if self.d['life_status']=='alive' and d['life_status']!='alive':
            if old['currentcage'] != ['','']: #if the mouse was in a cage, kick it out
                self.removeFromCage()
                
        return "Mouse updated"
        
    def addToDB(self,d):
        queries=[]
        ###### check for errors first #######
        if d['mousename'] is None:
            return "You must enter a name"
        d['mousename']=d['mousename'].lower()
        if ' ' in d['mousename']:
            return 'You cannot have spaces in mouse names'
        d['name']=d['mousename']
        if db.execute("SELECT id FROM mice WHERE name=%s",(d['mousename'],),commit=False) != []:
            return "The name '{}' is already in use.".format(d['mousename'])     
        ###   MICE   ###
        s=''
        parameters=[]
        for col in set(getAllColumns('mice')) & set(d.keys()):
            if d[col] is not None:
                s+=" {}=%s,".format(col)
                parameters.append(d[col])
        s=s[:-1]
        queries.append(['INSERT INTO mice SET {}'.format(s),tuple(parameters)])
        ###   LINEAGE   ###
        if d['mother'] is not None or d['father'] is not None:
            if (d['mother'] is not None and d['father'] is None) or (d['father'] is not None and d['mother'] is None):
                return 'You need to enter both a mother and a father'
            elif db.execute("SELECT id FROM mice WHERE name=%s",(d['mother'],))==[]:
                return "The mother does not exist"
            elif db.execute("SELECT id FROM mice WHERE name=%s",(d['father'],))==[]:
                return "The father does not exist"
            else:
                queries.append(["INSERT INTO lineage SET mother_id=(SELECT id FROM mice WHERE name=%s), father_id=(SELECT id FROM mice WHERE name=%s), child_id =(SELECT id FROM mice WHERE name=%s)",(d['mother'],d['father'],d['mousename'])])
        ### HOUSING   ###
        if d['cagename'] is not None:
            if db.execute("SELECT id from cages WHERE name=%s",(d['cagename'],))==[]:
                return 'The cage you selected does not exist'
            elif d['startDate'] is not None:
                queries.append(["INSERT INTO housing SET mouse_id=(SELECT id FROM mice WHERE name=%s), cage_id=(SELECT id FROM cages WHERE name=%s), start_date=%s, currentcage=1",(d['mousename'],d['cagename'],d['startDate'])])
            else:
                return "You must add an 'occupied' date for the current cage"
        for cage in d.keys():
            if cage.startswith('oldcagename'):
                n=cage.split('oldcagename')[1]
                if d['oldcagename'+n] is not None:
                    if d['startDate'+n] is None or d['endDate'+n] is None:
                        return 'You must add two dates for old cages'
                    if d['startDate'+n]>=d['endDate'+n]:
                        return 'Your cage end date must be greater than the start date'
                    if d['cagename'] is not None and (d['startDate']<=d['startDate'+n] or d['startDate']<d['endDate'+n]):
                        return 'The current cage start date must be after all the other start dates and end dates.'  
                    if db.execute("SELECT id from cages WHERE name=%s",(d['oldcagename'+n],))==[]:
                        return 'The cage "{}" does not exist'.format(d['oldcagename'+n])
                    queries.append(["INSERT INTO housing SET mouse_id=(SELECT id FROM mice WHERE name=%s), cage_id=(SELECT id FROM cages WHERE name=%s), start_date=%s, end_date=%s, currentcage=0 ",(d['mousename'], d['oldcagename'+n], d['startDate'+n], d['endDate'+n])])                     
                        
                        
        ### EXPERIMENTS
        newex=[]
        dt=datetime.datetime.today()
        today=datetime.datetime(dt.year,dt.month,dt.day)
        for reserve in d.keys():
            if reserve.startswith('reserve_lab_member'):
                n=reserve.split('reserve_lab_member')[1]
                if d['reserve_lab_member'+n] is not None:
                    try:
                        str2date(d['reserve_date'+n])
                    except (ValueError,AttributeError):
                        return "You must include a calendar date of the format '2016-08-02'"
                    if d['reserve_date'+n] is None or d['reserve_description'+n] is None or d['reserve_status'+n] is None:
                        return 'Your experiment needs a date, a type, and a status'
                    elif str2date(d['reserve_date'+n])>today and d['reserve_status'+n]=='completed':
                        return "You can't have 'completed' an experiment scheduled for {0}.".format(d['reserve_date'+n])
                    elif str2date(d['reserve_date'+n])<today and d['reserve_status'+n]=='planned':
                        return "You can't have a planned experiment scheduled for {0}.".format(d['reserve_date'+n])
                    elif d['reserve_lab_member'+n] != self.username:
                        return "You can't record or plan experiments for other lab members."
                    else:
                        newex.append([d['reserve_lab_member'+n],d['reserve_date'+n],d['reserve_description'+n],d['reserve_notes'+n], d['reserve_status'+n], d['reserve_filenames'+n]])

        if newex != ['','','','','','']:
            for x in newex:
                queries.append(["INSERT INTO experiments SET mouse_id=(SELECT id FROM mice WHERE name=%s), lab_member_id=(SELECT id FROM lab_members WHERE name=%s),date=%s, description=%s, notes=%s, status=%s, filenames=%s ",(d['mousename'],x[0],x[1],x[2],x[3],x[4],x[5])])


        ### GENETICS ###
        newgenes=[]
        for gene in d.keys():
            if gene.startswith('gene'):
                n=gene.split('gene')[1]
                if d['gene'+n] is not None:
                    if d['zygosity'+n] is not None:
                        newgenes.append([d['gene'+n],d['zygosity'+n]])
                    else:
                        return "Select the zygosity of {}".format(d['gene'+n])
        if newgenes != ['','']:
            if len([i[0] for i in newgenes]) > len(set([i[0] for i in newgenes])):
                return 'Your list of genes is not unique'
            for gene in newgenes:
                    queries.append(["INSERT INTO genetics SET mouse_id=(SELECT id FROM mice WHERE name=%s), gene_id=(SELECT id FROM genes WHERE name=%s), zygosity=%s",(d['mousename'],gene[0],gene[1])])
                    

        ### Actually perform the queries. Hopefully there aren't any errors here, as they won't show up in the browser.  
        for query in queries:
            db.execute(query[0],query[1],commit=True)
        return "Successfully added '{}'! ".format(d['mousename'])
        
    
    
class Cage:
    def __init__(self, name=''):
        if name != '':
            self.getFromDB(name)
    def getFromDB(self,name):
        self.d=db2.execute("SELECT c.id, c.name AS cagename, c.cagegroup, c.expectingpl, c.notes, c.date_activated, c.date_inactivated, c.location, c.active, m.name, housing.currentcage, housing.start_date, housing.end_date, lab_members.name AS caretaker FROM cages as c LEFT JOIN housing ON housing.cage_id=c.id LEFT JOIN mice as m ON m.id=housing.mouse_id LEFT JOIN care_taker AS ct ON ct.cage_id=c.id LEFT JOIN lab_members ON ct.lab_member_id=lab_members.id WHERE c.name=%s",(name,))
        if self.d ==[]:
            return "This cage does not exist"
        self.d=self.d[0]
        for key in self.d:
            if self.d[key] is None:
                self.d[key]=''
            elif self.d[key]==1 and key!='id':
                self.d[key]='Yes'
            elif self.d[key]==0:
                self.d[key]='No'
        if self.d['date_inactivated'] != '': self.d['date_inactivated']=date2str(self.d['date_inactivated']); 
        if self.d['date_activated'] != '': self.d['date_activated']=date2str(self.d['date_activated']);
        self.mice=db2.execute("SELECT h.mouse_id, m.name, m.id, m.sex, IF(EXISTS(SELECT * from experiments WHERE mouse_id=m.id), 'reserved','notreserved') AS reserved FROM housing AS h INNER JOIN mice AS m ON h.mouse_id=m.id WHERE h.cage_id=%s AND h.currentcage=1",(self.d['id'],))
        
        self.litters=db2.execute("SELECT DOB, mother_id FROM litters WHERE litters.cage_id=%s",(self.d['id'],))
    def editOldCage(self,d):
        s=''
        parameters=[]
        d['name']=d['cagename']
        for col in set(getAllColumns('cages')) & set(d.keys()):
            if d[col] is not None:
                s+=" c.{}=%s,".format(col)
                parameters.append(d[col])
            else:
                s+=" c.{}=NULL,".format(col)
        
        parameters.append(self.d['id'])
        s=s[:-1]
        db.execute("UPDATE cages AS c, care_taker SET {0} WHERE id=%s".format(s),tuple(parameters))
        if d['caretaker']!=self.d['caretaker']:
            db.execute('DELETE FROM care_taker WHERE cage_id=%s',(self.d['id'],))
            if d['caretaker']is not None:
                db.execute("INSERT INTO care_taker SET cage_id=%s, lab_member_id=(SELECT id FROM lab_members WHERE name=%s)",(self.d['id'],d['caretaker']))
        return 'Cage Updated'
        
    def addToDB(self,d): # 
        if d['cagename'] is None:
            return "You must enter a name"
        d['cagename']=d['cagename'].lower()
        d['name']=d['cagename']
        if db.execute("SELECT id FROM cages WHERE name=%s",(d['cagename'],),commit=False) != []:
            return "The name '{}' is already in use.".format(d['cagename'])        
        d_cages={}
        for col in set(getAllColumns('cages')) & set(d.keys()):
            d_cages[col]=d[col]
        columns=', '.join(d_cages.keys())
        parameters = ', '.join(['%({0})s'.format(k) for k in d_cages.keys()])
        query = 'INSERT INTO cages ({0}) VALUES ({1})'.format(columns, parameters)
        db.execute(query,d)
        m_id=db.execute("SELECT id FROM cages where name=%s",(d['cagename'],))[0][0]
        self.d={"id":m_id, 'cagename':d['cagename']}
        
        if d['caretaker'] is not None:
            db.execute("INSERT INTO care_taker SET cage_id=%s, lab_member_id=(SELECT id FROM lab_members WHERE name=%s)",(self.d['id'],d['caretaker']))
        return "Successfully added cage"
        
if __name__=='__main__':
    data='name=testmouse&tag=pop&strain=C57BL/6&sex=female&life_status=alive&breeding_status=unknown&DOB=2013-08-26&DOD=2013-08-20&cause_of_death=flogging&notes=&mother=lalala&father=kite&reserve_lab_member=Ethan&reserve_date=2013-08-07&reserve_description=an experiment&genotyped=True&gene1=i-tdTomato&zygosity1= -&gene2=&zygosity2=&cagename=wt1&startDate=2013-08-26&oldcagename1=&startDate1=&endDate1='
    data=urllib2.unquote(data.replace('+',' '))
    data2=[[b for b in c.split('=')] for c in data.split('&')] #list of lists
    m=Mouse()
    d={}
    for i in data2:
        if i[1]=='':
            d[i[0]]=None
        elif i[1]=='True':
            d[i[0]]=1
        elif i[1]=='False':
            d[i[0]]=0
        else:
            d[i[0]]=i[1] #now in dictionary
    m.addToDB(d)