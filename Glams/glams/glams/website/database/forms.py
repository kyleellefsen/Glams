# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 11:55:02 2013

@author: kyle
"""
from lxml import etree
from lxml.builder import E
import datetime
from glams.databaseInterface.connect import db, db2
import unicodedata

   
def date2str(d):
    if d is None:
        return ''
    else:
        return d.isoformat().strip().split('T')[0]

v={}
def textinput(name,otherattributes={}):
    global v
    value=v[name]
    if value is None: value=''
    a={'type':'text','name':name,'value':value}
    a=dict(a.items()+otherattributes.items())
    return E.input(a)
def select(name,selectvalues=[], otherattributes={}):
    global v
    value=v[name]
    if value is None: value=''
    answer=etree.Element('select',otherattributes)
    answer.set('name',name)
    for val in selectvalues:
        option=etree.Element('option')
        option.text=val
        if val==value:
            option.set('selected','selected')
        answer.append(option)
    return answer
def dateinput(name, otherattributes={}):
    global v
    value=v[name]
    if value is None: value=''
    a={'type':'date','name':name,'value':value}
    a=dict(a.items()+otherattributes.items())
    return E.input(a)
def textarea(name, otherattributes={}):
    global v
    value=v[name]
    if value is None: value=''
    a={'name':name}
    a=dict(a.items()+otherattributes.items())
    return E.textarea(a,value)
def numinput(name, otherattributes={}):
    global v
    value=v[name]
    if value is None: value=''
    a={'type':'number','step':'1','name':name}
    a=dict(a.items()+otherattributes.items())
    return E.input(a)







################################################################################################################
######################  CREATE MOUSE FORM ######################################################################
################################################################################################################
def getGeneList():
    genelist=db.execute("SELECT name FROM genes")
    answer=['']
    answer.extend([gene[0] for gene in genelist])
    return answer
def getStrainList():
    strainlist=db.execute("SELECT name FROM strains")
    answer=['']
    answer.extend([strain[0] for strain in strainlist])
    return answer
def getLabMemberList():
    labmemberlist=db.execute("SELECT name FROM lab_members")
    answer=['']
    answer.extend([lm[0] for lm in labmemberlist])
    return answer
def getBreedingStatusList():
    return ['','breeding','retired breeder','virgin','unknown']
def getLifeStatusList():
    return ['', 'alive','euthanized','missing','transferred']
def getSexList():
    return ['unknown', 'male', 'female']
def getZygosityList():
    return ['','++','+-','--','+?','-?','??','+/y','+/x']   
def getExperimentStatusList():
    return ['planned','completed']

   
def getMouseForm(oldval={}):
    global v
    mousebasev={'id':'','mousename':'','tag':'','strain':'','sex':'','life_status':'alive','breeding_status':'virgin',
   'DOB':date2str(datetime.datetime.now()),'DOD':'','cause_of_death':'','notes':'',
   'mother':'','father':'','reserve_lab_member1':'','reserve_date1':'','reserve_description1':'','reserve_filenames':'',
   'reserve_notes1':'','genotyped':'','gene1':'','zygosity1':'','cagename':'','startDate':'','oldcagename1':'','startDate1':'','endDate1':''}
   
    v=dict(mousebasev.items()+oldval.items())
    if oldval=={}: #if this is a new mouse form
        header='Add Mouse'
        v['genes']=[['','']]
        v['oldcages']=[['','','']]
        v['experiments']=[['','','','','','']]
    else: #if we are editing an old mouse
        header=oldval['mousename']
        v['cagename']=oldval['currentcage'][0]
        v['startDate']=oldval['currentcage'][1]  
        v['notes']=oldval['mouse_notes']
    basicfields= E.fieldset(
        E.div(  E.input({'type':'hidden','name':'id','value':str(v['id'])})),
        E.div(  E.label('Name:'),             textinput('mousename')),
        E.div(  E.label('Tag:'),              textinput('tag')),
        E.div(  E.label('Strain:'),           select('strain',getStrainList())),
        E.div(  E.label('Sex:'),              select('sex',getSexList())),
        E.div(  E.label('Life Status:'),      select('life_status',getLifeStatusList())),
        E.div(  E.label('Breeding Status:'),  select('breeding_status',getBreedingStatusList())),
        E.div(  E.label('Date of Birth:'),    dateinput('DOB')),
        E.div(  E.label('Date of Death:'),    dateinput('DOD')),
        E.div(  E.label('Cause of Death:'),   textinput('cause_of_death')),
        E.div(  E.label('Notes: '),           textarea('notes',{'rows':'10', 'cols':'30'})),
    )
    parentfields= E.fieldset(
        E.div(  E.label("Mother's name:"),    textinput('mother')),
        E.div(  E.label("Father's name:"),    textinput('father')),
    )
    ###########################################################################
    ##########        EXPERIMENTS     #########################################
    experimentfields= E.fieldset({'class':'exp_list_holder'})
    n=1
    for experiment in v['experiments']:
        v['reserve_lab_member'+str(n)]=experiment[0]
        v['reserve_date'+str(n)]=experiment[1]
        v['reserve_description'+str(n)]=experiment[2]
        v['reserve_notes'+str(n)]=experiment[3]
        v['reserve_status'+str(n)]=experiment[4]
        v['reserve_filenames'+str(n)]=experiment[5]
        if experiment[3] is None:
            reserve_notes=''
        else:
            reserve_notes=experiment[3]
        try:
            E.span(reserve_notes)
        except:
            print("reserve_notes = {}".format(reserve_notes))
            #reserve_notes="".join([i for i in reserve_notes if ord(i) < 127])
        experimentfields.append(        
            E.div({'class':'reserveSelect'},
                E.label("Experiment by:"),    select('reserve_lab_member'+str(n),getLabMemberList(),{'class':'reservenamelist','onblur':'removeReserveSelect(this);'}),
                E.span('on'),                dateinput('reserve_date'+str(n), {'class':'reserve_date'}),
                E.span('for'),               textinput('reserve_description'+str(n),{'class':'reserve_description','onfocus':"if (this.value == 'an experiment') {this.value = '';}", 'onblur':"if (this.value == '') {this.value = 'an experiment';}"}),
                E.span('status:'),           select('reserve_status'+str(n),getExperimentStatusList(), {'class':'reserve_status'}), 
                E.span('File names:'),        textinput('reserve_filenames'+str(n),{'class':'reserve_filenames'}),                    
                E.span('Experiment Notes:'),  E.div({'class':'reserve_notes reserve_notes'+str(n), 'name': 'reserve_notes'+str(n),'contentEditable':'true'}, reserve_notes)    #textarea('reserve_notes'+str(n), {'rows':'8', 'cols':'50', 'class':'reserve_notes'})
        ))
        n+=1
    
    ###########################################################################
    ##########        GENES      ##############################################
    genefields= E.fieldset(
        E.div(  E.label('Genotyped?'),         select('genotyped',['No','Yes'])),
    )
    n=1
    for gene in v['genes']:
        v['gene'+str(n)]=gene[0]
        v['zygosity'+str(n)]=gene[1]
        genefields.append(E.div({'class':'geneselect'}, 
              E.label('Select a gene:'),     
              select('gene'+str(n),getGeneList(), {'class':'genelist','onblur':"removeGeneSelect(this);"}),
              select('zygosity'+str(n),getZygosityList(),{'class':'zygosity'})
        ))
        n+=1
        
    ###########################################################################
    ##########        Cages      ##############################################
    cagefields= E.fieldset(
        #"displaycage('{}');".format(v['cagename'])
        E.div( E.label({'onclick':"displaycage($(this).next().val());"},'Current Cage:'), textinput('cagename'), E.span('occupied'), dateinput('startDate'), E.span('to present')),
    )
    n=1
    for oldcage in v['oldcages']:
        v['oldcagename'+str(n)]=oldcage[0]
        v['startDate'+str(n)]=oldcage[1]
        v['endDate'+str(n)]=oldcage[2]
        cagefields.append(E.div( {'class':'cageHistorySelect'},
            E.label({'onclick':"displaycage($(this).next().val());"},'Old Cage:'), textinput('oldcagename'+str(n),{'onblur':'removecageHistorySelect(this);'}), 
            E.span('occupied'), dateinput('startDate'+str(n)), 
            E.span('to'), dateinput('endDate'+str(n)))
            )
        n+=1
  
    
    bubble =  E.div(
        E.h1(header),
        E.div({'id':'mouseAlert','style':'display:none; background-color:yellow;position:absolute;right:0px;'},'l'),
        E.div({'class':'tabs'},
            E.ul(E.li(E.a({'href':'#tab1'},'Mouse')), E.li(E.a({'href':'#tab2'},'Experiments')),E.li(E.a({'href':'#tab3'},'Genealogy'))),
            E.form({'id':'editmouse'},             
                E.div({'id':'tab1'},
                    E.div({'style':'float:left;'},basicfields),
                    E.div({'style':'float:left;'},parentfields, genefields, cagefields)
                ),
                E.div({'id':'tab2'},experimentfields),
                E.div({'id':'tab3'},E.fieldset('Coming Soon!')),
                E.div( E.input({'class':'button-link','style':'float:right; bottom: 10px; right: 10px; white-space:nowrap;','type':'submit'}))
            ),
        ),
        E.img({'class':'close_button','src':'/support/images/x.gif','onclick':"closePopup('.bubble')"})
    )
    return etree.tostring(bubble, pretty_print=True)







################################################################################################################
######################  CREATE CAGE FORM        ################################################################
################################################################################################################
    
def getAge(DOB):
    if type(DOB) != type(datetime.datetime.today()):
        return 'no DOB'
    else:
        return 'P'+str((datetime.datetime.today()-DOB).days)
        

def getResident(r):
    return E.span({'class':'resident '+str(r['sex'])+' '+r['reserved']},
                       E.span({'class':'mousename','mouseID':str(r['id'])},r['name']),
                       E.span({'class':'x_mouse'},E.img({'src':'/support/images/x.gif','onclick':'removeMouseFromCage(this);'}))
                 )

def getInnerCageForm(username, oldval={}, residents=[],litters=[],history=[]):
    '''This function is called by 'getCageForm' in this file and ajax.refreshcage'''
    global v
    cagebasev={'cagename':'','active':'','date_activated':date2str(datetime.datetime.now()),'date_inactivated':'',
           'location':'','expectingpl':'No','caretaker':username,'cagegroup':'','notes':''}
           
    v=dict(cagebasev.items()+oldval.items())
    if oldval=={}: #if this is a new mouse form
        header='New Cage'
    else: #if we are editing an old mouse
        header=oldval['cagename']
        
    basicfields=E.fieldset(
        E.div(E.label('Name:'),             textinput('cagename')),
        E.div(E.label('Active?'),           select('active',['Yes','No'])),
        E.div(E.label('Date Activated:'),   dateinput('date_activated')),
        E.div(E.label('Date Inactivated:'), dateinput('date_inactivated')),
        E.div(E.label('Location:'),         textinput('location')),
        E.div(E.label('Breeding?'),         select('expectingpl',['Yes','No'])),
        E.div(E.label('Care Taker:'),       select('caretaker',getLabMemberList())),
        E.div(E.label('Cage Group:'),            textinput('cagegroup')),
        E.div(  E.label('Notes: '),         textarea('notes',{'rows':'6', 'cols':'20'}))
    )
    reslist=E.div({'style':'float:left;','class':'residents'})
    for r in residents:
        reslist.append(getResident(r))
    for l in litters:
        cageDOBmotherid="cage_id={}&DOB={}&mother_id={}".format(v['id'],date2str(l['DOB']),l['mother_id'])
        reslist.append(E.span({'class':'resident'},
                          E.span({'class':'pl','cageDOBmotherid':cageDOBmotherid}),'PL ({})'.format(getAge(l['DOB']))
                          ))
    reslist.append(E.a({'class':'button-link','style':'float:right;padding: 2px;','onclick':"addPLForm('{}')".format(v['cagename'])},'+PL'))
    histlist=E.table({'class':'historytable'})
    for h in history:
        histlist.append(E.tr(
            E.td({'class':'historydate'}, date2str(h[0])),
            h[1]
            )
        )
    histlist=E.div({'class':'hist_table_holder'},histlist)
        
    innerform=E.div(     E.h1(header),
                    E.div({'class':'cageAlert','style':'display:none; background-color:yellow;position:absolute;right:0px;white-space:nowrap;'},'l'),
                    E.div({'class':'tabs'},
                        E.ul(E.li(E.a({'href':'#tab1'},'Cage')), E.li(E.a({'href':'#tab2'},'History')),E.li(E.a({'href':'#tab3'},'Residents'))),
                        E.form(            
                            E.div({'id':'tab1'},
                                E.div(basicfields),
                                E.div( E.input({'class':'button-link','style':'float:right; bottom: 10px; right: 10px;','type':'submit'}))
                            ),
                            E.div({'id':'tab2'},histlist),
                            E.div({'id':'tab3'}, reslist)
                        ),
                    ),
                    E.img({'class':'close_button','src':'/support/images/x.gif','onclick':"$(this).parents('.cage').remove();"}),
                    )
    return innerform
    
    
    
def getCageForm(username, oldval={},cageN=1,residents=[],litters=[],history=[]):
    
    bubble =  E.div({'style':'top:{0}px;left:{0}px;'.format(30+int(cageN)*10),'class':'cage'},
                     getInnerCageForm(username, oldval, residents,litters,history)
              )
    return etree.tostring(bubble, pretty_print=True)
    
def getGeneticFilterForm():
    global v
    v['gene0']='gene0'
    v['zygosity0']='zygosity0'
    v['gene1']='gene1'
    v['zygosity1']='zygosity1'
    v['logiccomb0']='logiccomb0'
    v['logiccomb1']='logiccomb1'
    genefields= E.fieldset()
    genefields.append(E.div({'class':'geneselect'}, 
          select('logiccomb0',['AND','OR','NOT'],{'class':'logiccomb','style':'visibility:hidden;'}),
          select('gene0',getGeneList(), {'class':'genelist', 'onblur':'removeGeneSelectFilter(this);'}),
          select('zygosity0',getZygosityList(),{'class':'zygosity'})
    ))
    genefields.append(E.div({'class':'geneselect'}, 
          select('logiccomb1',['AND','OR','NOT'],{'class':'logiccomb','onblur':'removeGeneSelectFilter(this);'}),
          select('gene1',getGeneList(), {'class':'genelist', 'onblur':'removeGeneSelectFilter(this);'}),
          select('zygosity1',getZygosityList(),{'class':'zygosity'})
    ))
    return etree.tostring(genefields, pretty_print=True)
    
def getResidentsFilterForm():
    global v
    v['age0']='age0'
    v['age1']='age1'
    agefield=E.fieldset()
    agefield.append(E.div(
            E.span('Ages between '),
            numinput('age0'),
            E.span('and'),
            numinput('age1')
    ))
    return etree.tostring(agefield, pretty_print=True)
    

if __name__=='__main__':
    f=open('C:/Users/kyle/Desktop/blah.html','w')
    f.write(getMouseForm())
    f.close()

















