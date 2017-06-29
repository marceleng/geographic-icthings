#ifndef _LLIST_H_
#define _LLIST_H_

#include <stdlib.h>

typedef struct ll_node ll_node_t;
typedef struct linkedlist {
	ll_node_t *head;
	ll_node_t *tail;
	size_t size;
} llist_t;

//Returns 1 if element found, 0 if empty
int ll_pop_first(llist_t* l, void **item_buffer);
int ll_peek_first(llist_t* l, void **item_buffer);

int ll_pop_last(llist_t*, void **item_buffer);
int ll_peek_last(llist_t*, void **item_buffer);

void ll_push_back(llist_t *l, void *item);
void ll_push_front(llist_t *l, void *item);

int ll_search(llist_t *l, void *item);

void ll_remove(llist_t *l, void *item);

int ll_isempty(llist_t *l);

void ll_empty(llist_t *l);

#endif
