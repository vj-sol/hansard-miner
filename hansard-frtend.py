#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import sys
import os
import tkinter
#import HansardBkend
from tkinter.ttk import *
import tkinter.scrolledtext as tkst
import requests
import codecs
import csv
import re
import pickle
import progressbar
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
# from progressbar.spinner import Spinner
from subprocess import call
from time import sleep

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")

class popupWindow(object):
  def __init__(self, parent):
    top=self.top=tkinter.Toplevel(parent)
#     tkinter.title(self,'Please select desired candidates:')
    self.l=Label(top,text='Please select desired candidates:')
    self.l.pack()
    self.e=Entry(top)
    self.e.pack()
    self.b=Button(top,text='Search', command=self.cleanup)
    self.b.pack()
  def cleanup(self):
    self.value=self.e.get()
    self.top.destroy()

class hsMiner(tkinter.Tk):
    def __init__(self,parent):
        tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def popup(self):
      self.w=popupWindow(self.parent)
      self.wait_window(self.w.top)

    def initialize(self):
        self.grid()

        self.searchVariable = tkinter.StringVar()
        self.entrysv = tkinter.Entry(self,textvariable=self.searchVariable)
        self.entrysv.grid(column=0,row=0,sticky='EW')
        self.entrysv.bind("<Return>", self.OnPressEnter)
        self.searchVariable.set(u"Enter search term")

        self.startVariable = tkinter.StringVar()
        self.entrystv = tkinter.Entry(self,textvariable=self.startVariable)
        self.entrystv.grid(column=0,row=1,sticky='EW')
        self.entrystv.bind("<Return>", self.OnPressEnter)
        self.startVariable.set(u"Enter start date")
#         stDate = self.startVariable.get()

        self.endVariable = tkinter.StringVar()
        self.entryend = tkinter.Entry(self,textvariable=self.endVariable)
        self.entryend.grid(column=1,row=1,sticky='EW')
        self.entryend.bind("<Return>", self.OnPressEnter)
        self.endVariable.set(u"Enter end date")
#         endDate = self.startVariable.get()

        houses = [("Both",1,0),("Commons",2,1),("Lords",3,2)]
        v = tkinter.IntVar()
        v.set(1)
        for txt, val, pos in houses:
          tkinter.Radiobutton(self, text=txt, value=val, variable=v).grid(column=pos,row=2,sticky='W')

        self.dirVariable = tkinter.StringVar()
        self.entrydir = tkinter.Entry(self,textvariable=self.dirVariable)
        self.entrydir.grid(column=0,row=3,columnspan=3,sticky='EW')
        self.dirVariable.set(os.getcwd())

        button = tkinter.Button(self,text=u"Search Hansard",
                                command=self.OnButtonClick)
        button.grid(column=2,row=4)

        self.labelVariable = tkinter.StringVar()
        label = tkinter.Label(self,textvariable=self.labelVariable,
                              anchor="w",fg="black",bg="white")
        label.grid(column=0,row=5,columnspan=4,sticky='EW')
        self.labelVariable.set(u"Please perform a search...")

        self.text = tkst.ScrolledText(self, wrap="word")
        self.text.grid(column=0,row=7,columnspan=4,sticky='EW')

        sys.stdout = TextRedirector(self.text, "stdout")
#         self.text.pack(side="top", fill="both", expand=True)
#         self.text.tag_configure("stderr", foreground="#b22222")

        self.progress = tkinter.ttk.Progressbar(self, orient='horizontal', mode = 'indeterminate')
        self.progress.grid(column=0,row=6,columnspan=4,sticky='EW')

        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,True)
        self.update()
        self.geometry(self.geometry())
        self.entrysv.focus_set()
        self.entrysv.selection_range(0, tkinter.END)

