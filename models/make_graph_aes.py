#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
from sys import argv,exit
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
import re
from math import ceil

YLABEL=r"$E$ - energy ($\mu J$)"
XLABEL=r"$s_{msg}$ - size of the encrypted message (byte)"
TITLE="CPU utilisation of AES-CCM"
COLORS=['cyan','green','black','blue']
LINESTYLE=['solid', 'dashed','dotted','dashdot']

LINREG_LEGEND=['AES-CCM software','AES-CCM hardware']

CONVERT = [True, False]

y_value = 'E'
x_values= ['s_{msg}']

POWER_UJ = 37000.
CPU_FREQ_HZ = 32000000
def cyc_to_uj (x):
    return float(x)*POWER_UJ/CPU_FREQ_HZ

XTICK_FREQUENCY=16

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
    pos_linreg=[]
    data_linreg=[]

    for line in file:
        split_line=line.split()
        curr_pos=int(split_line[0])
        if CONVERT[arr_pos]:
            split_data = map(cyc_to_uj, map(int, split_line[1].split(',')))
        else:
            split_data = map(int, split_line[1].split(','))
        data.append(split_data)
        pos.append(curr_pos)
        if curr_pos % 16 is 0:
            data_linreg.append(split_data)
            pos_linreg.append(curr_pos)

    #Compute linear regression
    medians = np.median(data_linreg, axis=1)
    slope, intercept = np.polyfit(pos_linreg,medians,1)
    avg_median = np.mean(medians)
    r_squared = 1. - float(sum(map(lambda x,y : (x*slope+intercept-y)**2,pos_linreg, medians))) / sum(map(lambda x : (x-avg_median)**2, medians))
    equations.append([slope,intercept,r_squared])

    #Plot graph
    plt.plot(pos,map(lambda x : slope*ceil(x/16.)*16+intercept, pos), linestyle=LINESTYLE[arr_pos], color=COLORS[arr_pos],
            #label="{0}: {4}={1:.2f}{5}+{2:.2f}, R2={3:.4f}".format(filename,slope, intercept, r_squared, y_value, x_values[arr_pos]))
            label=r"{0}: ${4}={1:.2f}\lceil {5}/16\rceil+{2:.2f}$".format(LINREG_LEGEND[arr_pos],slope*16, intercept, r_squared, y_value, x_values[arr_pos]), marker='+')
    bp.append(plt.boxplot(data, positions=pos))
    plt.setp(bp[arr_pos]['boxes'], color=COLORS[arr_pos])
    arr_pos = arr_pos +1 

AES_CCM_HW_pos = [0,1,16,64,128]
AES_CCM_HW_val = [0,8.7,8.7,9.4,10]
plt.plot(AES_CCM_HW_pos,AES_CCM_HW_val,linestyle=LINESTYLE[arr_pos], color=COLORS[arr_pos],
        label=r"{0}".format(LINREG_LEGEND[arr_pos]), marker='o')

#Remove xticks for readability
for value in plt.xticks()[0]:
    if value==1 or value % XTICK_FREQUENCY==0:
        xticks.append(str(value))
    else:
        xticks.append('')
plt.xticks(plt.xticks()[0],xticks)

plt.legend(loc='upper center', bbox_to_anchor=(0.45,1.1), fontsize=12)

#Export to PDF
pp = PdfPages("aes_ccm.pdf")
pp.savefig(bbox_inches='tight')
pp.close()
