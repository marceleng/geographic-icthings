#include <stdlib.h>
#include <stdio.h>

#include "llist.h"

#define DEBUG printf("%s:%d\n",__FILE__,__LINE__)
struct ll_node
{
	struct ll_node *parent;
	struct ll_node *child;
	void *item;
};

int ll_pop_first(llist_t *l, void **buf)
{
	int ret = 0;
	if (l->head) {
		struct ll_node *old_head = l->head;
		*buf = old_head->item;
		ret = 1;
		if (l->head == l->tail) { //Only one element in the list
			l->head = l->tail = NULL;
		}
		else {
			l->head = l->head->child;
			l->head->parent = NULL;
		}
		free(old_head);
		l->size--;
	}
	return ret;
}

int ll_peek_first(llist_t *l, void **buf)
{
	int ret = 0;
	if (l->head) {
		ret = 1;
		*buf = l->head->item;
	}
	return ret;
}

int ll_pop_last(llist_t *l, void **buf)
{
	int ret = 0;
	if (l->tail) {
		struct ll_node *old_tail = l->tail;
		ret = 1;
		*buf = old_tail->item;
		if (l->tail == l->head) { //Only one element in the list
			l->tail = l->head = NULL;
		}
		else {
			l->tail = l->tail->parent;
			l->tail->child = NULL;
		}
		free(old_tail);
		l->size--;
	}
	return ret;
}

void _update_relation(struct ll_node *parent, struct ll_node *child)
{
	if (parent)
		parent->child = child;
	if (child)
		child->parent = parent;
}

int ll_peek_last(llist_t *l, void **buf)
{
	int ret = 0;
	if (l->head) {
		*buf = l->head->item;
		ret = 1;
	}
	return ret;
}

static int _insert_if_null(llist_t *l, struct ll_node *item) {
	int ret = 0;
	if (!l->head) {
		l->head = l->tail = item;
		ret = 1;
	}
	return ret;	
}

void ll_push_back(llist_t *l, void *item) {
	struct ll_node *node = (struct ll_node *) malloc(sizeof(struct ll_node));
	node->parent = node->child = NULL;
	node->item = item;

	if (!_insert_if_null(l, node)) {
		l->tail->child = node;
		node->parent = l->tail;
		l->tail = node;
	}
	l->size++;
}

void ll_push_front(llist_t *l, void *item) {
	struct ll_node *node = (struct ll_node *) malloc(sizeof(struct ll_node));
	node->parent = node->child = NULL;
	node->item = item;

	if (!_insert_if_null(l, node)) {
		l->head->parent = node;
		node->child = l->head;
		l->head = node;
	}
	l->size++;
}

int ll_search(llist_t *l, void *item)
{
	struct ll_node *cur;
	for(cur = l->head; cur; cur=cur->child ) {
		if (cur->item == item)
			return 1;
	}
	return 0;
}

void ll_remove(llist_t *l, void *item)
{
	struct ll_node *node = l->head;
	while (node) {
		if (node->item == item) {
			_update_relation(node->parent, node->child);
			if (!node->parent) {
				l->head = node->child;
			}

			if (!node->child) {
				l->tail = node->parent;
			}
		}
		struct ll_node *new_node = node->child;
		free(node);
		node = new_node;
		l->size--;
	}
}

int ll_isempty(llist_t *l) {
	return (!l->head);
}

void ll_empty(llist_t *l)
{
	struct ll_node *node = l->head;
	while(node && node->child) {
		node = node->child;
		free(node->parent);
	}
	if(node) free(node);
	l->head = l->tail = NULL;
	l->size = 0;
}
