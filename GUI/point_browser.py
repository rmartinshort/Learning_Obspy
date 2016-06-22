#!/usr/bin/env python
import webbrowser
import numpy as np


class PointBrowser:
    """
    Click on a point to select and highlight it -- the data that
    generated the point will be shown in the lower axes.  Use the 'n'
    and 'p' keys to browse through the next and previous points
    """
    def __init__(self):
        self.lastind = 0

    def onpick(self, event):

       print 'mouse click!'

       # the click locations
       x = event.x
       y = event.y

       print x,y


       #distances = np.hypot(x-xs[event.ind], y-ys[event.ind])
       #indmin = distances.argmin()
       #dataind = event.ind[indmin]

       #self.lastind = dataind
       #self.update()

    def update(self):
        if self.lastind is None: return

        dataind = self.lastind

        open_url = url[dataind]
        webbrowser.open(open_url, new=0, autoraise=True)