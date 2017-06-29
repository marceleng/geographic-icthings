#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdio.h>

#include "graph.h"

#define INITIAL_NEIGHBOURHOOD_SIZE 8

static size_t ID = 0;

double urandom_double(double min, double max)
{
	double shot = (double) rand();
	return shot*(max-min)/(double)RAND_MAX+min;
}

double node_distance(node *x, node *y)
{
	return sqrt(pow(x->x - y->x, 2) + pow(x->y - y->y, 2));
}

node* node_alloc()
{
	node *n = (node *) malloc(sizeof(node));
	memset(n, 0, sizeof(node));
	n->id = (ID++);
	return n;
}

void node_urandom(node *n, double size_x, double size_y)
{
	n->x = urandom_double(0, size_x);
	n->y = urandom_double(0, size_y);
}

node* node_alloc_urandom(double size_x, double size_y)
{
	node *n = node_alloc();
	node_urandom(n, size_x, size_y);
	return n;
}

int node_equals(node* n1, node *n2)
{
	return (n1->id==n2->id);
}

void node_free(node *n)
{
	if (n->neigh)
		free(n->neigh);

	if (n-> mpr)
		free(n->mpr);

	free(n);
}

void _node_add_neigh(node *n, node *neigh)
{
	if (n->max_number_of_neigh == 0) {
		n->neigh = (node **) malloc(sizeof(node *)*INITIAL_NEIGHBOURHOOD_SIZE);
		n->max_number_of_neigh = INITIAL_NEIGHBOURHOOD_SIZE;
	}
	else if (n->number_of_neigh == n->max_number_of_neigh) {
		n->neigh = (node **) realloc((void *) n->neigh,
						sizeof(node *)*2*n->max_number_of_neigh);
		n->max_number_of_neigh *= 2;
	}

	n->neigh[n->number_of_neigh++] = neigh;
}

void node_add_vertice(node *n1, node *n2)
{
	_node_add_neigh(n1, n2);
	_node_add_neigh(n2, n1);
}


void node_urandom_graph (size_t number_of_nodes, size_t density, node** nodes)
{
	double space_size = sqrt(M_PI* (double) number_of_nodes/ (double)density);
	
	for (size_t i=0; i<number_of_nodes; i++) {
		nodes[i] = node_alloc_urandom(space_size, space_size);
		nodes[i]->id = i;
		for (size_t j=0; j<i; j++) {
			if (node_distance(nodes[i], nodes[j]) < 1) {
				node_add_vertice(nodes[i], nodes[j]);
			}
		}
	}
}

void node_print (node *n) {
	printf("<Node %zu (%0.2f,%0.2f): {", n->id, n->x, n->y);
	for (size_t i=0; i<n->number_of_neigh; i++) {
		printf("%zu", (n->neigh[i])->id);
		if (i<n->number_of_neigh-1)
			printf(", ");
	}
	printf("}>\n");
}	
