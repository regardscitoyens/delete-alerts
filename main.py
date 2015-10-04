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

for i in range(nbmessages):  
  expcnt = 0  
  for msg in mailbox.retr(i+1)[1]:    
  
    for line in msg.split('\n'):
      
      if re.search("^From:[^<]{1,}<([^>]{1,})>", line):
        exp = re.sub(r'^From:[^<]{1,}<([^>]{1,})>', r'\1', line)
        expcnt += 1
        
        # expéditeur autorisé :
        if exp in conf['authorized_senders']:
          auth = True
        else:
          auth = False
      
      if re.search("nosdeputes", line):
        url = 'http://www.nosdeputes.fr/alerte/delete/'
        
      if re.search("nossenateurs", line):
        url = 'http://www.nossenateurs.fr/alerte/delete/'
      
      if re.search("edit/(.{32})$", line):
        m = re.search("edit/(.{32})$", line)
        alerteid = m.group(1)
        
        if auth and expcnt == 1:
          subprocess.call([os.path.join(dirpath, 'delete.sh'), url, alerteid, exp.split('@')[0]], shell=False)
      
  mailbox.dele(i+1)

mailbox.quit()
