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
from datetime import datetime as dt
import os
import cat_analysis as quaketools
from obspy import UTCDateTime
import tkFileDialog

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
#GUI base class for QuakeWatch 
###########################################

class QWGUI(Frame):
	'''Base class controlling QuakeWatch GUI aspects'''

	def __init__(self, parent, width=1100, height=400, **options):

		Frame.__init__(self,parent, **options)

		Grid.rowconfigure(self, 0, weight=1)
		Grid.columnconfigure(self, 0, weight=1)

		self.grid(sticky=E+W+N+S)
		self.userentries = {}

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
		#self.map.shadedrelief()
		self.map.arcgisimage(service='NatGeo_World_Map',verbose=False,xpixels=10000)
		self.map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,0])
		self.map.drawmeridians(np.arange(-180,180,30),labels=[0,0,0,1])

		date = dt.utcnow()
		self.map.nightshade(date)

		self.canvas = FigureCanvasTkAgg(self.f, self)
		self.canvas.mpl_connect('button_press_event',Browse.onpick)
		self.canvas.show()
		self.canvas.get_tk_widget().grid(row=1,sticky=W+S+N+E,columnspan=14,rowspan=10)

		self.SetElements()

		parent.title("QuakeWatch Mapper")

		#Various default settings

		self.mts = False #display moment tensors where possible
		self.quakesplotted = None
		self.mtsplotted = None
		self.datacenter = 'USGS' #default datacenter to retrieve quake data from
		self.Createmenubar(parent)



	def SetElements(self):

		'''Sets up the the GUI elements'''

		Label(self,text='QuakeWatch 1.0',bg='azure',height=2,pady=2,font='Helvetica 22 bold').grid(row=0,column=0,columnspan=14,sticky=W+E+S+N)

		#Zoom box bounds

		Label(self,text='Bounds of zoom box [lon/lat]',bg='azure',height=4,pady=2,padx=1,font='Helvetica 14 bold').grid(row=11,column=1,columnspan=4,sticky=W+E+S+N)
		Ncord = Entry(self)
		Ncord.grid(row=12,column=2,columnspan=1,sticky=E)
		Label(self,text='Northeastern corner').grid(row=12,column=1,columnspan=1,sticky=W)
		self.userentries['Northeast_box'] = Ncord

		Scord = Entry(self)
		Scord.grid(row=13,column=2,columnspan=1,sticky=E)
		Label(self,text='Southwestern corner').grid(row=13,column=1,columnspan=1,sticky=W)
		self.userentries['Southwest_box'] = Scord

		Button(self, text='Zoom',pady=1,padx=1,command=self.zoomin).grid(row=14,column=1,sticky=W+S+E+N,columnspan=1)
		Button(self, text='Reset',pady=1,padx=1,command=self.resetzoom).grid(row=14,column=2,sticky=W+S+E+N,columnspan=1)
		Button(self, text='Draw',pady=1,padx=1,command=self.drawbox).grid(row=14,column=3,sticky=W+S+E+N,columnspan=1)

		#Drawing profiles

		Label(self,text='Bounds of profile [lon/lat]',bg='azure',height=4,pady=2,padx=1,font='Helvetica 14 bold').grid(row=11,column=6,columnspan=4,sticky=W+E+S+N)

		Stcord = Entry(self)
		Stcord.grid(row=12,column=7,columnspan=1,sticky=E)
		Label(self,text='Start point ').grid(row=12,column=6,columnspan=3,sticky=W)
		self.userentries['profile_start'] = Stcord

		Edcord = Entry(self)
		Edcord.grid(row=13,column=7,columnspan=1,sticky=E)
		Label(self,text='End point').grid(row=13,column=6,columnspan=3,sticky=W)
		self.userentries['profile_end'] = Edcord

		Button(self, text='Plot profile',pady=1,padx=1,command=self.plotprofile).grid(row=14,column=6,sticky=W+S+E+N,columnspan=4)

		#Event labels

		Label(self,text='Event options',bd=5,bg='azure',height=4,pady=2,padx=1,font='Helvetica 14 bold').grid(row=11,column=11,columnspan=4,sticky=W+E+S+N)

		Evtmags = Entry(self)
		Evtmags.grid(row=12,column=12,columnspan=2,sticky=E)
		Label(self,text='Event magnitude range [min-max]').grid(row=12,column=11,columnspan=1,sticky=W)
		self.userentries['magrange'] = Evtmags

		Evttime = Entry(self)
		Evttime.grid(row=13,column=12,columnspan=2,sticky=E)
		Label(self,text='Event start date [yyyy/mm/dd]').grid(row=13,column=11,columnspan=1,sticky=W)
		self.userentries['evttime'] = Evttime

		Button(self, text='Set',pady=1,padx=1,command=self.setquakesmanual).grid(row=14,column=11,sticky=W+S+E+N,columnspan=1)
		Button(self, text='Reset',pady=1,padx=1,command=self.resetmap).grid(row=14,column=12,sticky=W+S+E+N,columnspan=1)

        #Set up the label showing when the datasets are refreshed: the current time goes into that label
		self.timer = StringVar()
		Label(self,textvariable=self.timer,bg='azure',height=1,pady=1,padx=1,font='Helvetica 10 bold').grid(row=0,column=0,columnspan=4,sticky=W+E+S+N)
		self.timer.set(str(time.asctime()))

		Quitter(self).grid(row=0,column=13,sticky=E)


	def zoomin(self):

		print 'Zoom'

	def drawbox(self):

		print 'Draw box'

		boxcoordsNE = self.userentries['Northeast_box'].get()
		boxcoordsSW = self.userentries['Southwest_box'].get()

		try:
			NElon = boxcoordsNE.split('/')[0]
			NElat = boxcoordsNE.split('/')[1]
			SWlon = boxcoordsSW.split('/')[0]
			SWlat = boxcoordsSW.split('/')[1]
		except:
			print 'User coordinates not entered correctly'

		boxlats = [SWlat,SWlat,NElat,NElat,SWlat]
		boxlons = [SWlon,NElon,NElon,SWlon,SWlon]

		xevent,yevent = self.map(boxlons,boxlats)
		self.map.plot(xevent,yevent,'r-',linewidth=1,alpha=0.9)
		self.map.plot(xevent,yevent,'k.')
		self.canvas.draw()


	def resetzoom(self):

		print 'Reset'

	def plotprofile(self):

		linecoordsstart = self.userentries['profile_start'].get()
		linecoordsend = self.userentries['profile_end'].get()

		try:
			Slon = linecoordsstart.split('/')[0]
			Slat = linecoordsstart.split('/')[1]
			Elon = linecoordsend.split('/')[0]
			Elat = linecoordsend.split('/')[1]
		except:
			print 'User coordinates not entered correctly'

		lats = [Slat,Elat]
		lons = [Slon,Elon]

		xevent,yevent = self.map(lons,lats)
		self.map.plot(xevent,yevent,'r-',linewidth=1,alpha=0.9)
		self.map.plot(xevent,yevent,'k.')
		self.canvas.draw()

	def setquakesmanual(self):

		'''Fetch an earthquake catalog corresponding to the user's choice'''

		#Reset the map
		self.resetmap()

		starttime = self.userentries['evttime'].get()

		t1 = str(starttime)+'T00:00:00.000'

		t2 = str(datetime.datetime.today()).split(' ') #Current time
		t2 = t2[0]+'T'+t2[1][:-3]

		try:
			t1 = UTCDateTime(t1)
			t2 = UTCDateTime(t2)
		except:
			print 'Alert: Times not entered correctly!'
			print 'Default time range : 1970-01-01 to today'
			t1 = UTCDateTime("1970-01-01T00:00:00.000")
			t2 = UTCDateTime(t2)


		mags = self.userentries['magrange'].get()

		try:
			mag1 = mags.split('-')[0].strip()
			mag2 = mags.split('-')[1].strip()
		except:
			print 'Alert: Magnitudes not entered correctly!'
			print 'Default magnitude range: 6-10'
			mag1 = 6
			mag2 = 10

		self.catalog = quaketools.get_cat(data_center=self.datacenter,includeallorigins=True,starttime=t1,endtime=t2,minmagnitude=mag1,maxmagnitude=mag2)
		self.quakes, self.mts, self.events, self.qblasts = quaketools.cat2list(self.catalog)

		if self.mts == True:

			#plot the moment tensors and redraw
			quaketools.plot_mt(self.map,self.a,self.f,self.quakes,self.mts,self.events)
			self.canvas.draw()

		else:
			#only plotting events, so continue
			self.quakesplotted = quaketools.plot_events(self.map,self.a,self.quakes)
			self.canvas.draw()

	def resetmap(self):

		if self.quakesplotted != None:

			self.quakesplotted.remove()
			self.canvas.draw()
			self.quakesplotted = None

		if self.mtsplotted != None:

			self.mtsplotted.remove()
			self.canvas.draw()
			self.mtsplotted = None

		else:

			print 'Default reset function'

			# self.a.clear()

			# self.map = Basemap(ax=self.a,lat_0=38,lon_0=-122.0,resolution ='l',llcrnrlon=-179.9,llcrnrlat=-89,urcrnrlon=179.9,urcrnrlat=89)
			# self.map.fillcontinents()

			# #self.map.drawparallels(np.arange(-90,90,30),labels=[1,0,0,0])
			# #self.map.drawmeridians(np.arange(self.map.lonmin,self.map.lonmax+30,60),labels=[0,0,0,1])

			# self.canvas = FigureCanvasTkAgg(self.f, self)
			# self.canvas.mpl_connect('button_press_event',Browse.onpick)
			# self.canvas.show()
			# self.canvas.get_tk_widget().grid(row=1,sticky=W+S+N+E,columnspan=14,rowspan=10)

	def refreshloop(self):
		'''Refresh the map data accordingly'''

		print 'Refreshing quake dataset'
		self.timer.set(str(time.asctime()))

		#GetLatestseismicity(14) #Get seismicity from the last 14 days, down to magnitude 0.1
		#self.Autoupdateplot()
		tk.after(210000,self.refreshloop) #Refresh the dataset every 10 mins


	def Createmenubar(self,parent): 
		'''Create the drop down menu: allows user to add data layers to the Alaska'''

		menubar = Menu(self)
		parent.config(menu=menubar)
		filemenu = Menu(menubar,tearoff=0,font="Helvetica 16 bold") #insert a drop-down menu

		submenu1 = Menu(filemenu)
		submenu1.add_command(label='M2.5+ 1 Week',command=self.M25_1wk)
		submenu1.add_command(label='M4.5+ 1 Week',command=self.M45_1wk)
		submenu1.add_command(label='M2.5+ 30 days',command=self.M25_30d)
		submenu1.add_command(label='M4.5+ 30 days',command=self.M45_30d)
		submenu1.add_command(label='M6.0+ 365 days',command=self.M60_365d)
		filemenu.add_cascade(label='Event options',menu=submenu1,underline=0)

		filemenu.add_separator()

		submenu2 = Menu(filemenu)
		submenu2.add_command(label='World',command=self.worldquakes)
		submenu2.add_command(label='USA',command=self.USAquakes)
		submenu2.add_command(label='California',command=self.CAquakes)
		submenu2.add_command(label='Oklahoma',command=self.OKquakes)
		submenu2.add_command(label='Alaska',command=self.AKquakes)
		filemenu.add_cascade(label='Region options',menu=submenu2,underline=0) #add the drop down menu to the menu bar

		filemenu.add_separator() 

		submenu3 = Menu(filemenu)
		submenu3.add_command(label='Save current frame',command=self.SaveasPDF)
		filemenu.add_cascade(label='Other options',menu=submenu3) #add the drop down menu to the menu bar 

		menubar.add_cascade(label="Options",menu=filemenu)

	def M25_1wk(self):

		print 'display'

	def M45_1wk(self):

		print 'display'

	def M25_30d(self):

		print 'display'

	def M45_30d(self):

		print 'display'

	def M60_365d(self):

		print 'display'

	def worldquakes(self):

		print 'display'

	def USAquakes(self):

		print 'display'

	def CAquakes(self):

		print 'display'

	def AKquakes(self):

		print 'display'

	def OKquakes(self):

		print 'display'

	def getcatalogglobe(self):

		'''Get earthquake catalog according to the user's input'''

		t2 = str(datetime.datetime.today()).split(' ') #Current time
		t2 = t2[0]+'T'+t2[1][:-3]

		t1 = UTCDateTime("1970-01-01T00:00:00.000")
		t2 = UTCDateTime(t2)

		self.catalog = quaketools.get_cat(data_center='USGS',includeallorigins=True,starttime=t1,endtime=t2,minmagnitude=8)
		self.quakes, self.mts, self.events, self.qblasts = quaketools.cat2list(self.catalog)
		#quaketools.plot_mt(self.quakes,self.mts,self.events)

		#print self.quakes, self.mts

	def SaveasPDF(self):
		'''Saves the current frame as a .pdf file'''

		#self.f.savefig('test.pdf',format='pdf')

		filelocation = tkFileDialog.asksaveasfilename(defaultextension='.pdf')
		self.f.savefig(filelocation,format='pdf')
		print 'Saved current figure'







if __name__ == '__main__':

	'''The GUI loop'''
	tk = Tk()
	viewer = QWGUI(tk)
	viewer.refreshloop()
	tk.mainloop()




