import numpy as np
import scipy as sp
import functools
from itertools import cycle
from matplotlib.lines import Line2D

def dict_to_list(d):
    indexes = list(d.keys())
    indexes.sort()
    ret = []
    for i in indexes:
        ret.append(d[i])
    return ret

def none_if_undef(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IndexError:
            return None
    return func

class ExpStats:
    def __init__(self, result_file=None):
        self.results = {}
        self.params = None
        self.resl = []
        if result_file:
            self.parse_file_name(result_file)
            self.import_file(result_file)
            self.resl = dict_to_list(self.results)

    def parse_file_name(self, filename):
        s = filename[:filename.rfind('.')] #Removes extension
        s = s[s.rfind('/')+1:] #Removes path
        s = s.split('_')
        self.params = dict(zip(["nodes", "degree", "steps", "date"], map(int, s[:-1])))
        self.params["mode"] = s[len(s)-1]

    def import_file(self, filename):
        f=open(filename,'r')
        for line in f:
            s = map(int,line.split()) 
            self.results[s[0]] = s[1:]
        f.close()

    @none_if_undef
    def get_medians(self):
        return np.median(self.resl, 1)
    
    @none_if_undef
    def get_means(self):
        return np.mean(self.resl, 1)

    @none_if_undef
    def get_stddev(self):
        return np.std(self.resl, 1)

    @none_if_undef
    def get_fitting(self, start=0, stop=None):
        if not stop:
            stop=len(self.results)
        try:
            means = self.get_means()[start:stop]
            mmean = np.mean(means)
            slope, intercept = np.polyfit(self.results.keys()[start:stop], means, 1)
            r_squared = (1. - float(sum(map(lambda x,y : (x*slope+intercept-y)**2, self.results.keys()[start:stop], means))) /
                                             sum(map(lambda x : (x-mmean)**2, means)))
        except Exception:
            print "Error on file ",
            print self.params
        return slope, intercept, r_squared

    def __str__(self):
        return r"Mode: {0}, d={1}, $|V_i| = {2:.2f}\times i + {3:.2f}, R^2={4:.2f}$".format(self.params["mode"], self.params["degree"],
                *self.get_fitting())

class StatsExplorer:

    def __init__(self, directory, start):
        import os
        self.exps = {}
        self.fittings = {}
        self.start = start
        self.markers = cycle(('s','+', '.', 'o', '*'))
        self.colors  = cycle(('blue', 'red', 'green', 'black'))
        self.linestyles = cycle(('solid', 'dashed', 'dotted'))
        self.lines = {}
        for f in os.listdir(directory):
            if f.endswith(".csv"):
                e = ExpStats("{}/{}".format(directory, f))
                d = e.params["degree"]
                s = e.params["steps"]
                if d not in self.exps or self.exps[d].params["steps"] < s:
                    self.exps[e.params["degree"]] = e
                    self.fittings[e.params["degree"]] = e.get_fitting(start)

    def fit_slopes(self):
        degrees = self.fittings.keys()
        degrees.sort()
        slopes = map(lambda x : self.fittings[x][0], degrees)
        mslope = np.mean(slopes)
        slope, inter = np.polyfit(degrees, slopes, 1)
        r_squared = (1. - float(sum(map(lambda x,y : (x*slope+inter-y)**2, degrees, slopes))) /
                 sum(map(lambda x : (x-mslope)**2, slopes)))
        return slope, inter, r_squared

    def plot_subgraphs(self, stop=None, reverse=False):
        for esk in self.exps:
            self.plot_subgraph(esk, reverse=reverse, stop=stop)
        return self.lines

    def plot_subgraph(self, density, stop=None, reverse=False):
        import matplotlib.pyplot as plt
        es = self.exps[density]
        keys = es.results.keys()
        means = es.get_means()
        if stop:
            keys = keys[:stop]
            means = means[:stop]
        if reverse:
            keys = map(lambda x : keys[len(keys)-1]+1-x, keys)
        color=self.colors.next()
        marker=self.markers.next()
        linestyle=self.linestyles.next()
        s, i, _ = es.get_fitting(self.start, stop)
        self.lines[density] = Line2D(keys, means, marker=marker, color=color, linestyle=linestyle)
        #plt.plot(self.lines[density], label=r"d={0}".format(density))
        #plt.plot(keys, map(lambda x : x*s+i, keys), color=color, linestyle=PLT_LINESTYLE.next())

