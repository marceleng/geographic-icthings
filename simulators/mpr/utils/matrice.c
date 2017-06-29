#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "matrice.h"


void matrice_print(matrice *m)
{
	assert(m && m-> data);

	printf("Matrice %ux%u:\n", m->height, m->width);
	for (uint i=0; i<m->height; i++) {
		printf ("[ ");
		for(uint j=0; j<m->width; j++) {
			printf("%u ", MATRICE_GET(m,i,j));
		}
		printf("]\n");
	}
}

matrice* matrice_alloc(uint height, uint width) {
	matrice* m = (matrice *) malloc(sizeof(matrice));
	m->height = height;
	m->width = width;
	m->data = (uint *) malloc(sizeof(uint)*width*height);
	memset(m->data, 0, sizeof(uint)*width*height);
	return m;
}

void matrice_resize(matrice *m, uint new_height, uint new_width) {
	assert(m);

	if (m->data)
		free(m->data);

	m->data = (uint *) malloc(sizeof(uint)*new_height*new_width);
	memset(m->data, 0, sizeof(uint)*new_width*new_height);
	m->height = new_height;
	m->width = new_width;
}

void matrice_free(matrice *m) {
	if (m->data)
		free(m->data);
	free(m);
}

void matrice_copy(matrice *dest, matrice *source) {
	assert(source && dest);

	matrice_resize(dest, source->height, source->width);
	memcpy(dest->data, source->data, sizeof(uint)*MATRICE_LENGTH(dest));
}

/*
 * a: matrice
 * b: matrice
 * c: matrice
 * Condition: 
 * Result: c=a*b
 */
void matrice_multiplication(matrice *m1, matrice *m2, matrice *r)
{
	assert((m1->width == m2->height));

	matrice_resize(r, m1->height, m2->width);

	for (uint i=0; i<m1->height; i++) {
		for (uint j=0; j<m2->width; j++) {
			for (uint k=0; k<m1->width; k++) {
				MATRICE_GET(r,i,j) += MATRICE_GET(m1,i,k)*MATRICE_GET(m2,k,j);
			}
		}
	}
}

void matrice_fill(matrice *m, uint x)
{
	assert(m && m->data);
	for(int i=0; i<MATRICE_LENGTH(m); i++)
		m->data[i] = x;
}

void matrice_random_fill(matrice *m)
{
	assert(m && m->data);

	for(uint i=0; i<MATRICE_LENGTH(m); i++)
		m->data[i] = ((uint) rand())%2;
}

matrice* matrice_identity(uint n)
{
	matrice *m=matrice_alloc(n,n);
	for (int i=0; i<n; i++)
		MATRICE_GET(m, i, i) = 1;

	return m;
}
