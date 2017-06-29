import flood_simulator_stats as fss
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages
from itertools import cycle
from math import fsum, fabs
import numpy as np

plt.ion()
matplotlib.rcParams.update({ 'font.size' : 20 })

#Forces matplotlib to use type 1 fonts
matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

cf=fss.StatsExplorer("sim_results/naiveflood_10000", 0)
mf=fss.StatsExplorer("sim_results/mpr_10000", 0)

cf_s, mf_s = "solid", "dashed"

pc = {
        4 : 0.15,
        6: .21,
        8: .27,
        10: .32,
        12: .37,
        14: .42,
        16: .47,
        18: .51,
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

#### PACKET SIZE SECTION ####
#See https://www.ietf.org/mail-archive/web/icnrg/current/pdfs9ieLPWcJI.pdf
IEEE802154_HEADER_SIZE = 46
NONCE_SIZE = 4

def int_packet_size(payload_size, number_name_components=3, size_name_comp=4, with_nonce=False):
    base = IEEE802154_HEADER_SIZE + 1 #InterestType TL
    if payload_size > 0:
        base = base + (1+payload_size)
    if with_nonce:
        base = base + (1+NONCE_SIZE)
    return base + (1+number_name_components*(size_name_comp+1))

def cont_packet_size(payload_size, number_name_components=3, size_name_comp=4, with_sign=True):
    base = IEEE802154_HEADER_SIZE + 1 #ContentType TL
    if with_sign:
        base = base + 24 #Security info + signature
    return base + (1+payload_size) + (1+number_name_components*(size_name_comp+1))
##### END PACKET SIZE SECTION ####

def get_markers ():
        markers = cycle(('s','+', '.', 'o', '*'))
        colors  = cycle(('blue', 'red', 'green', 'black'))
        linestyles = cycle(('solid', 'dashed', 'dotted'))
        return (markers, colors, linestyles)

def plot_compared_average(cf, mf, d_values=range(4,16)):
    plt.clf()
    markers, colors, linestyles = get_markers()
    compared_means = {}
    for i in d_values:
        compared_means[i] = map(lambda x,y : x/y, cf.exps[i].get_means(), mf.exps[i].get_means()[:-1])
        plt.plot(range(0,15), compared_means[i], label=r"$d={}$".format(i), marker=markers.next(), color=colors.next(), linestyle=linestyles.next())
    lgd = plt.legend(ncol=3, loc="center", bbox_to_anchor=(0.49,1.03))
    plt.xlabel(r"$T-t$")
    #plt.ylabel(r"$\frac{|V_{t, \textrm{F\&L}}|}{|V_{t, \textrm{mprF\&L}}|}$", rotation=0, ha='right')
    plt.ylabel(r"Average $V_t$ value for F\&L wrt mprF\&L")
    return lgd

def plot_compared_average_vs_model(cf, mf, start=4, stop=15):
    plt.clf()
    markers, colors, linestyles = get_markers()
    ttls = range(1,15)
    ylim = (0, .35)
    for i in xrange(start, stop+1):
        marker = markers.next()
        color = colors.next()
        linestyle = linestyles.next()
        ax = plt.subplot(2,1,1)
        fitted_values = map(lambda x : cf.fittings[i][0]*x+cf.fittings[i][1], ttls)
        plt.plot(ttls, map(lambda x,y : fabs(x-y)/float(x), cf.exps[i].get_means()[1:], fitted_values),
                label=r"$d={}$".format(i), marker=marker, color=color, linestyle=linestyle)
        ax = plt.subplot(2,1,2)
        fitted_values = map(lambda x : mf.fittings[i][0]*x+mf.fittings[i][1], ttls)
        plt.plot(ttls, map(lambda x,y : fabs(x-y)/float(x), mf.exps[i].get_means()[1:-1], fitted_values),
                label=r"$d={}$".format(i), marker=marker, color=color, linestyle=linestyle)
    plt.subplot(2,1,1)
    plt.ylabel("Naive flood")
    plt.ylim(ylim)
    plt.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.6,1.3))
    plt.subplot(2,1,2)
    plt.ylabel("mprF\&L")
    plt.ylim(ylim)
    plt.xlabel(r"$T-t$")

