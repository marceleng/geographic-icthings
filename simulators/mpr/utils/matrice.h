#ifndef _MATRICE_H_
#define _MATRICE_H_

typedef unsigned int uint;

//m_(i,j) = m[i*width+j]
typedef struct {
	uint height;
	uint width;
	uint *data;
} matrice;

#define MATRICE_GET(m,i,j) ((m)->data)[i*(m)->width+j]
#define EMPTY_MATRICE() {.height=0, .width=0, .data=NULL}
#define MATRICE_LENGTH(m) (m->width*m->height)

void matrice_print(matrice *m);

matrice* matrice_alloc(uint height, uint width);

void matrice_resize(matrice *m, uint new_height, uint new_width);

void matrice_free(matrice *m);

void matrice_copy(matrice *dest, matrice *source);

void matrice_multiplication(matrice *m1, matrice *m2, matrice *r);

void matrice_fill(matrice *m, uint x);

void matrice_random_fill(matrice *m);

matrice* matrice_identity(uint n);

#endif
