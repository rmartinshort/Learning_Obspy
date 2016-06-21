#!/usr/bin/env python 

#RMS 2016
#Main GUI class for QuakeWatch program

from Tkinter import *
import tkFileDialog
import matplotlib 
import numpy as np
import time
import datetime
import os

#Import obspy modules for fetching event data 
from obspy.fdsn import Client as fdsnClient
from obspy import UTCDateTime

clientNCEDC = fdsnClient("NCEDC")
clientIRIS = fdsnClient("IRIS")
clientUSGS = fdsnClient("USGS")

#Allow matplotlib to be used within a tkinter canvas
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm 
from netCDF4 import Dataset

#Control matplotlib font size
matplotlib.rcParams.update({'font.size': 6})

###########################################
#GUI base class for BayQuake 
###########################################

class QWGUI(Frame):
	'''Base class controlling QuakeWatch GUI aspects'''

	def __init__(self, parent, width=1000, height=300, **options):

		Frame.__init__(self,parent, **options)

		Grid.rowconfigure(self, 0, weight=1)
		Grid.columnconfigure(self, 0, weight=1)

		self.grid(sticky=E+W+N+S)

		top=self.winfo_toplevel()

		#Configure the width of rows and columns when tthe gui gets stretched. The second number provides the relative
		#weight of the column or row given by the first number

		norows = 9
		nocols = 13

		for i in range(norows):
			Grid.rowconfigure(self,i,weight=1)
			Grid.rowconfigure(parent,i,weight=1)
		for i in range(nocols):
			Grid.columnconfigure(self,i,weight=1)
			Grid.columnconfigure(parent,i,weight=1)

        #create subplot where the map will go
		self.f = Figure(figsize=(4.5,2.5),dpi=200,facecolor='white')
		self.a = self.f.add_subplot(111)

		#Call function to download some earhquakes and ... 

		#Call one of Quinhai's functions here to make the initial map: This is just a placeholder 

		self.map = Basemap(ax=self.a,lat_0=38,lon_0=-122.0,resolution ='l',llcrnrlon=-125,llcrnrlat=20,urcrnrlon=-60,urcrnrlat=60)
		self.map.shadedrelief()

		self.canvas = FigureCanvasTkAgg(self.f, self)
		self.canvas.show()
		self.canvas.get_tk_widget().grid(row=1,sticky=W+S+N+E,columnspan=9,rowspan=9)

		self.SetElements()

		parent.title("QuakeWatch Mapper")


	def SetElements(self):

		'''Sets up the the GUI elements'''

		Label(self,text='QuakeWatch 1.0',bg='azure',height=4,pady=2,font='Helvetica 18 bold').grid(row=0,column=0,columnspan=14,sticky=W+E+S+N)

		Label(self,text='Bounds of zoom box [lon/lat]',bg='azure',height=4,pady=2,padx=2,font='Helvetica 16 bold').grid(row=1,column=9,columnspan=4,sticky=W+E+S+N)

		Ncord = Entry(self)
		Ncord.grid(row=2,column=11,columnspan=2,sticky=E)
		Label(self,text='Northeastern corner').grid(row=2,column=9,columnspan=2,sticky=W)

		Scord = Entry(self)
		Scord.grid(row=3,column=11,columnspan=2,sticky=E)
		Label(self,text='Southwestern corner').grid(row=3,column=9,columnspan=2,sticky=W)

		Button(self, text='Zoom',pady=1,padx=1,command=self.zoomin).grid(row=4,column=9,sticky=W+S+E+N,columnspan=2)
		Button(self, text='Reset',pady=1,padx=1,command=self.resetzoom).grid(row=4,column=11,sticky=W+S+E+N,columnspan=2)

		Label(self,text='Bounds of profile [lon/lat]',bg='azure',height=4,pady=2,padx=2,font='Helvetica 16 bold').grid(row=5,column=9,columnspan=4,sticky=W+E+S+N)

		Stcord = Entry(self)
		Stcord.grid(row=6,column=11,columnspan=2,sticky=E)
		Label(self,text='Start point ').grid(row=6,column=9,columnspan=2,sticky=W)

		Edcord = Entry(self)
		Edcord.grid(row=7,column=11,columnspan=2,sticky=E)
		Label(self,text='End point').grid(row=7,column=9,columnspan=2,sticky=W)

		Button(self, text='Plot profile',pady=1,padx=1,command=self.plotprofile).grid(row=8,column=9,sticky=W+S+E+N,columnspan=4)

        #Set up the label showing when the datasets are refreshed: the current time goes into that label
		self.timer = StringVar()
		Label(self,textvariable=self.timer,bg='azure',height=4,pady=2,padx=4,font='Helvetica 10 bold').grid(row=9,column=9,columnspan=4,sticky=W+E+S+N)
		self.timer.set(str(time.asctime()))

	def zoomin(self):

		print 'Zoom'

	def resetzoom(self):

		print 'Reset'

	def plotprofile(self):

		print 'plot a 2D profile'


	def refreshloop(self):
		'''Refresh the map data accordingly'''

		print 'Refreshing quake dataset'
		self.timer.set(str(time.asctime()))

		#GetLatestseismicity(14) #Get seismicity from the last 14 days, down to magnitude 0.1
		#self.Autoupdateplot()
		tk.after(60000,self.refreshloop) #Refresh the dataset every 10 mins


if __name__ == '__main__':

	'''The GUI loop'''
	tk = Tk()
	viewer = QWGUI(tk)
	viewer.refreshloop()
	tk.mainloop()




