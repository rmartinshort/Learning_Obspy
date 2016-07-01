#!/usr/bin/env python
import webbrowser
import numpy as np


class PointBrowser:
    """
    Click on a point to select and highlight it -- the data that
    generated the point will be shown in the lower axes.  Use the 'n'
    and 'p' keys to browse through the next and previous points
    """
    def __init__(self,xs=None,ys=None):
        self.lastind = 0
        self.xs = None
        self.ys = None
        self.urls = None

    def updatedata(self,xs,ys,urls,rad):

        self.xs = xs
        self.ys = ys
        self.url = urls
        self.mtsize = rad/2.0

    def onpick(self, event):

       print 'mouse click!'

       # the click locations

       lon = event.xdata
       lat = event.ydata

       print lon,lat

       if self.xs.any():

         #determine distances from the click point to each of the moment tensors
         distances = np.hypot(lon-self.xs, lat-self.ys)

         #determine index of the nearest moment tensor
         indmin = distances.argmin()

         #detrmine smallest distance 
         if distances[indmin] < self.mtsize:

          self.lastind = indmin
          self.update()

    def update(self):
        if self.lastind is None: return

        dataind = self.lastind

        open_url = self.url[dataind]
        webbrowser.open(open_url, new=0, autoraise=True)