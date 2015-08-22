# -*- coding: UTF-8 -*-


import re
import json
import urllib2, urllib, requests
from operator import itemgetter
#from collections import OrderedDict
import itertools as iter

def parse_file(annotations):
   try:
      data=json.loads(annotations)
      return data
   except:
      print annotations 
      return {"Annotations":[]}

def has_digit(texto):
  for l in texto:
    if l.isdigit():
      return True
  return False

def get_other_marks(texto):
   
   result = []
   texto=texto.replace("with regard to","with_regard_to")
   #longitud = 0
   offset=0

   for line in texto.split('\n'):
     
     for sent in line.split(". "):
       first=True
       for token in sent.split(" "):

         if len(token)==0: 
            #offset+=1
            continue

         t_clean = token

         t_clean = t_clean.replace("(", "")
         t_clean = t_clean.replace(")", "")
         if t_clean.endswith(":"):
           t_clean = t_clean[:-1]

         t_clean = t_clean.replace(",", "")
         t_clean = t_clean.replace(".", "")
         t_clean = t_clean.replace(";", "")
         t_clean = t_clean.replace("'s", "")
         t_clean = t_clean.replace("(", "")
         t_clean = t_clean.replace(")", "")
         # [code, pos, match, color, src, grp, score, cui, idf, ids, length]
         
         #print token,"->",texto[offset:offset+10]
         #print t,t_clean,start,first

         pos=-1
         if t_clean.lower() in ["there","besides","which","though","since","despite","that","when","where","and","would","with"]:
           pos = texto.find(t_clean, offset)
           result.append([0, pos, t_clean, '#000000', "", "STOP", 1, "", "", "", "", len(t_clean)])
           #print t,t_clean,"->",pos,texto[pos:pos+len(t_clean)]
           #print start,texto[start:pos+20]

         elif not t_clean.isdigit() and t_clean.upper()==t_clean and 0<len(t_clean)<4 and t_clean not in ['I','X','Y','CGH']:
           pos = texto.find(t_clean, offset)
           result.append([1, pos, t_clean, '#81BEF7', "", "PEOP", 1, "", "", "", "", len(t_clean)])
           print token,t_clean,"->",pos,texto[pos:pos+len(t_clean)]
           print pos-offset

         elif not first and not t_clean.isdigit()  and len(t_clean)==2 and t_clean[0].capitalize()==t_clean[0]:
           pos = texto.find(t_clean, offset)
           result.append([1, pos, t_clean, '#81BEF7', "", "PEOP", 1, "", "", "", "", len(t_clean)])
           #print pos-offset

         first=False
         if pos>0: offset=pos+len(token)-1
         else: offset+=len(t_clean) 
        
       #offset+=1 #setence
     #offset+=1 #paragraph

   #no offset displacement should be done at sentence or paragraph?

   return result

def split_per_name(total, texto): #NOW not used -> find_associations!
  per_names = [] 
  new_person = [[],[]] # [[name1,name2], [info1,info2,info3]]
  i = 0
  code_ant = -1  
  while i < len(total):
    code_actual = total[i][0]
    if code_actual == 1 and code_ant == 1: # seguimos misma persona
      new_person[0].append(total[i])
    elif code_ant == 1 and code_actual != 1: # empieza info de una persona
      new_person[1].append(total[i])
    elif code_ant != 1 and code_actual == 1: # persona nueva
      if len(new_person[0]) != 0:
        per_names.append(new_person)
      new_person = [[],[]]
      new_person[0].append(total[i])
    elif code_ant != 1 and code_actual != 1: # mas info
      new_person[1].append(total[i])
    code_ant = total[i][0]
    i += 1
  result = {} #OrderedDict()
  for group in per_names:
    names = group[0]
    syms = group[1]
    if len(names) == 1:
      result[names[0][2]] = syms
    else:
      n_ant = names[-2]
      n = names[-1]
      ty = n[9]
      ty_ant = n_ant[9]
      pos = n[1]
      pos_ant = n_ant[1]
      if ty_ant == '' and (ty == 'T099' or ty == 'T100'):
         if pos - (pos_ant + len(names[-1][2])) <= 3:
           result[texto[pos_ant: pos] + names[-1][2]] = syms
  return result