#         wid = self.winfo_id()
#         os.system('xterm -into %d -geometry 40x20 -sb &' % wid)

    def OnButtonClick(self):
        self.labelVariable.set("Performing search for: " + self.searchVariable.get())
        self.entrysv.focus_set()
        self.entrysv.selection_range(0, tkinter.END)
        ## Perform step 1 - Get search terms
        searchName = self.searchVariable.get()
        searchName = searchName.replace(' ','-')
        searchDateStart = []
        searchDateEnd = []
        searchHouse = []
        #search Record = []

        # Make searchName into url string form
        urlName = searchName.replace('-','%20')

        ## Perform step 2 - Build directory structure

        targcwd = os.getcwd()

        # Set search criteria directory
        searchcritDir = targcwd + "/search-criteria/"

        if os.path.exists(searchcritDir) is False:
            try:
                call(['mkdir',searchcritDir])
            except:
                call(['mkdir',searchcritDir],shell=True)

        # Set storage directory
        storeDir = targcwd + '/stores/'

        if os.path.exists(storeDir) is False:
            try:
                call(['mkdir',storeDir])
            except:
                call(['mkdir',searchDir],shell=True)

        # Set search storage directory
        searchDir = targcwd + "/stores/searches/"

        if os.path.exists(searchDir) is False:
            try:
                call(['mkdir',searchDir])
            except:
                call(['mkdir',searchDir],shell=True)

        # Set text directory
        textDir = targcwd + "/stores/text/"

        if os.path.exists(textDir) is False:
            try:
                call(['mkdir',textDir])
            except:
                call(['mkdir',textDir],shell=True)

        # Set database directory
        dataDir = targcwd + "/databases/"

        if os.path.exists(dataDir) is False:
            try:
                call(['mkdir',dataDir])
            except:
                call(['mkdir',dataDir],shell=True)

        # Set image directory
#        imgDir = "./img/"
#
#       if os.path.exists(imgDir) is False:
#          call(['mkdir',imgDir])

        targdataDir = dataDir+searchName + '/'

        if os.path.exists(targdataDir) is False:
            try:
                call(['mkdir',targdataDir])
            except:
                call(['mkdir',targdataDir],shell=True)

# if os.path.exists(textDir + searchName + '/') is False:
#       call(['mkdir',textDir+searchName])

# Set hansard url handle
        hans = "https://hansard.parliament.uk"


## Perform step 3 - Perform search
# Add searchName to the url that needs to be searched
        htmlString = 'https://hansard.parliament.uk/search?searchTerm=' + urlName

# Begin url requests session
        session = requests.session()

# Perform url request
        req = session.get(htmlString)

# Extract html content
        doc = BeautifulSoup(req.content, 'html.parser')

# Begin aside
# Format html into neat code
# out = doc.prettify("utf-8")

# Transform from byte type to str type
# out = out.decode('utf-8')

# Navigate to cleaner results page
        clnPg = doc.find_all(href=re.compile('Members\?searchTerm'))

        urlHold = []
        for member in clnPg:
          urlHold.append(str(member))

        urlStore = []
        for member in urlHold:
          holder = member.split(' ')
          href = 'href'
          for line in holder:
            if href in line:
              urlStore.append(line)

        clnUrl = urlStore[0].split('"')
        clnUrl = clnUrl[1]
        clnUrl = hans + clnUrl

# make new request with clnUrl
# Perform url request
        reqMem = session.get(clnUrl)

# Extract html content
        docMem = BeautifulSoup(reqMem.content, 'html.parser')

# Get search urls for target search criteria
        target = docMem.find_all(href=re.compile('memberId'))

        urlHold = []
        for member in target:
          urlHold.append(str(member))

        urlStore = []
        for member in urlHold:
          holder = member.split(' ')
          href = 'href'
          for line in holder:
            if href in line:
              urlStore.append(line)

        urlStore = [w.replace('href="', '') for w in urlStore]
        urlStore = [w.replace('"', '') for w in urlStore]
        urlStore = [w.replace('amp;', '') for w in urlStore]
        urlStore = [w.replace('/search', hans+'/search') for w in urlStore]

