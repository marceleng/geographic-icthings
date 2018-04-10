#!/usr/bin/local/python

from math import log,ceil,floor
import matplotlib.colors as colors
import numpy as np
from itertools import product

from constants import icn_int_packet_size, icn_geo_int_packet_size, HDR_802154_LEN, icn_cnt_packet_size

from model_result_notebook import nb_tries_per_message, pc

URBAN_SENSORS = (1,1)
BDG_AUTO = (20,2000)

AGGREGATION_DEGREE = 1

def nb_names(nb_neigh):
    #return 14250-850*nb_neigh
    x = float(URBAN_SENSORS[1]-BDG_AUTO[1]) / float(URBAN_SENSORS[0]-BDG_AUTO[0]);
    y = float (URBAN_SENSORS[0]*BDG_AUTO[1]-URBAN_SENSORS[1]*BDG_AUTO[0]) / float(URBAN_SENSORS[0]-BDG_AUTO[0])
    return ceil(x*nb_neigh+y)
    #return floor((URBAN_SENSORS[1]-BDG_AUTO[1])/(URBAN_SENSORS[0]-BDG_AUTO[0]) * nb_neigh +
    #        (URBAN_SENSORS[0]*BDG_AUTO[1]-URBAN_SENSORS[1]*BDG_AUTO[0])/(URBAN_SENSORS[0]-BDG_AUTO[0]))

RT_INTEREST=1

COST_RX_UJ=0.96
COST_TX_UJ=1.163
CPU_AMP=13./1000
CPU_FREQ=32*1000000
COST_OF_CYCLE_UJ=3.*CPU_AMP/CPU_FREQ*1000000
COST_NEIGH_UJ=620*COST_OF_CYCLE_UJ
INTERCEPT_NEIGH_UJ=577*COST_OF_CYCLE_UJ
COST_FIB_UJ=70*COST_OF_CYCLE_UJ
INTERCEPT_FIB_UJ=202*COST_OF_CYCLE_UJ

def fib_size(nb_names):
    return ceil(nb_names*AGGREGATION_DEGREE)

def name_length (nb_names):
    #return 20
    return ceil(log(nb_names,2)/8)

#Geo specific
LOC_SIZE = 8
RT_BEACON=0
def beacon_size (loc_size):
    return 31+loc_size
def geo_name_length(name_lgth, loc_size):
    return name_lgth # + LOC_SIZE + 5

PAYLOAD_SIZE = 32
def data_msg_length (name_lgth):
    return hdr_length(name_lgth) + PAYLOAD_SIZE

def decrypt_uj(l):
    return 10

def encrypt_uj(l):
    return 10

def crypto_cost_uj (l):
    return (decrypt_uj(l)+encrypt_uj(l))

def reception_cost (l):
    return COST_RX_UJ*l 

def transmission_cost(l):
    return COST_TX_UJ*l

def beacon_cost (nb_neigh, loc_size):
    return (transmission_cost(beacon_size(loc_size)) + nb_neigh*reception_cost(beacon_size(loc_size)))*RT_BEACON

def communication_cost (interest_lgth):
    return reception_cost(interest_lgth)+transmission_cost(interest_lgth)

def interest_cost_fib (nb_names, name_lgth):
    return RT_INTEREST*(communication_cost(hdr_length(name_lgth)) + COST_FIB_UJ*fib_size(nb_names))

def interest_cost_geo (nb_neigh, nb_names, name_lgth, loc_size):
    return RT_INTEREST*(communication_cost(geo_hdr_length(name_lgth, loc_size)) + COST_NEIGH_UJ*nb_neigh+INTERCEPT_NEIGH_UJ)

def fib_cost (nb_names, name_lgth):
    return interest_cost_fib (nb_names, name_lgth)

def geo_cost (nb_names, nb_neigh, name_lgth, loc_size):
    return beacon_cost(nb_neigh, loc_size)+interest_cost_geo(nb_neigh, nb_names, name_lgth, loc_size)