def find_associations(total,texto):

  #find associations in annotations of patients
  
  output={}
  #pivot elements (mainly observations and hpo annotations)
  obsv=[0]+[total.index(ann) for ann in total if ann[0] in [0,2]]+[len(total)]
  patient_ant=""
  for i in range(1,len(obsv)-1):
      ann=total[obsv[i]]

      if ann[0]==0: continue
      association=['']*9
      association[1]=ann[2]

      #look for associations in the nearest entities within the boundaries
      poscs=find_partners(total,obsv[i],start=obsv[i-1],end=obsv[i+1])

      #determine the patient and group associations around it
      if True:
         for code in poscs.keys(): 
             partner=total[poscs[code]]
             if code>0:
                association[code-1]=partner[2] #match of the annotation
         if association[0]!='':
            patient=association[0]
            patient_ant=patient
         else:
            association[0]=patient_ant
            patient=patient_ant
         if len(patient)>0:
            if output.has_key(patient): output[patient].append(association)
            else: output[patient]=[association]

  return output
  
  #return result

def find_partners(lista,posicion,start=0,end=0):
   candidates={}
   uid_ref=".".join(lista[posicion][10].split(".")[:2])
   pos_ref=lista[posicion][1]
   for pos in range(start+1,end):
       ann=lista[pos]
       code,uid=ann[0],".".join((ann[10].split("."))[:2])
       annpos=ann[1]
       if code!=2 and code>0 and (uid==uid_ref or uid==""):
         if candidates.has_key(code): candidates[code].append(pos)
         else: candidates[code]=[pos] 
   for k in candidates:
       candidates[k].sort(key=lambda x:abs(x-posicion))
       #group consecutive annotations of the same code??
       candidates[k]=candidates[k][0]
   return candidates

def change_total(total):  ##to remove??
  new_total = []
  pos_ant = -1
  len_ant = 0
  for elem in total:
    pos = elem[1]
    if pos != pos_ant and pos >= pos_ant + len_ant:
      new_total.append(elem)
    #else:
    #  print "discarded",elem
    pos_ant = pos
    len_ant = elem[-1]
  return new_total

def change_group(x,sgrs):
  x['grp']=min(sgrs)
  return x

def choose_one(lann):
  sgrs=set([ann['grp'].split(".")[0] for ann in lann])
  out=[ann for ann in lann if ann['src']==u'hpo']
  if len(out)==0:
     if len(set(["ANAT","CELL","GENE"]) & sgrs):
        return [ann for ann in lann if ann['grp'].split(".")[0] in ["ANAT","CELL","GENE"]]
     else:
        return [min(lann)]
  else:
     return map(lambda x:change_group(x,sgrs),out)

def choose_color_code(src,grp):
  color,code = "",-1
  if src == u"shifters":
    color = "#A9F5A9"
    code = 3
  elif src== u"umls2012ab_family": # familia
    color = "#81BEF7"
    code = 1
  elif src== u"umls2012ab_modifiers": # or ty == u"T080" or ty == u"T081" or ty == u"T169": # modificadores
    color = "#F4FA58"
    code = 4
  elif src == u"hpo":
    color = "#BD7AFF"
    code = 2
  elif src in [u"umls2012ab_gene_disorders",u"umls2012ab_omim",u"umls2012ab_hpo",u"umls2012ab_congenital"] and grp in ["DISO","OBSV","ACTI","CONC"]:
    color = "#FA5858"
    code = 2
  elif grp in ["GENE","CELL","ANAT","PHYS","PROC"]  or src in [u"umls2012ab_gene_loci","umls2012ab_gene_names"]: # GENE
    color = "#FF9900"
    code = 5
  return (color,code)

