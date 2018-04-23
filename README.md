# On the cost of geography-centric things
This repository contains source code and scripts for the paper entitled *On the cost of geographic-forwarding for information centric things*. This tools are provided so that other researcher can quickly explore and reproduce the results, and build on our work.

## Structure of the directory
 * `simulators`: code used for simulating the flooding on a wireless sensor network
 * `sim_results`: results for the simulation campaign that we performed as CSV files
 * `models`: python code to compute the model results for the simulation results in `sim_results`
 * `geo_fwd_module`: C code (compatible with RIOT-OS) for compiling the next-hop with GPSR
 * [SOON] `paper`: LaTeX source code for the paper
 
## Exploring the results:
On top of the paper manuscript [LINK] We provide a [Jupyter Notebook](https://github.com/marceleng/geographic-icthings/blob/master/models/geographic-icthings.ipynb) to explore the results. Feel free to download it and run it with [Jupyter](https://jupyter.org/install)
