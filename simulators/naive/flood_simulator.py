#!/usr/local/bin/python
import threading, multiprocessing
import logging
from graph_construction import Node

TTL=15
RES_FOLDER = "results"

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

class ExpStep():

    def __init__(self, number_of_nodes, node_degree):
        self.number_of_nodes = number_of_nodes
        self.node_degree = node_degree
        self.ret = None
        self.graph = None

    def traverse_graph(self, origin, ttl):
        origin.seen=True
        pq = []
        pq.append((origin, 0))
        result = {}

        while pq:
            node, nb_hops = pq.pop(0)
            result[nb_hops] = result[nb_hops]+1 if nb_hops in result else 1
            for n in node.neigh:
                if not n.seen:
                    n.seen=True
                    if nb_hops < ttl:
                        pq.append((n, nb_hops+1))

        return result

    def run(self):
        g = Node.create_graph(self.number_of_nodes, self.node_degree)
        r = self.traverse_graph(g[0], TTL)
        self.ret = r

    def get_result(self):
        return self.graph, self.ret

class ExpInst(multiprocessing.Process):

    def __init__(self, number_of_nodes, node_degree, number_of_tries, pipe, status_evt, stop_evt):
        super(ExpInst, self).__init__()
        self.number_of_nodes = number_of_nodes
        self.node_degree = node_degree
        self.number_of_tries = number_of_tries
        self.ret = None
        self.l = None
        self.cnt = 0
        self.lock = threading.Lock()
        self.done_evt = threading.Event()
        self.pipe = pipe
        self.status_evt = status_evt
        self.stop_evt = stop_evt

    def run(self):
        degrees = []
        ret = []

        status_thr = threading.Thread(target=self.listen_for_status)
        status_thr.start()

        while self.cnt < self.number_of_tries:
            if self.stop_evt.is_set():
                break
            #log.debug("Step %d"%cnt)
            e = ExpStep(self.number_of_nodes, self.node_degree)
            e.run()
            g,r = e.get_result()
            if (len(r) > TTL):
                ret.append(r)
                self.lock.acquire()
                self.cnt += 1
                self.lock.release()

        #plt.hist(degrees, 50)
        #plt.show()
        self.ret = ret
        log.info("Process {} is done, exporting to {}".format(self, self._filename()))
        self.done_evt.set()
        self.status_evt.set()
        status_thr.join()
        self.export()

    def listen_for_status(self):
        while not self.done_evt.isSet():
            self.status_evt.wait()
            self.lock.acquire()
            log.info(str(self))
            self.lock.release()
            self.status_evt.clear()
        
    @staticmethod
    def dict_to_list(d):
        indexes = list(d.keys())
        indexes.sort()
        ret = []
        for i in indexes:
            ret.append(d[i])
        return ret

    def get_stats(self):
        self.l = map(self.dict_to_list, self.ret)
        return self.l

    def _filename(self):
        import time
        cnt = self.cnt
        date=time.strftime("%Y%m%d%H%M")
        return "{}_{}_{}_{}.csv".format(self.number_of_nodes, self.node_degree, cnt, date)

    def export(self):
        if not self.l:
            self.get_stats()
        f=open("{}/{}".format(RES_FOLDER, self._filename()), 'w')
        for i in xrange(TTL):
            f.write("%d "%i)
            f.write(str(map(lambda x : x[i], self.l)).replace(',','')[1:-1])
            f.write('\n')
        f.close()

    def __str__(self):
        return "<ExpInst, alive={}, number_of_nodes={}, node_degree={}, current_step={}/{}>".format(
            self.is_alive(), self.number_of_nodes, self.node_degree, self.cnt, self.number_of_tries)
        
class ExpManager:

    def __init__(self, number_of_nodes, number_of_tries, min_degree, max_degree, step=1):
        self.number_of_nodes= number_of_nodes
        self.number_of_tries = number_of_tries
        self.degrees = xrange(min_degree, max_degree, step)
        self.processes = {}
        self.pipes = {}
        self.status_evt = {}
        self.stop_evt = {}

    def start_exp(self):
        for i in self.degrees:
            self.pipes[i],pipe = multiprocessing.Pipe()
            self.stop_evt[i] = multiprocessing.Event()
            self.status_evt[i] = multiprocessing.Event()
            self.processes[i] = ExpInst(self.number_of_nodes, i, self.number_of_tries, pipe, 
                    self.status_evt[i], self.stop_evt[i])
            self.processes[i].start()
            
    def status_exp(self):
        for evt in self.status_evt:
            self.status_evt[evt].set()

    def stop_exp(self):
        for evt in self.stop_evt:
            self.stop_evt[evt].set()
        for process in self.processes:
            self.processes[process].join()