def align_offsets(Lann,texto):
  offset_ant , start = -1 , 0
  fixedAnn=[]
  #Lann.sort(key=lambda x:x['offset'])
  for i in range(len(Lann)):
    a=Lann[i]
    #print a['match'],a['src'],a['grp'],a['offset']
    offset=a['offset']
    flag=True
    if offset==offset_ant: 
      if pos!=-1:
         a['offset']=pos
      else: 
         print "Warning: annotation not found in text ->",a['match']
         #print "\t",text[offset_ant-10:a['offset']+a['len']+10]
         flag=False
    else:
      pos=texto.find(a['match'],start)
      start = pos + 1
      if pos != -1:
        a['offset']=pos
      else:
        print "Warning: annotation not found in text ->",a['match']
        flag=False
    if flag: 
      fixedAnn.append(a)
    offset_ant=offset

  return fixedAnn
  
def extract_all(texto):
 url = u'http://monster.dlsi.uji.es:8081/query/hpo/q='
 url_completa = url + texto
 response = ""
 try:
   response = requests.get(url_completa).text
 except requests.ConnectionError, e:
   print e
 
 total = get_other_marks(texto)

 data = parse_file(response)

 Annotations = align_offsets(data['Annotations'],texto)

 start = 0
 procAnn=[]

 for ann in Annotations:
    if ann['src']==u'hpo': print ann

 
 #group by sentence
 for (k,grupo1) in iter.groupby(Annotations,key=lambda x:x['id'].split(".")[:-1]):
     
     offset_ant,len_ant=-1,0
     
     #group annotations with same offset and length
     for (k2,grupo2) in iter.groupby(sorted(grupo1,key=lambda x:(x['offset'],-x['len'])),key=lambda x:(x['offset'],x['len'])):

        anns=choose_one([e for e in grupo2])
        #print k2, anns
      
        for ann in anns:
          
          ann['color']=''
          ann['code']=-1
          ann['grp']=ann['grp'].split(".")[0]

          offset,length = ann['offset'],ann['len']

          if offset_ant+len_ant > offset: #overlapped annotation (this doesn't work)
             #merge ann_ant
             print "merging annotations"
             ann_ant=procAnn[-1]
             (new_color,new_code)=choose_color_code(ann['src'],ann['grp'])
             if new_color!="":
                match=ann_ant['match'][:offset-offset_ant]+ann['match']
                #start=max(offset_ant-3,0)
                #pos=texto.find(match,start)
                procAnn[-1]['match']=match
                procAnn[-1]['len']  =len_ant-(offset_ant-offset)
                procAnn[-1]['color']=new_color
                procAnn[-1]['code'] =new_code
                
          else:
             #u'src': u'UMLS', u'grp': u'OBSV', u'len': 14, u'score': Decimal('2.5947990442421545'), 
             #u'cui': u'C1861337', u'offset': 3552, u'idf': 21, u'type': u'T033', u'id': u'rest.e204', 
             #u'match': u'palmar creases'}
             if texto[ann['offset']:ann['offset']+ann['len']]!=ann['match']:
                print "\tWarning: some offset misalignment ?",ann['match'],
                print ann['offset'],texto[ann['offset']:ann['offset']+ann['len']]
             (color,code)=choose_color_code(ann['src'],ann['grp'])
             if code!=-1:
                ann['color']=color
                ann['code']=code
                procAnn.append(ann)
             else:
                print "Disregarded: ",ann

             #total.append([code, pos, match, color, src, grp, score, cui, idf, ty, ids, length])

        (offset_ant,length_ant) = k2
 
 
 total.extend(map(lambda x:[x[k] for k in ['code','offset','match','color','src','grp','score','cui','idf','type','id','len']],procAnn))
 
 dicc_res = {} #OrderedDict()
 for t in total: #preserve the order of insertion in total
   if t[0]==0: continue ##fake annotation for association finding
   pos = t[1]
   #print "::",pos,texto[pos:pos+t[-1]]
   if dicc_res.has_key(pos):
     if len(dicc_res[pos]) == 1 and dicc_res[pos][0][0] == 1: # si hay una etiqueta de persona, descartamos las demas
       pass
     elif t not in dicc_res[pos]: # no repetir anotaciones
       dicc_res[pos].append(t)
   else:
     dicc_res[pos] = [t]

 #total = change_total(total)

 total = sorted(total, key=itemgetter(1))

 per_names = find_associations(total, texto)

 #now we return the ordered list of colored annotations
 return sorted(dicc_res.items()), per_names

