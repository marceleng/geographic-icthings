#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
from sys import argv,exit
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
import re

YLABEL="Number of CPU cycles"
XLABEL="Number of neighbours/FIB entries"
TITLE="CPU utilisation of vanilla ICN and geographic forwarding"
COLORS=['cyan','green','black','blue']
LINESTYLE=['solid', 'dashed','dotted','dashdot']

y_value = 'n_{cyc}'
x_values= ['n_{fib}','n_{neigh}']

XTICK_FREQUENCY=5

matplotlib.figure.Figure(figsize=(2,1))
matplotlib.rcParams.update({ 'font.size' : 14 })

arr_pos=0
bp = []
xticks = []

equations=[]

if len(argv) < 2:
    exit("Usage: ./make_graph filename")

def adjustFigAspect(fig,aspect=1):
    '''
    Adjust the subplot parameters so that the figure has the correct
    aspect ratio.
    '''
    xsize,ysize = fig.get_size_inches()
    minsize = min(xsize,ysize)
    xlim = .4*minsize/xsize
    ylim = .4*minsize/ysize
    if aspect < 1:
        xlim *= aspect
    else:
        ylim /= aspect
    fig.subplots_adjust(left=.5-xlim, right=.5+xlim, bottom=.5-ylim, top=.5+ylim)

fig = plt.figure()
plt.clf()

adjustFigAspect(fig, 2.3)

#plt.title(TITLE)
plt.ylabel(YLABEL)
plt.xlabel(XLABEL)

for filename in argv[1:] :
    file=open(filename,"r")

    pos=[]
    data=[]

    for line in file:
        split_line=line.split()
        data.append(map(int,split_line[1].split(',')))
        pos.append(int(split_line[0]))

    #Compute linear regression
    medians = np.median(data, axis=1)
    slope, intercept = np.polyfit(pos,medians,1)
    avg_median = np.mean(medians)
    r_squared = 1. - float(sum(map(lambda x,y : (x*slope+intercept-y)**2,pos, medians))) / sum(map(lambda x : (x-avg_median)**2, medians))
    equations.append([slope,intercept,r_squared])

    #Plot graph
    plt.plot(pos,map(lambda x : slope*x+intercept, pos), linestyle=LINESTYLE[arr_pos], color=COLORS[arr_pos],
            #label="{0}: {4}={1:.2f}{5}+{2:.2f}, R2={3:.4f}".format(filename,slope, intercept, r_squared, y_value, x_values[arr_pos]))
            label=r"{0}: ${4}={1:.2f}{5}+{2:.2f}$".format(re.sub('_', ' ', filename),slope, intercept, r_squared, y_value, x_values[arr_pos]))
    bp.append(plt.boxplot(data, positions=pos))
    plt.setp(bp[arr_pos]['boxes'], color=COLORS[arr_pos])
    arr_pos = arr_pos +1 

#Remove xticks for readability
for value in plt.xticks()[0]:
    if value==1 or value % XTICK_FREQUENCY==0:
        xticks.append(str(value))
    else:
        xticks.append('')
plt.xticks(plt.xticks()[0],xticks)

plt.legend(loc='upper left', fontsize=12)#, bbox_to_anchor=(0.5,1.35), fontsize=12) 
#Export to PDF
pp = PdfPages("test.pdf")
pp.savefig(bbox_inches='tight')
pp.close()
