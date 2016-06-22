#!/usr/bin/env python 

#RMS 2016
#Main GUI class for QuakeWatch program

print 'Importing modules....'

from Tkinter import *
from point_browser import *
import matplotlib 
import numpy as np
import time
import datetime
import os
import cat_analysis as quaketools
from obspy import UTCDateTime

#Import obspy modules for fetching event data 
from quitter import Quitter

#Allow matplotlib to be used within a tkinter canvas
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm 

#Control matplotlib font size
matplotlib.rcParams.update({'font.size': 6})


#This class handles the mouse-click options
Browse = PointBrowser()

print 'Done imports'

###########################################
#GUI base class for BayQuake 
###########################################

class QWGUI(Frame):
	'''Base class controlling QuakeWatch GUI aspects'''

	def __init__(self, parent, width=1100, height=400, **options):

		Frame.__init__(self,parent, **options)

		Grid.rowconfigure(self, 0, weight=1)
		Grid.columnconfigure(self, 0, weight=1)

		self.grid(sticky=E+W+N+S)

		top=self.winfo_toplevel()

		#Configure the width of rows and columns when tthe gui gets stretched. The second number provides the relative
		#weight of the column or row given by the first number

		norows = 14
		nocols = 13

		for i in range(norows):
			Grid.rowconfigure(self,i,weight=1)
			Grid.rowconfigure(parent,i,weight=1)
		for i in range(nocols):
			Grid.columnconfigure(self,i,weight=1)
			Grid.columnconfigure(parent,i,weight=1)

        #create subplot where the map will go
		self.f = Figure(figsize=(5.0,2.2),dpi=250,facecolor='white')
		self.a = self.f.add_subplot(111)

		#Call function to download some earhquakes and ... 

		#Call one of Quinhai's functions here to make the initial map: This is just a placeholder 

		self.map = Basemap(ax=self.a,lat_0=38,lon_0=-122.0,resolution ='l',llcrnrlon=-179,llcrnrlat=-79,urcrnrlon=179.9,urcrnrlat=79)
		self.map.shadedrelief()

		self.canvas = FigureCanvasTkAgg(self.f, self)
		self.canvas.mpl_connect('button_press_event',Browse.onpick)
		self.canvas.show()
		self.canvas.get_tk_widget().grid(row=1,sticky=W+S+N+E,columnspan=14,rowspan=10)

		self.SetElements()

		parent.title("QuakeWatch Mapper")


	def SetElements(self):

		'''Sets up the the GUI elements'''

		Label(self,text='QuakeWatch 1.0',bg='azure',height=2,pady=2,font='Helvetica 22 bold').grid(row=0,column=0,columnspan=14,sticky=W+E+S+N)

		#Zoom box bounds

		Label(self,text='Bounds of zoom box [lon/lat]',bg='azure',height=4,pady=2,padx=1,font='Helvetica 14 bold').grid(row=11,column=1,columnspan=4,sticky=W+E+S+N)
		Ncord = Entry(self)
		Ncord.grid(row=12,column=2,columnspan=1,sticky=E)
		Label(self,text='Northeastern corner').grid(row=12,column=1,columnspan=1,sticky=W)

		Scord = Entry(self)
		Scord.grid(row=13,column=2,columnspan=1,sticky=E)
		Label(self,text='Southwestern corner').grid(row=13,column=1,columnspan=1,sticky=W)

		Button(self, text='Zoom',pady=1,padx=1,command=self.zoomin).grid(row=14,column=1,sticky=W+S+E+N,columnspan=1)
		Button(self, text='Reset',pady=1,padx=1,command=self.resetzoom).grid(row=14,column=2,sticky=W+S+E+N,columnspan=1)
		Button(self, text='Draw',pady=1,padx=1,command=self.drawbox).grid(row=14,column=3,sticky=W+S+E+N,columnspan=1)

		#Drawing profiles

		Label(self,text='Bounds of profile [lon/lat]',bg='azure',height=4,pady=2,padx=1,font='Helvetica 14 bold').grid(row=11,column=6,columnspan=4,sticky=W+E+S+N)

		Stcord = Entry(self)
		Stcord.grid(row=12,column=7,columnspan=1,sticky=E)
		Label(self,text='Start point ').grid(row=12,column=6,columnspan=3,sticky=W)

		Edcord = Entry(self)
		Edcord.grid(row=13,column=7,columnspan=1,sticky=E)
		Label(self,text='End point').grid(row=13,column=6,columnspan=3,sticky=W)

		Button(self, text='Plot profile',pady=1,padx=1,command=self.plotprofile).grid(row=14,column=6,sticky=W+S+E+N,columnspan=4)

		#Event labels

		Label(self,text='Event options',bd=5,bg='azure',height=4,pady=2,padx=1,font='Helvetica 14 bold').grid(row=11,column=11,columnspan=4,sticky=W+E+S+N)

		Evtmags = Entry(self)
		Evtmags.grid(row=12,column=12,columnspan=2,sticky=E)
		Label(self,text='Event magnitude range [min-max]').grid(row=12,column=11,columnspan=1,sticky=W)

		Evttime = Entry(self)
		Evttime.grid(row=13,column=12,columnspan=2,sticky=E)
		Label(self,text='Event start date [yyyy/mm/dd]').grid(row=13,column=11,columnspan=1,sticky=W)

		Button(self, text='Set',pady=1,padx=1,command=self.getcatalogglobe).grid(row=14,column=11,sticky=W+S+E+N,columnspan=1)
		Button(self, text='Reset',pady=1,padx=1,command=self.resetquakes).grid(row=14,column=12,sticky=W+S+E+N,columnspan=1)

        #Set up the label showing when the datasets are refreshed: the current time goes into that label
		self.timer = StringVar()
		Label(self,textvariable=self.timer,bg='azure',height=1,pady=1,padx=1,font='Helvetica 10 bold').grid(row=0,column=0,columnspan=4,sticky=W+E+S+N)
		self.timer.set(str(time.asctime()))

		Quitter(self).grid(row=0,column=13,sticky=E)

	def zoomin(self):

		print 'Zoom'

	def drawbox(self):

		print 'Draw box'

	def resetzoom(self):

		print 'Reset'

	def plotprofile(self):

		print 'plot a 2D profile'

	def setquakes(self):

		print 'set quakes'

	def resetquakes(self):

		print 'reset quakes'

	def refreshloop(self):
		'''Refresh the map data accordingly'''

		print 'Refreshing quake dataset'
		self.timer.set(str(time.asctime()))

		#GetLatestseismicity(14) #Get seismicity from the last 14 days, down to magnitude 0.1
		#self.Autoupdateplot()
		tk.after(60000,self.refreshloop) #Refresh the dataset every 10 mins

	def getcatalogglobe(self):

		'''Get earthquake catalog according to the user's input'''

		t2 = str(datetime.datetime.today()).split(' ') #Current time
		t2 = t2[0]+'T'+t2[1][:-3]

		t1 = UTCDateTime("1970-01-01T00:00:00.000")
		t2 = UTCDateTime(t2)

		self.catalog = quaketools.get_cat(data_center='USGS',includeallorigins=True,starttime=t1,endtime=t2,minmagnitude=8)
		self.quakes, self.mts, self.events, self.qblasts = quaketools.cat2list(self.catalog)
		quaketools.plot_mt(self.quakes,self.mts,self.events)

		#print self.quakes, self.mts


if __name__ == '__main__':

	'''The GUI loop'''
	tk = Tk()
	viewer = QWGUI(tk)
	viewer.refreshloop()
	tk.mainloop()




