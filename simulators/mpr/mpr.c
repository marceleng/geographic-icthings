#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <assert.h>

#include "mpr.h"
#include "utils/rbtree.h"
#include "utils/llist.h"
#include "utils/matrice.h"
#define DEBUG printf("%s:%d\n",__FILE__,__LINE__)

#include <time.h>

void _print_node(node *n)
{
	printf("<Node %zu, neigh={", n->id);
	for (size_t i=0; i<n->number_of_neigh; i++) {
		printf("%zu", n->neigh[i]->id);
		if (i == n->number_of_neigh - 1)
			printf("}");
		else
			printf(", ");
	}
	printf(">\n");
}

void mpr_node_to_matrice_tree(node *n, matrice *m)
{
	rbtree *n2_neigh_tree = NULL;
	uint nbr_neigh = n->number_of_neigh;
	node* neigh;
	for (size_t i = 0; i<nbr_neigh; i++) {
		neigh = n->neigh[i];
		for (size_t j=0; j<neigh->number_of_neigh; j++) {
			n2_neigh_tree = rbtree_insert(n2_neigh_tree, neigh->neigh[j], neigh->neigh[j]->id);
		}
	}

	size_t nbr_n2_neigh = rbtree_size(n2_neigh_tree);
	keyt_t id[nbr_n2_neigh];
	node *n2_neigh_arr[nbr_n2_neigh];

	rbtree_flatten(n2_neigh_tree, (void **) &n2_neigh_arr, (keyt_t *) id);
	
	matrice_resize(m, nbr_neigh, nbr_n2_neigh);

	//TODO: it can be easier if we use the rbtree in a better way, eg by storing the n1_neighbors in each n2 entry
	for (size_t i=0; i<nbr_neigh; i++) {
		neigh = n->neigh[i];
		for (size_t j=0; j<neigh->number_of_neigh; j++) {
			size_t idx = neigh->neigh[j]->id;
			
			//Searches for that id in *nbr_n2_neigh
			size_t start=0, stop=nbr_n2_neigh-1, new_bound;
			while (start<stop) {
				new_bound = (start+stop)/2;
				if (idx == id[new_bound]) {
					start=stop=new_bound;
				}
				else if (idx > id[new_bound]) {
					start=++new_bound;
				}
				else {
					stop=--new_bound;
				}
			}
			if(idx==id[start] || idx==id[stop]) {
				assert(idx==id[new_bound]);
				MATRICE_GET(m, i, new_bound) = 1;
			}
		}
	}
}


void mpr_node_to_matrice_array(node *n, matrice *m, size_t nbr_nodes)
{
	llist_t n2_neigh_arr[nbr_nodes];
	memset(n2_neigh_arr, 0, sizeof(llist_t)*nbr_nodes);

	node *neigh, *n2_neigh;
	uint nbr_neigh = n->number_of_neigh;
	size_t nb_n2_neigh = 0;
	for (size_t i=0; i<nbr_neigh; i++) {
		neigh = n->neigh[i];
		for (size_t j=0; j<neigh->number_of_neigh; j++) {
			n2_neigh = neigh->neigh[j];
			size_t n2_id = n2_neigh->id;
			if(n2_id != n->id) { //We do not had the origin
				if (ll_isempty(&n2_neigh_arr[n2_id])) {
					nb_n2_neigh++;
				}
				ll_push_back(&n2_neigh_arr[n2_id], (void *) i);
			}
		}
	}

	//Removes n1_neigh
	for (size_t i=0; i<nbr_neigh; i++) {
		neigh = n->neigh[i];
		llist_t *n2_list = &n2_neigh_arr[neigh->id];
		if(!ll_isempty(n2_list)) {
			ll_empty(n2_list);
			nb_n2_neigh--;	
		}
	}

	matrice_resize(m, nbr_neigh, nb_n2_neigh);

	size_t big_idx=0;
	llist_t * l;
	for(size_t i=0; i<nb_n2_neigh; i++) {
		//Finds next n2 neigh
		l = &n2_neigh_arr[big_idx];
		while (ll_isempty(l))
			l = &n2_neigh_arr[++big_idx];
		//TODO: update matrice
		size_t n1_neigh = 0;
		while (ll_pop_first(l, (void **) &n1_neigh)) {
			MATRICE_GET(m, n1_neigh, i) = 1;
		}
		big_idx++;
	}
}


/*
 * number_of_2_neighbors total number of 2-hop neighbors
 * 2_neighbors[i][j]: 1 iif i<->j
 * mpr_neighbor: buffer for sending result. Must be at least of size number_of_neighbors
 * returns the number of neighbors put in mpr_neighbors
 */
size_t greedy_mpr(matrice *n_n2_matrice, size_t *mpr_neighbors)
{
	size_t found_ngh = 0;
	size_t mpr_size=0;
	size_t nb_neigh = n_n2_matrice->height;
	size_t nb_n2_neigh = n_n2_matrice->width;

	matrice temp_m;
	temp_m.data = NULL;
	matrice *found = matrice_identity(nb_n2_neigh);
	matrice *all_1 = matrice_alloc(nb_n2_neigh, 1);

	while (found_ngh < n_n2_matrice->width) {
		//Removes already found 2-neighbours
		matrice_multiplication(n_n2_matrice, found, &temp_m);

		size_t max=0;
		matrice_fill(all_1, 1);
		matrice result;
		result.data = NULL;
		matrice_multiplication(&temp_m, all_1, &result); 

		//Finds node with max amount of n2 neighbours
		for (size_t i=0; i<nb_neigh; i++)
			if (MATRICE_GET(&result,i,0)>MATRICE_GET(&result,max,0))
				max = i;

		//Removes already selected nodes from matrice
		for(size_t i=0; i<nb_n2_neigh; i++) {
			if(MATRICE_GET(n_n2_matrice, max, i)) {
				MATRICE_GET(found, i, i) = 0;
			}
		}
		found_ngh += MATRICE_GET(&result, max, 0);
		mpr_neighbors[mpr_size++] = max;
		if(result.data) free(result.data);
	}
	if(temp_m.data) free(temp_m.data);
	matrice_free(all_1);
	matrice_free(found);

	return mpr_size;
}

void mpr_update_node(node *n, size_t max_node_id)
{
	matrice *m = matrice_alloc(1,1);
	size_t mpr_buffer[n->number_of_neigh];
	mpr_node_to_matrice_array(n, m, max_node_id);
	n->mpr_size  = greedy_mpr(m, (size_t *) &mpr_buffer);
	if(n->mpr) free(n->mpr);
	matrice_free(m);
	n->mpr = (size_t *) malloc(sizeof(size_t)*n->mpr_size);
	memcpy(n->mpr, mpr_buffer, n->mpr_size * sizeof(size_t));
}