###
### Stacked bar plots
###
'''
BASELINE={"name length" : [5,20], "nb neigh" : [5, 20], "nb names" : [5], "loc size" : [1,8]}
#SCENARIOS=list(product(*map(lambda x : x[1], BASELINE.iteritems())))
SCENARIOS=[[10,4,97,4],[11,5,150,8],[8,8,30,1],[13,15,250,8]]
print SCENARIOS
ind=np.arange(0.15,len(SCENARIOS)+.15)
width=0.35

fig, ax = plt.subplots()

## WITHOUT LOG
comm_cost = map(lambda x : nb_tries_per_message(pc[x[1]])*communication_cost(icn_int_packet_size(x[0]) + icn_cnt_packet_size(x[0], PAYLOAD_SIZE)), SCENARIOS)
crypto_cost = map(lambda x : crypto_cost_uj(icn_int_packet_size(x[0]))+crypto_cost_uj(icn_cnt_packet_size(x[0], PAYLOAD_SIZE)), SCENARIOS)
fwd_cost = map(lambda x : COST_FIB_UJ*fib_size(x[2])+INTERCEPT_FIB_UJ, SCENARIOS)

comm_cost_geo = map(lambda x : nb_tries_per_message(pc[x[1]])*communication_cost(icn_geo_int_packet_size(x[0], x[3]) + icn_cnt_packet_size(x[0], PAYLOAD_SIZE)), SCENARIOS)
crypto_cost_geo = map(lambda x : crypto_cost_uj(icn_geo_int_packet_size(x[0], x[3])) + crypto_cost_uj(icn_cnt_packet_size(x[0], PAYLOAD_SIZE)), SCENARIOS)
fwd_cost_geo = map(lambda x : COST_NEIGH_UJ*x[1]+INTERCEPT_NEIGH_UJ, SCENARIOS)

ax.set_ylabel(r"Energy cost ($\mu J$)")

hdr_arr = [2*HDR_802154_LEN*(COST_RX_UJ+COST_TX_UJ)]*len(SCENARIOS)
hdr = ax.bar(ind, hdr_arr, width, color='w', hatch="//", edgecolor='black', bottom=comm_cost)
comm = ax.bar(ind, comm_cost, width, color='w')
crypto = ax.bar(ind, crypto_cost, width, bottom=map(lambda x,y : x+y, hdr_arr, comm_cost), color='grey')
fwd = ax.bar(ind, fwd_cost, width, bottom=map(lambda x,y,z : x+y+z, crypto_cost, comm_cost, hdr_arr), color='black')

hdr_geo = ax.bar(ind+width, hdr_arr, width, color='w', hatch="//", bottom=comm_cost_geo)
comm_geo = ax.bar(ind+width, comm_cost_geo, width, color='w')
crypto_geo = ax.bar(ind+width, crypto_cost_geo, width, bottom=map(lambda x,y : x+y, comm_cost_geo, hdr_arr), color='grey')
fwd_geo = ax.bar(ind+width, fwd_cost_geo, width, bottom=map(lambda x,y,z : x+y+z, crypto_cost_geo, comm_cost_geo, hdr_arr), color='black')

plt.legend([comm[0], hdr[0], crypto[0], fwd[0]],('Communication (L3)','Communication (L2 hdr)','Cryptography','Forwarding'), loc='upper center', bbox_to_anchor=(0,1.06,1,0.102), ncol=2, mode="expand")
#plt.ylim((0,520))

ax.set_xticks(ind+width)
ax.set_xticklabels(map(lambda x, y : ('\n'.join(("Use case "+y,"$s_{{name}}={0}$",r"$n_{{neigh}}={1}$",r"$s_{{loc}}={3}$"))).format(*x), SCENARIOS, ["A", "B", "C", "D"]), fontsize=18)
plt.subplots_adjust(bottom=0.18)

def label_bar (rects, label):
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 0.1, label, ha='center', va='bottom')

label_bar(fwd,"FIB")
label_bar(fwd_geo,"GEO")
pp = PdfPages("fib_geo_stacked_bar.pdf")
pp.savefig()
pp. close()

plt.show()
'''
