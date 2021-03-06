from osgeo import gdal
gdal.UseExceptions() #enable exception handling

import numpy as np
from landclass import *

from math import *
import matplotlib.pyplot as plt
import itertools as it


class basin(object):
    """Describes a CRHM basin"""
    def __init__(self):
        self._landclass = {}
        self._hrus= None #holds the generated HRU
        self._num_hrus = 0
        self._num_lc = 0

    def get_num_landclass(self):
        return len(self._landclass)
    
    def add_landclass(self,lc):
        self._landclass[lc._name] = lc
        self._num_lc += 1
        
    def get_num_hrus(self):
        return self._num_hrus
    
    def create_hrus(self):
        comb = []
        size = None
        for c in self._landclass:
            a=range(1,self._landclass[c].get_nclasses()+1)
            comb.append(a)
            
            #if size == None:
                #size = self._landclass[c].size()
            #elif size != self._landclass[c].size():
                #raise Exception('Rasters are of a different size')
            
        hrus = list(it.product(*comb))
        self._num_hrus = len(hrus)
        stack = np.ma.dstack(([r.get_classraster() for r in self._landclass.values()]))

        #do the classification
        hrus = (np.ma.masked_array([np.ma.masked_array(h)[...,:] == stack for h in hrus]).all(axis = -1) *
                 (2 + np.ma.arange(len(hrus)))[:, None, None]).max(axis=0) - 1       
    
        self._hrus = copy.copy(self._landclass.iteritems().next()[1]) #just copy the first raster, doesn't matter what it is
        self._hrus._raster = hrus
        self._hrus.__class__ = raster
        
    def show(self):
        
        nclasses = len(self._landclass)
        gs=plt.GridSpec(nclasses, 2)
        
        row = 0
        fig=plt.figure()
        for c in self._landclass:
            ax=fig.add_subplot(gs[row,0], title=c)
            im=ax.imshow(self._landclass[c].get_raster())
            
            from mpl_toolkits.axes_grid1 import make_axes_locatable
            divider = make_axes_locatable(plt.gca())
            cax = divider.append_axes("right", "5%", pad="3%")            
            cb=fig.colorbar(im,cax=cax)
            
            ax=fig.add_subplot(gs[row,1],title='Classified '+c)
            im=ax.imshow(self._landclass[c].get_classraster())
            
            
            divider = make_axes_locatable(plt.gca())
            cax = divider.append_axes("right", "5%", pad="3%")            
            cb=fig.colorbar(im,cax=cax)
            
            cb.set_ticks( list(range(1,self._landclass[c].get_nclasses()+1)))
            cb.set_ticklabels(self._landclass[c].get_classes_str())            

            row +=1
        
        fig.tight_layout()
        #plt.show()

    def __call__(self,name):
        return self._landclass[name]
   
    def remove_landclass(self,name):
        del self._landclass[name]
        self._num_lc-=1
