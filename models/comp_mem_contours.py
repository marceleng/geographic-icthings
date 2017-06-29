import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.colors as colors
from math import floor, ceil, log
import numpy as np

URBAN_SENSORS = (1,1)
BDG_AUTO = (15,800)

x=np.array(range(URBAN_SENSORS[0],BDG_AUTO[0]))
y=np.array(range(URBAN_SENSORS[1],BDG_AUTO[1]))
X,Y=np.meshgrid(x,y)

#Forces matplotlib to use type 1 fonts
matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

matplotlib.rcParams.update({ 'font.size' : 16 })

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

adjustFigAspect(fig, 1.3)


LOC_SIZE = 8
NAME_SIZE = 12

def name_length (nb_names):
    return 12
    #return ceil(log(nb_names*10,2)/8)

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

def mem_cost_geo (nb_names, nb_neigh):
    return nb_neigh*(LOC_SIZE+name_length(nb_names)+1)

XTICKS=[0,2,4,6,8,10,12,14]
XLABELS=[r'$0$',r'$2$',r'$4$',r'$6$','',r'$10$','',r'$14$']
ax = plt.subplot(1,3,1)
ax.set_yscale('log')
fwd_points = map(lambda a : map(lambda b : fwd_cost_geo(a)/fwd_cost(b), y), x)
POINTS=np.array(fwd_points)
manual_locations=[(10,378),(9,170),(9.1, 85), (4,17), (10,23)]
cs = plt.contour(X,Y,POINTS.T,[0.25, 0.5,1,2, 4]) #, [0.5,1,2,4])
plt.clabel(cs, fmt="%gx", inline=1, fontsize=16, manual=manual_locations)

plt.ylabel("Number of FIB entries", fontsize=16)
plt.title("CPU")

plt.text(4.6,150,'A', fontsize=16)
plt.text(4,97,'B', fontsize=16)
plt.text(12.4,650,'C', fontsize=16)
plt.text(8,30,'D', fontsize=16)
plt.xlim((0,14))
plt.ylim((0,1000))
plt.xticks(XTICKS, XLABELS)

ax = plt.subplot(1,3,2)
ax.set_yscale('log')
mem_points = map(lambda a : map(lambda b : float(mem_cost_geo(b,a))/mem_cost(b), y), x)
POINTS=np.array(mem_points)
cs = plt.contour(X,Y,POINTS.T,[0.25,0.5,1,2,4])
manual_locations=[(10,59),(6,18),(10.,14),(10,7),(10,3)]
plt.clabel(cs, fmt="%gx", inline=1, fontsize=16, manual=manual_locations)

plt.title("Memory")
plt.xlabel("Number of neighbours", fontsize=16)
plt.yticks([])
plt.xticks(XTICKS, XLABELS)

plt.text(4.6,150,'A', fontsize=16)
plt.text(4,97,'B', fontsize=16)
plt.text(12.4,650,'C', fontsize=16)
plt.text(8,30,'D', fontsize=16)
plt.xlim((0,14))
plt.ylim((0,1000))

ax = plt.subplot(1,3,3)
ax.set_yscale('log')
def is_both_1 (a,b):
    return int(b<1)*2+int(a<1)

both=[[0]*len(y) for a in xrange(len(x))]
for i in range(len(x)):
    for j in range(len(y)):
        both[i][j] = is_both_1(mem_points[i][j],fwd_points[i][j])

POINTS=np.array(both)

plt.title("Combined")
plt.pcolormesh(X,Y,POINTS.T, cmap='Greys_r')
plt.yticks([])
plt.xticks(XTICKS, XLABELS)

plt.text(4.6,150,'A', fontsize=16)
plt.text(4,97,'B', fontsize=16)
plt.text(12.4,650,'C', fontsize=16)
plt.text(8,30,'D', fontsize=16, color='w')

pp = PdfPages("cpu_consump_contour.pdf")
pp.savefig(bbox_inches='tight')
pp. close()

plt.show()