# Get target speaker names
        spkNames = []
        for crank in target:
          spkNames.append(str(crank.find_all('span')))

        spkNames = [crank.replace('[<span>','') for crank in spkNames]
        spkNames = [crank.replace('</span>]','') for crank in spkNames]

# Get target speaker house
        spkHouse = []
        for crank in target:
          spkHouse.append(str(crank.find_all('div','information house')))

        spkHouse = [crank.replace('[<div class="information house">','') for crank in spkHouse]
        spkHouse = [crank.replace('</div>]','') for crank in spkHouse]

# Get target speaker party
        spkParty = []
        for crank in target:
          spkParty.append(str(crank.find_all('div','information party')))

        spkParty = [crank.replace('[<div class="information party">','') for crank in spkParty]
        spkParty = [crank.replace('</div>]','') for crank in spkParty]

# Get target speaker constituency
        spkConst = []
        for crank in target:
          spkConst.append(str(crank.find_all('div','information constituency-date')))

        spkConst = [crank.replace('[<div class="information constituency-date">\r\n','') for crank in spkConst]
        spkConst = [crank.replace('</div>]','') for crank in spkConst]
        spkConst = [crank.replace('\r\n','') for crank in spkConst]
        spkConst = [crank.replace(' ','') for crank in spkConst]

# Get target speaker member Id
        spkMemid = []
        for crank in urlStore:
#   print(crank)
          crank = [i for i in crank if i.isdigit()]
#   print(crank)
          crank = ''.join(crank)
#   print(crank)
          crank = int(crank)
#   print(crank)
          spkMemid.append(crank)

# Get number of members
        memNo = len(urlStore)

# Create index for data frame
        dfIndex = list(range(0,memNo))

# Create data frame
        datFrame = pd.DataFrame({'name':spkNames,'id':spkMemid,'party':spkParty,'constituency':spkConst,'house':spkHouse,'url':urlStore},index=dfIndex)

# Save data array
# datFrame.to_csv()

## Perform step 4 - Browse and select required results
        print('Found ' + str(memNo) + ' results:')
        print(datFrame[['name','party','constituency','house']])

# At this point the user must select the results they want to return, datSelect will hold the selections
        if memNo > 1:
          self.popup()
# datSelect = []
        datSelect = list(range(0,memNo))
        subdf = datFrame.iloc[datSelect]
        dfurls = subdf['url']
# outDat = 9 members
        count = -1
        for url in dfurls:
          self.progress.start(10)
          tkinter.Tk.update(self)
          count = count+1
          urlReq = session.get(url)
          urlDoc = BeautifulSoup(urlReq.content, 'html.parser')
          urlPg = urlDoc.find_all('a',title=re.compile('Go to last page'))
          urlPg1 = urlPg[0].get('href')
          urlPg2a = urlPg1.split('page=')[0]
          urlPg2b = urlPg1.split('page=')[1]
          urlPgs = list(range(1,int(urlPg2b)+1))
          lastUrl = hans + urlPg2a + 'page=' + str(urlPgs[-1])
          lastPg = session.get(lastUrl)
          lastPghtml = BeautifulSoup(lastPg.content, 'html.parser')
          end = lastPghtml.find('div','results-list row')
          lastLen = len(end.find_all('div','information'))
          noRows = 20*urlPgs[-2]+lastLen
          count2= 0
          dat = pd.DataFrame(np.nan, index = list(range(0,noRows)), columns = ['name','party','constituency','house','id','date','text'])
          targeturls = []
          tkinter.Tk.update(self)
#   bar = progressbar.ProgressBar(max_value=noRows)
          print('\nProccessing ' + datFrame.loc[count,('name')] + ', please wait...')