def plot_compared_average_vs_model_errorbar(cf, mf, start=4, stop=15):
    plt.clf()
    markers, colors, linestyles = get_markers()
    ttls = range(2,15)
    densities = range(start, stop+1)
    ylim = (0, .35)
    #cf_values = map(lambda i : map(lambda x : cf.fittings[i][0]*x+cf.fittings[i][1], ttls), densities)
    cf_values = []
    mf_values = []
    for i in densities:
        cf_value = []
        mf_value = []
        for x in ttls:
            fitted_value = cf.fittings[i][0]*x+cf.fittings[i][1]
            avg_value = cf.exps[i].get_means()[x]
            cf_value.append(fabs(fitted_value - avg_value)/avg_value)
            fitted_value = mf.fittings[i][0]*x+mf.fittings[i][1]
            avg_value = mf.exps[i].get_means()[x]
            mf_value.append(fabs(fitted_value - avg_value)/avg_value)
        cf_values.append(cf_value)
        mf_values.append(mf_value)
    plt.subplot(2,1,1)
    plt.boxplot(cf_values, showfliers=False, positions=densities)
    t = plt.title("Naive flood")
    t.set_position([.5, .8])
    plt.subplot(2,1,2)
    plt.boxplot(mf_values, showfliers=False, positions=densities)
    t = plt.title("mpr flood")
    t.set_position([.5, .8])
    plt.xlabel(r"Density $d$")
    plt.text(2.40, 0.15, "Relative difference between the model and the simulation", va='center', rotation='vertical')

def plot_compared_average_model(cf, mf, start=4, stop=15):
    plt.clf()
    markers, colors, linestyles = get_markers()
    ttls = range(1,15)
    ylim = (1.5, 3.0)
    for i in xrange(start, stop+1):
        marker = markers.next()
        color = colors.next()
        linestyle = linestyles.next()
        ax = plt.subplot(2,1,1)
        compared_means = map(lambda x,y : x/y, cf.exps[i].get_means(), mf.exps[i].get_means()[:-1])[1:]
        plt.plot(ttls, compared_means, label=r"$d={}$".format(i), marker=marker, color=color, linestyle=linestyle)

        ax = plt.subplot(2,1,2)
        compared_means = map(lambda x : (cf.fittings[i][0]*x+cf.fittings[i][1])/(mf.fittings[i][0]*x+mf.fittings[i][1]), ttls)
        plt.plot(ttls, compared_means, label=r"$d={}$".format(i), marker=marker, color=color, linestyle=linestyle)
    plt.subplot(2,1,1)
    plt.ylabel(r"$\frac{|V_{t, \textrm{F\&L}}|}{|V_{t, \textrm{mprF\&L}}|}$ - Simulation")
    plt.ylim(ylim)
    plt.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.6,1.3))
    plt.subplot(2,1,2)
    plt.ylabel(r"$\frac{|V_{t, \textrm{naive}}|}{|V_{t, \textrm{mpr}}|}$ - Model")
    plt.xlabel(r"$T-t$")
    plt.ylim(ylim)

def plot_fittings(cf, mf, start=4, stop=15):
    plt.clf()
    s_m, i_m = "o", "+"
    keys = range(start, stop+1)
    plt.plot(keys, map(lambda x : cf.fittings[x][0], keys), label= "Naive - slope", marker=s_m, linestyle=cf_s)
    plt.plot(keys, map(lambda x : mf.fittings[x][0], keys), label= "MPR - slope", marker=s_m, linestyle=mf_s)
    plt.plot(keys, map(lambda x : cf.fittings[x][1], keys), label= "Naive - intercept", marker=i_m, linestyle=cf_s)
    plt.plot(keys, map(lambda x : mf.fittings[x][1], keys), label= "MPR - intercept", marker=i_m, linestyle=mf_s)
    plt.xlabel(r"Average node degree $d$")
    plt.legend(ncol=2, loc='upper center')

def plot_all_means(cf, mf, d_values=range(4,16)):
    plt.clf()
    ax = plt.subplot(1,2,1)
    plt.title("F\&L")
    naive_lines = cf.plot_subgraphs()
    plt.ylabel(r"$V_t$")
    for line in d_values:
        ax.add_line(naive_lines[line])
    plt.xlabel(r"$T-t$")
    plt.ylim([0,200])
    plt.xlim([0,14])

    ax = plt.subplot(1,2,2)
    plt.title("mprF\&L")
    mpr_lines = mf.plot_subgraphs()
    for line in d_values:
        ax.add_line(mpr_lines[line])
    plt.xlabel(r"$T-t$")
    plt.xlim([0,14])
    plt.ylim([0,200])

    plt.figlegend([naive_lines[line] for line in sorted(d_values)],
                  [ r"d={}".format(x) for x in sorted(d_values)], "center", ncol=3,
                  bbox_to_anchor=(0.49,1.03))

