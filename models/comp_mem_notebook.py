from math import floor, ceil, log
import numpy as np

URBAN_SENSORS = (1,1)
BDG_AUTO = (15,800)

def name_length (nb_names):
    #return 12
    return ceil(log(nb_names*10,2)/8)

CPU_AMP=13./1000
CPU_FREQ=32*1000000
COST_OF_CYCLE_UJ=3.*CPU_AMP/CPU_FREQ*1000000
COST_NEIGH_UJ=620*COST_OF_CYCLE_UJ
INTERCEPT_NEIGH_UJ=577*COST_OF_CYCLE_UJ
COST_FIB_UJ=70*COST_OF_CYCLE_UJ
INTERCEPT_FIB_UJ=202*COST_OF_CYCLE_UJ

def fwd_cost (nb_names):
    return COST_FIB_UJ*nb_names+INTERCEPT_FIB_UJ

def fwd_cost_geo (nb_neigh):
    return COST_NEIGH_UJ*nb_neigh+INTERCEPT_NEIGH_UJ

def mem_cost (nb_names):
    return nb_names*(name_length(nb_names)+2)

def mem_cost_geo (nb_names, nb_neigh, sloc):
    return nb_neigh*(sloc+name_length(nb_names)+1)
