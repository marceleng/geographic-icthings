import flood_simulator_stats as fss
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_pdf import PdfPages
from itertools import cycle
from math import fsum, fabs, log, ceil
import numpy as np
from compare_classic_mpr_flood import get_markers

from constants import *

plt.ion()

#Forces matplotlib to use type 1 fonts
matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

matplotlib.rcParams.update({ 'font.size' : 18 })

cf=fss.StatsExplorer("sim_results/naiveflood_10000", 0)
mf=fss.StatsExplorer("sim_results/mpr_10000", 0)


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

adjustFigAspect(fig, 1.5)

cf_s, mf_s = "solid", "dashed"

pc = {
        4 : 0.15,
        5:  .18,
        6: .21,
        7: .24,
        8: .27,
        9: .295,
        10: .32,
        11: .345,
        12: .37,
        13: .395,
        14: .42,
        15: .445,
        16: .47,
        17: .49,
        18: .51,
        19: .535,
        20: .56,
        22: .59,
        24: .63,
        26: .66,
        28: .68,
        30: .71,
        32: .73,
        34: .76,
        36: .78,
        38: .81,
        40: .83,
        42: .84,
        44: .86,
        46: .87,
        48: .88,
        50: .89
        }

PAYLOAD_SIZE = 32
NODE_ID_SIZE = 2
SLOC = 8
NUMBER_NAME_COMP = 3
TTL = 4

LIFETIME = 1 * 60 * 24 * (365*2) # 1 reading/minute over 2 years

def nb_tries_per_message(pc, mtr=5):
    return (1.-(pc**mtr)*(mtr+1.)+(pc**(mtr+1))*mtr)/(1.-pc)

def total_number_transmitted_messages(density, ttl):
    d=density
    return fsum(cf.exps[d].get_means()[0:ttl])*nb_tries_per_message(pc[d])

# -ICN_CNT_SEC_LEN: We don't need the ICN signature since the interest is never forwarded
# 2+1+NODE_ID_SIZE: NameComponent TLVs for /ndb/node_id
BEACON_SIZE = HDR_802154_LEN + ICN_CNT_HDR_LEN - ICN_CNT_SEC_LEN + 2 + 1 + NODE_ID_SIZE + SLOC

def name_size(number_of_nodes):
    return NUMBER_NAME_COMP + int(ceil(log(number_of_nodes,2)))

def geo_efficiency(number_of_nodes, density):
    nsize = name_size(number_of_nodes)
    p = pc[density]
    numerator = PAYLOAD_SIZE * LIFETIME
    denominator = BEACON_SIZE *nb_tries_per_message(p) + LIFETIME*(icn_geo_int_frame_size(nsize, SLOC)+icn_cnt_frame_size(nsize, PAYLOAD_SIZE)) * TTL * nb_tries_per_message(p) + (LIFETIME / CHANGE_RATE) * BEACON_SIZE * density * nb_tries_per_message(p)
    return numerator / denominator

def geo_energy_capacity(number_of_nodes, density, change_frequency):
    nsize = name_size(number_of_nodes)
    p = pc[density]
    ntr = nb_tries_per_message(p)
    res = float(AA_J)
    control = ((BEACON_SIZE * ntr * COST_TX_UJ + CRYPTO_UJ) + density * (BEACON_SIZE * ntr * COST_RX_UJ + CRYPTO_UJ)) / J_IN_UJ
    res = res - control
    denominator = control/change_frequency + TTL * (2*CRYPTO_UJ + ntr*(icn_geo_int_frame_size(nsize, SLOC)+icn_cnt_frame_size(nsize, PAYLOAD_SIZE))*(COST_RX_UJ+COST_TX_UJ)) / J_IN_UJ
    return res/denominator

def mpr_energy_capacity(number_of_nodes, density, change_frequency):
    nsize = name_size(number_of_nodes)
    p = pc[density]
    ntr = nb_tries_per_message(p)
    total = min(total_number_transmitted_messages(density, TTL), number_of_nodes*ntr/2)
    res = float(AA_J)
    #XXX Why TTL?
    #control = TTL*(float(total*2*CRYPTO_UJ)/ntr + total*icn_int_frame_size(nsize)*(COST_RX_UJ+COST_TX_UJ)) / J_IN_UJ
    control = (float(total*2*CRYPTO_UJ)/ntr + total*icn_int_frame_size(nsize)*(COST_RX_UJ+COST_TX_UJ)) / J_IN_UJ
    res = res - control
    denominator = control/change_frequency + TTL * (2*CRYPTO_UJ + ntr*(icn_int_frame_size(nsize)+icn_cnt_frame_size(nsize, PAYLOAD_SIZE))*(COST_RX_UJ+COST_TX_UJ)) / J_IN_UJ
    return res/denominator

