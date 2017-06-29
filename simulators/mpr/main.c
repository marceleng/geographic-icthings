#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <string.h>

#include "utils/graph.h"
#include "mpr.h"
#include "utils/llist.h"

#define VISITED 1
#define DEBUG printf("%s:%d\n",__FILE__,__LINE__)

static char *folder="results";

//BEWARE: results[i] must be empty for all i
//n->flag must be 0 for all nodes in graph
unsigned int traverse_graph(node *g, size_t number_of_nodes, unsigned int ttl, size_t *results)
{
	unsigned int round = 0;
	node *tmp_n, *relay;
	llist_t rounds[ttl+1];
	for (unsigned int i=0; i<=ttl; i++) {
		memset(&rounds[i], 0, sizeof(llist_t));
	}

	ll_push_front(&rounds[0], g);
	g->flag = VISITED;

	while(round < ttl) {
		results[round] = rounds[round].size;
		//TODO: Check whether list is empty and return ttl if so
		if(ll_isempty(&rounds[round])) {
			break;
		}

		while(ll_pop_first(&rounds[round], (void **) &tmp_n)) {
			if (!tmp_n->mpr) { //Computes MPR if necessary
				mpr_update_node(tmp_n, number_of_nodes);
			}
			for (size_t i=0; i<tmp_n->mpr_size; i++) {
				relay = tmp_n->neigh[tmp_n->mpr[i]];
				if (relay->flag != VISITED) { //Only adds non-visited nodes
					relay->flag = VISITED;
					ll_push_back(&rounds[round+1], relay);
				}
			}
			for (size_t i=0; i<tmp_n->number_of_neigh; i++) {
				tmp_n->neigh[i]->flag = VISITED;
			}
		}
		round++;
	}
	results[round] = rounds[round].size;

	//Free unused memory
	for (unsigned int i=0; i<=ttl; i++) {
		ll_empty(&rounds[i]);
	}

	return round;
}

void export(char *folder, size_t **results, unsigned int ttl, size_t number_of_nodes,
		size_t density, unsigned int number_of_tries)
{
	char buffer[128];
	memset(buffer, 0, sizeof(char)*128);
	time_t t = time(0);
	struct tm *time = localtime(&t);
	//YYYYMMDDHHMM
	char date[15];
	snprintf(date, 13, "%04d%02d%02d%02d%02d", time->tm_year+1900, time->tm_mon, time->tm_mday,
			time->tm_hour, time->tm_min);
	snprintf(buffer, 128, "%s/%zu_%zu_%u_%s_olsr.csv", folder, number_of_nodes, density,
			number_of_tries, date);
	
	FILE *file = fopen(buffer, "w+");

	for(unsigned int i=0; i<=ttl; i++) {
		fprintf(file, "%u ",i);
		for(unsigned int j=0; j<number_of_tries; j++) {
			fprintf(file, "%zu ", results[i][j]);
		}
		fprintf(file, "\n");
	}

	fclose(file);
}

void exp_step(size_t number_of_nodes, size_t density, unsigned int number_of_tries, unsigned int ttl)
{
	node *g[number_of_nodes];
	int graph_used = 0; //Boolean to keep track of whether g has been allocated
	size_t **results = (size_t **) malloc(sizeof(size_t *)*(ttl+1));
	for (unsigned int i=0; i<=ttl; i++)
		results[i] = (size_t *) malloc(sizeof(size_t)*number_of_tries);
	size_t temp_res[ttl+1];
	for (unsigned int i=0; i<number_of_tries; i++) {
		printf("Density=%zu, step=%u/%u\n", density, i+1, number_of_tries);
		do {
			if(graph_used) {
				for (size_t j=0; j<number_of_nodes; j++) {
					if(g[j]) node_free(g[j]);
				}
			}
			node_urandom_graph(number_of_nodes, density, (node **) g);
			graph_used=1;
		} while (traverse_graph(g[0], number_of_nodes, ttl, (size_t *) &temp_res) < ttl);
		for (unsigned int j=0; j<=ttl; j++) {
			results[j][i] = temp_res[j];
		}
		for (size_t j=0; j<number_of_nodes; j++) {
			node_free(g[j]);
		}
		graph_used = 0;
	}

	export(folder, (size_t **) results, ttl, number_of_nodes, density, number_of_tries);
	for (unsigned int i=0; i<=ttl; i++)
		free(results[i]);
	free(results);
}


int main (int argc, char** argv)
{
	if (argc < 5) {
		printf("Usage: ./mpr_flood_sim [number of nodes] [density] [ttl] [number of repetitions]\n");
		exit(EXIT_FAILURE);
	}

	setbuf(stdout, NULL);
	size_t number_of_nodes = strtoul(argv[1], NULL, 10);
	size_t density = strtoul(argv[2], NULL, 10);
	unsigned int ttl = strtol(argv[3], NULL, 10);
	unsigned int number_of_tries = strtol(argv[4], NULL, 10);

	exp_step(number_of_nodes, density, number_of_tries, ttl);
	return 0;
}