#           bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
          for targU in urlPgs:
            urlTxt = hans + urlPg2a + 'page=' + str(targU)
            targeturls.append(urlTxt)
            tkinter.Tk.update(self)
          for targPg in targeturls:
            urlSub = session.get(targPg)
            urlSubDoc = BeautifulSoup(urlSub.content, 'html.parser')
            speechurl = urlSubDoc.find_all('div','col-sm-12 result-outer')
            spkurl = []
            tkinter.Tk.update(self)
            for crank in speechurl:
              subcrank = crank.find('a')
              spkurl.append(hans+str(subcrank.get('href')))
              tkinter.Tk.update(self)
            spkurlDup = [crank.split('/') for crank in spkurl]
            spkDup2 = []
            tkinter.Tk.update(self)
            for dupe in spkurlDup:
              spkDup2.append(dupe[-2])
              tkinter.Tk.update(self)
            spkDup2 = list(set(spkDup2))
            coretarg = []
            tkinter.Tk.update(self)
            for trial in spkDup2:
              subcoretarg= []
              tkinter.Tk.update(self)
              for t2 in spkurl:
                if trial in t2:
                  subcoretarg.append(t2)
                  tkinter.Tk.update(self)
              coretarg.append(subcoretarg[0])
              tkinter.Tk.update(self)
            for finalcrank in coretarg:
              finalReq = session.get(finalcrank)
              finalUrl = BeautifulSoup(finalReq.content, 'html.parser')
              urlsrclist = finalUrl.find_all('h2','memberLink')
              finalList = []
              tkinter.Tk.update(self)
              for source in urlsrclist:
                srcpop = source.find('a')
                srcurl = srcpop.get('href')
                spvals = srcurl.split('memberId=')
                spvals = int(spvals[1])
                tkinter.Tk.update(self)
                if spvals == datFrame.id[count]:
                  trgSource = srcpop.parent.parent.parent
                  trgSource = trgSource.find('div','contribution col-md-9')
                  speech = trgSource.find_all('p')
                  name = trgSource.parent.parent.find('a').string
                  date = trgSource.parent.parent.find('span','glyphicon glyphicon-info-sign hidden hidden-xs').get('title')
                  count2 = count2+1
#             dat.name[count2] = str(datFrame.name[count])
                  dat.loc[count2,('name')] = datFrame.loc[count,('name')]
#             dat.party[count2] = str(datFrame.party[count])
                  dat.loc[count2,('party')] = datFrame.loc[count,('party')]
#             dat.constituency[count2] = str(datFrame.constituency[count])
                  dat.loc[count2,('constituency')] = datFrame.loc[count,('constituency')]
#             dat.house[count2] = str(datFrame.house[count])
                  dat.loc[count2,('house')] = datFrame.loc[count,('house')]
                  dat.loc[count2,('id')] = str(datFrame.id[count])
                  dat.loc[count2,('date')] = date
                  dat.loc[count2,('text')] = str(speech)
#         print(name)
#         print(str(count2) + '/' + str(noRows))
#                   bar.update(count2)
                  tkinter.Tk.update(self)


          name = datFrame.name[count]
          finalDir = targdataDir + name
          if os.path.exists(finalDir) is False:
              try:
                  call(['mkdir', finalDir])
              except:
                  call(['mkdir', finalDir],shell=True)
                  
          fileName = name + '.csv'
          fileDir = finalDir + '/' + fileName
#     print(fileDir)
          dat.to_csv(fileDir)
          self.progress.stop()

        print('\nAll done, database(s) stored in ' + targdataDir)
#         print(self.searchVariable.get())
#         print(self.endVariable.get())

    def OnPressEnter(self,event):
        self.labelVariable.set("Performing search for: " + self.searchVariable.get())
        self.entrysv.focus_set()
        self.entrysv.selection_range(0, tkinter.END)
#         print(self.startVariable.get())
#         print(self.endVariable.get())

if __name__ == "__main__":
    app = hsMiner(None)
    app.title('Hansard Miner')
    img = tkinter.PhotoImage(file='./parliament-uk-logo.gif')
    app.call('wm', 'iconphoto', app._w, img)
#     app.wm_iconbitmap(bitmap='@/home/vijay/Documents/Strath/scripts/python/parliament-uk-logo.xbm')
    app.mainloop()