def fl_efficiency(number_of_nodes, density):
    nsize = name_size(number_of_nodes)
    p = pc[density]
    numerator = PAYLOAD_SIZE * LIFETIME
    denominator = min(total_number_transmitted_messages(density, TTL), number_of_nodes/2)*(1+LIFETIME/CHANGE_RATE)*icn_int_frame_size(nsize) + LIFETIME * (icn_int_frame_size(nsize) + icn_cnt_frame_size(nsize, PAYLOAD_SIZE)) * TTL * nb_tries_per_message(p)
    return numerator / denominator

DENSITIES = np.array(range(4, 15, 1))
NODES     = np.array(range(10, 750))
X,Y = np.meshgrid(DENSITIES, NODES)
colorbar = (0.9, 1.8)

def plot_heatmap(change_rate):
    CHANGE_RATE = change_rate
    POINTS = np.array(map(lambda x : map(lambda y : geo_energy_capacity(y,x,CHANGE_RATE)/mpr_energy_capacity(y,x,CHANGE_RATE), NODES), DENSITIES))
    plt.pcolormesh(X,Y,POINTS.T, cmap="Greys_r")
    plt.colorbar()
    c = plt.contour(X,Y,POINTS.T, colors="white", levels=[1], linewidth=[2])
    plt.clabel(c, fmt="%1.1fx", inline = 1, fontsize=14, manual=[(10,100)])
    plt.text(4.6,150,'A', fontsize=18, color='w')
    plt.text(4,97,'B', fontsize=18, color='w')
    plt.text(13.4,700,'C', fontsize=18, color='black')
    plt.text(8,30,'D', fontsize=18, color='w')
    plt.xlabel(r"Average node degree $d$")
    plt.ylabel(r"Number of nodes $N_{nodes}$")

formatter = FuncFormatter(lambda x,y : '%dM' % (x*1e-6) if x!=0 else '')

def plot_examples(begin, end):
    fig = plt.figure()
    x_axis = range(begin, end)
    ax = fig.add_subplot(2,2,1)
    ax.set_xscale("log")
    plt.title('Example A')
    ax.yaxis.set_major_formatter(formatter)
    plt.ylim(0,8000000)
    y,x = 5,150
    plt.plot(x_axis, map(lambda f : geo_energy_capacity(x,y,f), x_axis), label='Geographic')
    plt.plot(x_axis, map(lambda f : mpr_energy_capacity(x,y,f), x_axis), label='mprF\&L')
    plt.legend(loc="lower right")
    ax = fig.add_subplot(2,2,2)
    ax.set_xscale("log")
    plt.title('Example B')
    ax.yaxis.set_major_formatter(formatter)
    plt.ylim(0,8000000)
    y,x = 4,97
    plt.plot(x_axis, map(lambda f : geo_energy_capacity(x,y,f), x_axis), label='Geographic')
    plt.plot(x_axis, map(lambda f : mpr_energy_capacity(x,y,f), x_axis), label='mprF\&L')
    plt.legend(loc="lower right")
    ax = fig.add_subplot(2,2,3)
    ax.set_xscale("log")
    plt.title('Example C')
    ax.yaxis.set_major_formatter(formatter)
    plt.ylim(0,8000000)
    y,x = 14,720
    plt.plot(x_axis, map(lambda f : geo_energy_capacity(x,y,f), x_axis), label='Geographic')
    plt.plot(x_axis, map(lambda f : mpr_energy_capacity(x,y,f), x_axis), label='mprF\&L')
    plt.legend(loc="lower right")
    ax = fig.add_subplot(2,2,4)
    ax.set_xscale("log")
    plt.title('Example D')
    ax.yaxis.set_major_formatter(formatter)
    plt.ylim(0,8000000)
    y,x = 8,30
    plt.plot(x_axis, map(lambda f : geo_energy_capacity(x,y,f), x_axis), label='Geographic')
    plt.plot(x_axis, map(lambda f : mpr_energy_capacity(x,y,f), x_axis), label='mprF\&L')
    plt.legend(loc="lower right")
    fig.text(0.5, 0.04, r'Number of measurements between 2 route changes $f_c$', ha='center', va='center')
    fig.text(0.07, 0.5, r'Number of possible measurements on one AA battery $N_m$', ha='center', va='center', rotation='vertical')

