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
#matplotlib.use("macosx")
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


		#Various default settings
		self.momenttensors = True #display moment tensors where possible
		self.quakesplotted = None
		self.MTs = None

		t2 = str(datetime.datetime.today()).split(' ') #Current time
		t2 = t2[0]+'T'+t2[1][:-3]
		self.now = UTCDateTime(t2)

		self.starttime = 604800 #1 week quakes

		#--------------------------
		#Default map boundaries
		#--------------------------
		self.minlon = -179.9
		self.maxlon = 179.9
		self.minlat = -89
		self.maxlat = 89
		#--------------------------

		self.minmag = 4.5
		self.maxmag = 10.0
		self.datacenter = 'USGS' #default datacenter to retrieve quake data from

        #create subplot where the map will go
		self.f = plt.figure(dpi=250,facecolor='white')

		#set the size of the figure for use with global map. Will need to choose this on the fly when
		#resizing the figure
		
		self.f.set_size_inches(5.0,2.2)
		self.a = self.f.add_subplot(111)

		#Call function to download some earhquakes and ... 

		#Initial meap setup and quakes
		self.map = Basemap(ax=self.a,lat_0=38,lon_0=-122.0,resolution ='l',llcrnrlon=-179.9,llcrnrlat=-89,urcrnrlon=179.9,urcrnrlat=89)
		self.map.arcgisimage(service='NatGeo_World_Map',verbose=False,xpixels=10000)
		self.map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,0],linewidth=0.5,fontsize=4)
		self.map.drawmeridians(np.arange(-180,180,30),labels=[0,0,0,1],linewidth=0.5,fontsize=4)

		self.canvas = FigureCanvasTkAgg(self.f, self)

		#plot quakes for the last week on the globe map with default parameters
		self.worldquakes()

		self.f.canvas.mpl_connect('button_press_event',Browse.onpick)
		self.canvas.get_tk_widget().grid(row=1,sticky=W+S+N+E,columnspan=14,rowspan=10)
		self.canvas.show()

		self.SetElements()

		parent.title("QuakeWatch Mapper")

		self.Createmenubar(parent)



	def SetStartMap(self):

		'''Make global pretty map. Takes a long time so only make on startup'''

		self.map = Basemap(ax=self.a,lat_0=38,lon_0=-122.0,resolution ='l',llcrnrlon=-179.9,llcrnrlat=-89,urcrnrlon=179.9,urcrnrlat=89)
		#self.map.shadedrelief()
		self.map.arcgisimage(service='NatGeo_World_Map',verbose=False,xpixels=10000)
		self.map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,0],linewidth=0.5,fontsize=4)
		self.map.drawmeridians(np.arange(-180,180,30),labels=[0,0,0,1],linewidth=0.5,fontsize=4)
		self.canvas.draw()

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
		Label(self,text='Start:').grid(row=12,column=6,columnspan=3,sticky=W)
		self.userentries['profile_start'] = Stcord

		Edcord = Entry(self)
		Edcord.grid(row=13,column=7,columnspan=1,sticky=E)
		Label(self,text='End:').grid(row=13,column=6,columnspan=3,sticky=W)
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
		Label(self,text='Event start date [yyyy-mm-dd]').grid(row=13,column=11,columnspan=1,sticky=W)
		self.userentries['evttime'] = Evttime

		Button(self, text='Set',pady=1,padx=1,command=self.setquakesmanual).grid(row=14,column=11,sticky=W+S+E+N,columnspan=1)
		Button(self, text='Reset',pady=1,padx=1,command=self.resetmap).grid(row=14,column=12,sticky=W+S+E+N,columnspan=1)

        #Set up the label showing when the datasets are refreshed: the current time goes into that label
		self.timer = StringVar()
		Label(self,textvariable=self.timer,bg='azure',height=1,pady=1,padx=1,font='Helvetica 10 bold').grid(row=0,column=0,columnspan=4,sticky=W+E+S+N)
		self.timer.set(str(time.asctime()))

		Quitter(self).grid(row=0,column=13,sticky=E)

	def SetZoomMap(self,lon1,lon2,lat1,lat2):

		'''Zoom into map'''

		self.a.clear()

		#Ensure that no extra elememts are plotted
		self.MTs = None
		self.quakesplotted = None

		#true_scale_lat = (lat2-lat1)/2

		#scale the longitude and latiude grid increments
		latinc = int((max(lat1,lat2)-min(lat1,lat2))/6)
		loninc = int(abs((lon2-lon1)/6))
		lon0 = int(abs(lon2)-abs(lon1))/2
		lat0 = int((lat2-lat1)/2)

		if abs(lat2-lat1) < 6.0:
			res = 'i'
		elif abs(lat2-lat1) < 2.0:
			res = 'h'
		else:
			res = 'l'

		#choose a resolution based on the size of the provided box

		self.map = Basemap(ax=self.a,lat_0=lat0,lon_0=lon0,resolution=res,llcrnrlon=lon1,llcrnrlat=lat1,urcrnrlon=lon2,urcrnrlat=lat2)
		self.map.drawparallels(np.arange(lat1,lat2,latinc),labels=[1,1,0,0],linewidth=0.5,fontsize=4)
		self.map.drawmeridians(np.arange(lon1,lon2,loninc),labels=[0,0,0,1],linewidth=0.5,fontsize=4)

		#self.map = Basemap(ax=self.a,projection='merc',llcrnrlat=lat1,urcrnrlat=lat2,llcrnrlon=lon1,urcrnrlon=lon2,lat_ts=true_scale_lat,resolution='l')
		#self.map.arcgisimage(service='NatGeo_World_Map',verbose=False,xpixels=10000)

		#self.map.drawlsmask(land_color="#ddaa66", ocean_color="#7777ff",resolution='i')
		self.map.fillcontinents()
		self.map.drawcountries()
		self.canvas.draw()

	def zoomin(self):

		boxcoordsNE = self.userentries['Northeast_box'].get()
		boxcoordsSW = self.userentries['Southwest_box'].get()

		try:
			NElon = float(boxcoordsNE.split('/')[0])
			NElat = float(boxcoordsNE.split('/')[1])
			SWlon = float(boxcoordsSW.split('/')[0])
			SWlat = float(boxcoordsSW.split('/')[1])
		except:
			print 'User coordinates not entered correctly'

		self.SetZoomMap(SWlon,NElon,SWlat,NElat)

	def drawbox(self):

		print 'Draw box'

		boxcoordsNE = self.userentries['Northeast_box'].get()
		boxcoordsSW = self.userentries['Southwest_box'].get()

		try:
			NElon = float(boxcoordsNE.split('/')[0])
			NElat = float(boxcoordsNE.split('/')[1])
			SWlon = float(boxcoordsSW.split('/')[0])
			SWlat = float(boxcoordsSW.split('/')[1])
		except:
			print 'User coordinates not entered correctly'

		boxlats = [SWlat,SWlat,NElat,NElat,SWlat]
		boxlons = [SWlon,NElon,NElon,SWlon,SWlon]

		xevent,yevent = self.map(boxlons,boxlats)
		self.map.plot(xevent,yevent,'r-',linewidth=1,alpha=0.9)
		self.map.plot(xevent,yevent,'k.')
		self.canvas.draw()


	def resetzoom(self):

		'''Reset the zoom to the global map'''

		self.a.clear()
		self.MTs = None
		self.quakesplotted = None
		self.SetStartMap()

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

		t2 = self.now

		try:
			t1 = UTCDateTime(t1)
		except:
			print 'Alert: Times not entered correctly!'
			print 'Default time range : 1970-01-01 to today'
			t1 = UTCDateTime("1970-01-01T00:00:00.000")


		mags = self.userentries['magrange'].get()

		try:
			mag1 = mags.split('-')[0].strip()
			mag2 = mags.split('-')[1].strip()
		except:
			print 'Alert: Magnitudes not entered correctly!'
			print 'Default magnitude range: 6-10'
			mag1 = 6
			mag2 = 10

		#get the box coordinates, if they exist
		try:

			NElat,NElon,SWlat,SWlon = self.GetBoxCoors()

			#set the dafault map coordinates to be those corresponding to the inputs
			self.minlon = SWlon
			self.maxlon = NElon
			self.minlat = SWlat
			self.maxlat = NElat

			self.catalog = quaketools.get_cat(data_center=self.datacenter,includeallorigins=True,starttime=t1,endtime=t2,minmagnitude=mag1,maxmagnitude=mag2,maxlongitude=NElon,minlongitude=SWlon,maxlatitude=NElat,minlatitude=SWlat)
			self.quakes, self.mts, self.events, self.qblasts = quaketools.cat2list(self.catalog)

			if self.momenttensors == True:

				#plot the moment tensors and redraw
				self.mtlines, self.MTs, self.quakedots, xs, ys, urls = quaketools.plot_mt(self.map,self.a,self.f,self.quakes,self.mts,self.events,llat=SWlat,ulat=NElat,llon=SWlon,ulon=NElon,dist_bt=200,radius=5,mt_width=1)

			else:
				#only plotting events, so continue
				self.quakesplotted = quaketools.plot_events(self.map,self.a,self.quakes,llat=SWlat,ulat=NElat,llon=SWlon,ulon=NElon,dist_bt=100)
		
		except:

			#Case where the user has not entered the correct zoom coordinates or none at all

			print 'Assuming global map'

			self.catalog = quaketools.get_cat(data_center=self.datacenter,includeallorigins=True,starttime=t1,endtime=t2,minmagnitude=mag1,maxmagnitude=mag2)

			self.quakes, self.mts, self.events, self.qblasts = quaketools.cat2list(self.catalog)

			if self.momenttensors == True:

				#plot the moment tensors and redraw
				self.mtlines, self.MTs, self.quakedots, xs, ys, urls = quaketools.plot_mt(self.map,self.a,self.f,self.quakes,self.mts,self.events)

			else:
				#only plotting events, so continue
				self.quakesplotted = quaketools.plot_events(self.map,self.a,self.quakes)
		
		self.canvas.draw()

	def resetmap(self):

		if self.quakesplotted != None:

			self.quakesplotted.remove()
			self.canvas.draw()
			self.quakesplotted = None

		if self.MTs != None:

			for e1 in self.MTs:
				print e1
				e1.remove()

			for e2 in self.mtlines:
				if e2 is not None:
					print e2
					e2[0].remove()

			self.quakedots.remove()

			#self.mtlines.remove()
			#self.mtdots.remove()
			#self.MTs.remove()
			self.canvas.draw()
			self.MTs = None

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
		submenu3.add_command(label='Pretty map (may take a long time to load!)',command=self.PrettyMap)
		filemenu.add_cascade(label='Other options',menu=submenu3) #add the drop down menu to the menu bar 

		menubar.add_cascade(label="Options",menu=filemenu)

		fm2 = Menu(menubar,tearoff=0)
		subm1 = Menu(fm2)
		subm1.add_command(label='Some command')
		menubar.add_cascade(label="Statistics",menu=fm2)


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

		'''Get world catalog of quakes and plot. If we already on a global map, then we just plot the elemments'''

		t2 = self.now
		t1 = t2-self.starttime

		self.catalog = quaketools.get_cat(data_center=self.datacenter,includeallorigins=True,starttime=t1,endtime=t2,minmagnitude=self.minmag,maxmagnitude=self.maxmag)
		self.quakes, self.mts, self.events, self.qblasts = quaketools.cat2list(self.catalog)



		if self.momenttensors == True:

			#plot the moment tensors and redraw

			#maximum radius of a moment tensor
			print '---------------------------'
			print self.events
			print '---------------------------'

			mtradius = 10
			self.mtlines, self.MTs, self.quakedots, xs, ys, urls = quaketools.plot_mt(self.map,self.a,self.f,self.quakes,self.mts,self.events,mt_width=3,radius=mtradius,angle_step=30)

			Browse.updatedata(xs,ys,urls,mtradius)
			print xs,ys,urls

		else:
			#only plotting events, so continue
			self.quakesplotted = quaketools.plot_events(self.map,self.a,self.quakes)
		
		self.canvas.draw()

	def Autoupdate(self):

		'''For use with the auto-updater - get only the quakes within the map region and update'''

		t2 = str(datetime.datetime.today()).split(' ') #Update the time
		t2 = t2[0]+'T'+t2[1][:-3]
		self.now = UTCDateTime(t2)

		t2 = self.now
		t1 = t2-self.starttime

		self.catalog = quaketools.get_cat(data_center=self.datacenter,includeallorigins=True,starttime=t1,endtime=t2,minmagnitude=self.minmag,maxmagnitude=self.maxmag,maxlongitude=self.maxlon,minlongitude=self.minlon,maxlatitude=self.maxlat,minlatitude=self.minlon)
		self.quakes, self.mts, self.events, self.qblasts = quaketools.cat2list(self.catalog)

		if self.momenttensors == True:

			#plot the moment tensors and redraw
			self.mtlines, self.MTs, self.quakedots, xs, ys, urls = quaketools.plot_mt(self.map,self.a,self.f,self.quakes,self.mts,self.events,mt_width=3,radius=10,angle_step=40,llat=SWlat,ulat=NElat,llon=SWlon,ulon=NElon)

		else:
			#only plotting events, so continue
			self.quakesplotted = quaketools.plot_events(self.map,self.a,self.quakes)
		
		self.canvas.draw()


	def USAquakes(self):

		print 'display'

	def CAquakes(self):

		print 'display'

	def AKquakes(self):

		print 'display'

	def OKquakes(self):

		print 'display'

	def PrettyMap(self):

		'''Display some useful information on the current map'''


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

	def GetBoxCoors(self):

		'''Returns the coordinates of user defined zoom box'''

		boxcoordsNE = self.userentries['Northeast_box'].get()
		boxcoordsSW = self.userentries['Southwest_box'].get()

		try:
			NElon = float(boxcoordsNE.split('/')[0])
			NElat = float(boxcoordsNE.split('/')[1])
			SWlon = float(boxcoordsSW.split('/')[0])
			SWlat = float(boxcoordsSW.split('/')[1])
			return NElat,NElon,SWlat,SWlon
		except:
			return None



if __name__ == '__main__':

	'''The GUI loop'''
	tk = Tk()
	viewer = QWGUI(tk)
	viewer.refreshloop()
	tk.mainloop()




