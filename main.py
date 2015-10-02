#! /usr/bin/env python
# -*- coding: utf8 -*-
import sys, re, json, getpass, poplib, subprocess

with open('config.json') as conf_file:    
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
          subprocess.call(["./delete.sh", url, alerteid, exp.split('@')[0]], shell=False)
      
  #mailbox.dele(i+1)
  print 'delete msg %d' % (i+1)

status = mailbox.stat()
print "Mailbox has %d messages for a total of %d bytes" % (status[0], status[1])

mailbox.quit()
