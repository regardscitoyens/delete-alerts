#! /usr/bin/env python
# -*- coding: utf8 -*-
import sys, os, re, json, getpass, poplib, subprocess

dirpath = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(dirpath, 'config.json')) as conf_file:    
  conf = json.load(conf_file)

mailbox = poplib.POP3(conf['host'].encode('utf-8'))

try:
  mailbox.apop(conf['user'].encode('utf-8'), conf['password'].encode('utf-8'))
except poplib.error_proto:
  try:
    mailbox.user(conf['user'].encode('utf-8'))
    mailbox.pass_(conf['password'].encode('utf-8'))
  except poplib.error_proto, e:
    print conf['user'].encode('utf-8')+" login failed:", e
    sys.exit(1)

nbmessages = len(mailbox.list()[1])
nbtodel = 0

for i in range(nbmessages): 
  exp = []
  dest = 'Utilisateur indéterminé'
  keywords = 'Alerte indéterminée'
  data = mailbox.retr(i+1)[1]
  datastr = re.sub('> ', '', ' '.join(data))
  
  if re.search('alertes de votre abonnement', datastr):
    k = re.search('alertes de votre abonnement \: ([^-]{1,})-', datastr)
    keywords = k.group(1)
  
  for line in data: 
      
    if re.search("^From:[^<]{1,}<([^>]{1,})>", line):
      exp.append(re.sub(r'^From:[^<]{1,}<([^>]{1,})>', r'\1', line))
      
      # expéditeur autorisé :
      if unicode(exp[0]) in conf['authorized_senders']:
        auth = True
      else:
        auth = False
    
    if re.search("nosdeputes", line):
      url = 'http://www.nosdeputes.fr/alerte/delete/'
      
    if re.search("nossenateurs", line):
      url = 'http://www.nossenateurs.fr/alerte/delete/'
    
    if re.search("^> To: ", line):
      d = re.search("^> To: (.{1,})", line)
      dest = d.group(1)
    
    if re.search("(edit|delete)/(.{32})$", line):
      m = re.search("(edit|delete)/(.{32})$", line)
      alerteid = m.group(2)
      
      if auth:
        subprocess.call([os.path.join(dirpath, 'delete.sh'), keywords, url, alerteid, dest, exp[0].split('@')[0].title()], shell=False)
        nbtodel += 1
        break
      else:
        print "Message de %s supprimé sans traitement (expéditeur non autorisé ou message \"bouncé\")" % exp
      
  mailbox.dele(i+1)

if nbtodel >= 1:
  print "# Pour supprimer d'autres alertes, envoyez moi l'email \"undelivered\" "
  print "# (ou sa pièce jointe .eml s'il en comporte une) à %s (en réponse ou en fwd)" % conf['user'].encode('utf-8')

mailbox.quit()