def plot_nbr_trans_nodes(cf, mf, start=4, stop=15, min_ttl=5, max_ttl=15):
    keys = range(start, stop+1)
    m, c, l = get_markers()
    ax1 = plt.subplot(1,2,1)
    ax2 = plt.subplot(1,2,2)
    naive_lines = []
    for t in xrange(min_ttl, max_ttl):
        marker = m.next()
        color = c.next()
        ls = l.next()
        li = Line2D(keys, map(lambda d : sum(cf.exps[d].get_means()[0:t]), keys), linestyle=ls, marker=marker, color=color)
        naive_lines.append(li)
        ax1.add_line(li)
        li = Line2D(keys, map(lambda d : sum(mf.exps[d].get_means()[0:t]), keys), linestyle=ls, marker=marker, color=color)
        ax2.add_line(li)
    plt.subplot(1,2,1)
    plt.ylim([0,1600])
    plt.xlim([0, stop+1])
    plt.ylabel(r"Total number of transmitting nodes $\sum_{t\in (0,TTL)} |V_t|$")
    plt.xlabel(r"Average node degree $d$")
    plt.title("Naive flood")
    plt.subplot(1,2,2)
    plt.ylim([0,1600])
    plt.xlim([0, stop+1])
    #plt.xlabel(r"Average node degree $d$")
    plt.title("MPR flood")
    plt.figlegend(naive_lines, [ r"TTL={}".format(x) for x in xrange(min_ttl, max_ttl)], "upper left", ncol=3, bbox_to_anchor=(0.,1.07))

def plot_nbr_trans_msg(cf, mf, d_values=range(4,15,2), ttl_values=range(5,15), maxMacRetry=5):
    keys = sorted(d_values)
    m, c, l = get_markers()
    ax1 = plt.subplot(1,2,1)
    ax2 = plt.subplot(1,2,2)
    naive_lines = []
    ylim=[0,2200]

    def nb_msg_per_node(d):
        return (1. - pow(pc[d], maxMacRetry)*(maxMacRetry+1.) + pow(pc[d],maxMacRetry+1)*maxMacRetry) / (1. - pc[d])

    for t in ttl_values:
        marker = m.next()
        color = c.next()
        ls = l.next()
        li = Line2D(keys, map(lambda d : sum(cf.exps[d].get_means()[0:t])*nb_msg_per_node(d), keys), linestyle=ls, marker=marker, color=color)
        naive_lines.append(li)
        ax1.add_line(li)
        li = Line2D(keys, map(lambda d : sum(mf.exps[d].get_means()[0:t])*nb_msg_per_node(d), keys), linestyle=ls, marker=marker, color=color)
        ax2.add_line(li)
    plt.subplot(1,2,1)
    plt.ylim(ylim)
    plt.xlim([0, keys[-1]])
    plt.ylabel(r"Total number of tries over delivery $N_{tr}(T,d)$")
    plt.xlabel(r"Node degree $d$")
    plt.title(r"F\&L")
    plt.subplot(1,2,2)
    plt.ylim(ylim)
    plt.xlim([0, keys[-1]])
    plt.yticks([])
    #plt.xlabel(r"Average node degree $d$")
    plt.title(r"mprF\&L")
    plt.figlegend(naive_lines, [ r"TTL={}".format(x) for x in ttl_values], "center", ncol=3, bbox_to_anchor=(0.49,1.03))

def plot_ratio_trans_msg(cf, mf, start=4, stop=15, min_ttl=5, max_ttl=15, d_step=2, maxMacRetry=5):
    keys = range(start, stop+1, 2)
    m, c, l = get_markers()
    naive_lines = []
    ylim=[0,2200]

    arr = map(lambda t : map(lambda d:  sum(cf.exps[d].get_means()[0:t])/ sum(mf.exps[d].get_means()[0:t]), keys), range(min_ttl, max_ttl))
    import numpy as np
    plt.plot(keys, np.mean(arr, axis=0))

    plt.legend()

def nb_tries_per_message(pc_fund, mtr=5):
    return (1.-(pc**mtr)*(mtr+1.)+(pc**(mtr+1))*mtr)/(1.-pc)

def plot_final_eq(cf, mf, pc_func, density_values=range(4,15), ttl_values=range(0,16), mtr=5):
    ec, em = [], []
    def coef(exp, d):
        return (lambda x : exp.fittings[d][0]*x+exp.fittings[d][1])
    for d in density_values:
        pc = pc_func(d)
        ec.append(
                fsum(map(lambda x : coef(cf,d)(x)*(1.-(pc**mtr)*(mtr+1.)+(pc**(mtr+1))*mtr)/(1.-pc), ttl_values)))
        em.append(
                fsum(map(lambda x : coef(mf,d)(x)*(1.-(pc**mtr)*(mtr+1.)+(pc**(mtr+1))*mtr)/(1.-pc), ttl_values)))
    
    plt.plot(density_values, ec, label="Naive flood")
    plt.plot(density_values, em, label="MPR flood")
    plt.xlim([0, stop])
    plt.xlabel(r"Density $d$")
    plt.ylabel(r"Number of messages transmission $\mathbf{E}[N_{tr}(T,d)]$")
    plt.legend(loc="upper left")
