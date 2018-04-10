import flood_simulator_stats as fss
from itertools import cycle
import numpy as np

from constants import *

cf=fss.StatsExplorer("../sim_results/naiveflood_10000", 0)
mf=fss.StatsExplorer("../sim_results/mpr_10000", 0)

def get_markers ():
        markers = cycle(('s','+', '.', 'o', '*'))
        colors  = cycle(('blue', 'red', 'green', 'black'))
        linestyles = cycle(('solid', 'dashed', 'dotted'))
        return (markers, colors, linestyles)

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

def nb_tries_per_message(pc, mtr=5):
    return (1.-(pc**mtr)*(mtr+1.)+(pc**(mtr+1))*mtr)/(1.-pc)

def total_number_transmitted_messages(density, ttl):
    d=density
    return np.sum(cf.exps[d].get_means()[0:ttl])*nb_tries_per_message(pc[d])

# -ICN_CNT_SEC_LEN: We don't need the ICN signature since the interest is never forwarded
# 2+1+NODE_ID_SIZE: NameComponent TLVs for /ndb/node_id
def beacon_size(sloc):
    return HDR_802154_LEN + ICN_CNT_HDR_LEN - ICN_CNT_SEC_LEN + 2 + 1 + NODE_ID_SIZE + sloc

def name_size(number_of_nodes):
    return NUMBER_NAME_COMP + np.ceil(np.log2(number_of_nodes))

def geo_energy_capacity(number_of_nodes, density, change_frequency, payload_size=PAYLOAD_SIZE, sloc=SLOC, ttl=TTL):
    nsize = name_size(number_of_nodes)
    p = pc[density]
    ntr = nb_tries_per_message(p)
    res = float(AA_J)
    control = ((beacon_size(sloc) * ntr * COST_TX_UJ + CRYPTO_UJ) + density * (beacon_size(sloc) * ntr * COST_RX_UJ + CRYPTO_UJ)) / J_IN_UJ
    res = res - control
    denominator = control/change_frequency + ttl * (4*CRYPTO_UJ + ntr*(icn_geo_int_frame_size(nsize, sloc)+icn_cnt_frame_size(nsize, payload_size))*(COST_RX_UJ+COST_TX_UJ)) / J_IN_UJ
    return res/denominator

def mpr_energy_capacity(number_of_nodes, density, change_frequency, payload_size=PAYLOAD_SIZE, ttl=TTL):
    nsize = name_size(number_of_nodes)
    p = pc[density]
    ntr = nb_tries_per_message(p)
    total = min(total_number_transmitted_messages(density, ttl), number_of_nodes*ntr/2)
    res = float(AA_J)
    control = (float(total*2*CRYPTO_UJ)/ntr + total*icn_int_frame_size(nsize)*(COST_RX_UJ+COST_TX_UJ)) / J_IN_UJ
    res = res - control
    denominator = control/change_frequency + ttl * (4*CRYPTO_UJ + ntr*(icn_int_frame_size(nsize)+icn_cnt_frame_size(nsize, payload_size))*(COST_RX_UJ+COST_TX_UJ)) / J_IN_UJ
    return res/denominator


DENSITIES = np.arange(4, 15, 1)
NODES     = np.arange(10, 750)
X,Y = np.meshgrid(DENSITIES, NODES)
colorbar = (0.9, 1.8)