def plt_examples_unified(begin, end):
    matplotlib.rcParams.update({ 'font.size' : 14 })
    examples={'B': (4,97),'A': (5,150),'D': (8,30),'C': (14,720)}
    fig,ax = plt.subplots()
    x_axis = range(begin, end)
    ax.set_xscale("log")
    ax.yaxis.set_major_formatter(formatter)
    plt.ylim(0,8000000)
    colors = get_markers()[1]

    for ex in examples:
        color=colors.next()
        y,x = examples[ex]
        print "Example {} ({},{})".format(ex, x, y)
        plt.plot(x_axis, map(lambda f : geo_energy_capacity(x,y,f), x_axis), label='{} - Geo'.format(ex), linestyle="dashed", color=color)
        plt.plot(x_axis, map(lambda f : mpr_energy_capacity(x,y,f), x_axis), label='{} - mprF\&L'.format(ex), color=color)

    fig.text(0.5, 0.04, r'Number of measurements between 2 route changes $f_c$', ha='center', va='center')
    fig.text(0.07, 0.5, r'Number of possible measurements on one AA battery $N_m$', ha='center', va='center', rotation='vertical')
    plt.legend(loc='lower right')

def multiplot_heatmaps():
    plt.subplot(2,2,1)
    CHANGE_RATE = float(1 * 60 * 10)
    plt.title("1 change/10 hours")
    POINTS = np.array(map(lambda x : map(lambda y : geo_energy_capacity(y,x,CHANGE_RATE)/mpr_energy_capacity(y,x,CHANGE_RATE), NODES), DENSITIES))
    plt.pcolormesh(X,Y,POINTS.T, cmap="Greys_r")
    plt.clim(colorbar)
    plt.colorbar()
    c = plt.contour(X,Y,POINTS.T, colors="white", levels=[1], linewidth=[2])
    plt.clabel(c, fmt="%1.1fx", inline = 1, fontsize=14)
    plt.subplot(2,2,2)
    CHANGE_RATE = float(1*60*2)
    plt.title("1 change/2 hours")
    POINTS = np.array(map(lambda x : map(lambda y : geo_energy_capacity(y,x,CHANGE_RATE)/mpr_energy_capacity(y,x,CHANGE_RATE), NODES), DENSITIES))
    plt.pcolormesh(X,Y,POINTS.T, cmap="Greys_r")
    plt.clim(colorbar)
    plt.colorbar()
    c = plt.contour(X,Y,POINTS.T, colors="white", levels=[1])
    plt.clabel(c, fmt="%1.1fx", inline = 1, fontsize=14)
    plt.subplot(2,2,3)
    CHANGE_RATE = float(1*60)
    plt.title("1 change/hour")
    POINTS = np.array(map(lambda x : map(lambda y : geo_energy_capacity(y,x,CHANGE_RATE)/mpr_energy_capacity(y,x,CHANGE_RATE), NODES), DENSITIES))
    plt.pcolormesh(X,Y,POINTS.T, cmap="Greys_r")
    plt.clim(colorbar)
    plt.colorbar()
    c = plt.contour(X,Y,POINTS.T, colors="white", levels=[1])
    plt.clabel(c, fmt="%1.1fx", inline = 1, fontsize=14)
    plt.subplot(2,2,4)
    CHANGE_RATE = float(1*30)
    plt.title("2 changes/hour")
    POINTS = np.array(map(lambda x : map(lambda y : geo_energy_capacity(y,x,CHANGE_RATE)/mpr_energy_capacity(y,x,CHANGE_RATE), NODES), DENSITIES))
    plt.pcolormesh(X,Y,POINTS.T, cmap="Greys_r")
    plt.clim(colorbar)
    plt.colorbar()
    plt.contour(X,Y,POINTS.T, colors="white", levels=[1])
    plt.show()
