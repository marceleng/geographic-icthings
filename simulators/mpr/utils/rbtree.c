#include <string.h>
#include <assert.h>
#include <stdio.h>

#include "rbtree.h"

#define COLOR_RED 1
#define COLOR_BLACK 2
#define COLOR_DOUBLE_BLACK 3
#define COLOR_UNDEF 0

#define LEFT 1
#define RIGHT 0

#define CHILD(node,side) (((side)==LEFT) ? node->lchild : node->rchild)
#define SIDE(node) ((node==node->parent->lchild) ? LEFT : RIGHT)

#define DEBUG printf("%s:%u\n",__FILE__,__LINE__)

static int DEFAULT_POLICY = POLICY_IGNORE;

void rbtree_set_default_policy(int policy)
{
	assert(policy == POLICY_IGNORE || policy==POLICY_INSERT
#ifdef POLICY_OVERRIDE
			|| policy==POLICY_OVERRIDE
#endif
			);

	DEFAULT_POLICY = policy;
}

int rbtree_get_default_policy()
{
	return DEFAULT_POLICY;
}

size_t rbtree_size(rbtree *tree)
{
	if (!tree)
		return 0;
	else
		return 1+rbtree_size(tree->lchild)+rbtree_size(tree->rchild);
}

void _rbtree_update_child(rbtree * tree, rbtree *child, int left)
{
	if (left)
		tree->lchild = child;
	else
		tree->rchild = child;

	if (child)
		child->parent = tree;
}

rbtree* _rbtree_search(rbtree *tree, keyt_t key)
{
	if (!tree) {
		return NULL;
	}
	else if (key == tree->key) {
		return tree;
	}
	else if (key < tree->key) {
		return _rbtree_search(tree->lchild, key);
	}
	else {
		return _rbtree_search(tree->rchild, key);
	}
}

rbtree * _rbtree_bst_insert(rbtree *tree, rbtree *node, int policy, int *modified)
{
	*modified = 1;
	if (!tree) {
		tree = node;
	}
	else if (node->key == tree->key && policy != POLICY_INSERT) {
#ifdef POLICY_OVERRIDE
		if (policy == POLICY_OVERRIDE) {
			//TODO: figure out what happens with tree->item. Should it be freed? (no)
			tree->item = node->item;
		}
#endif
		*modified = 0;
	}
	else if (node->key < tree->key) {
		_rbtree_update_child(tree, _rbtree_bst_insert(tree->lchild, node, policy, modified), LEFT);
	}
	else {
		_rbtree_update_child(tree, _rbtree_bst_insert(tree->rchild, node, policy, modified), RIGHT);
	}

	return tree;
}

rbtree* rbtree_alloc()
{
	rbtree *node = (rbtree *) malloc(sizeof(rbtree));
	memset(node, 0, sizeof(rbtree));
	return node;
}

void rbtree_free(rbtree *tree)
{
	if (tree->lchild)
		rbtree_free(tree->lchild);
	else if (tree->rchild)
		rbtree_free(tree->rchild);
	free(tree->item);
	free(tree);
}

rbtree* _rbtree_gp(rbtree *node)
{
	if (!node->parent)
		return NULL;
	else
		return node->parent->parent;
}

rbtree* _rbtree_s(rbtree *node, int *side)
{
	rbtree *ret = NULL;
	if (node->parent) {
		if (node == node->parent->lchild){
			*side = LEFT;
			ret = node->parent->rchild;
		}
		else {
			*side = RIGHT;
			ret = node->parent->lchild;
		}
	}
	return ret;
}

rbtree* _rbtree_u(rbtree *node)
{
	rbtree *ret = _rbtree_gp(node);
	if (ret) {
		if (node->parent == ret->lchild)
			ret = ret->rchild;
		else
			ret = ret->lchild;
	}
	return ret;
}

rbtree* _rbtree_rotate_left(rbtree *tree)
{
	rbtree *old_root = tree->parent;

	assert(old_root && tree == old_root->rchild);

	_rbtree_update_child(old_root, tree->lchild, RIGHT);
	if (old_root->parent) {
		int side = (old_root == old_root->parent->lchild) ? LEFT : RIGHT;
		_rbtree_update_child(old_root->parent, tree, side);
	}
	else { /* Old root has not parent -> It's the root */
		tree->parent = NULL;
	}
	_rbtree_update_child(tree, old_root, LEFT);

	return tree;
}

rbtree* _rbtree_rotate_right(rbtree *tree)
{

	rbtree *old_root = tree->parent;

	assert(old_root && tree == old_root->lchild);

	if (old_root->parent) {
		int side = (old_root == old_root->parent->lchild) ? LEFT : RIGHT;
		_rbtree_update_child(old_root->parent, tree, side);
	}
	else { /* Old root has not parent -> It's the root */
		tree->parent = NULL;
	}
	_rbtree_update_child(old_root, tree->rchild, LEFT);
	_rbtree_update_child(tree, old_root, RIGHT);

	return tree;
}

rbtree *_rbtree_rotate(rbtree *tree, int side)
{
	switch (side) {
	case LEFT:
		return _rbtree_rotate_left(tree);
	case RIGHT:
		return _rbtree_rotate_right(tree);
	default:
		return tree;
	}
}

rbtree* rbtree_insert(rbtree *tree, void *item, keyt_t key)
{
	return rbtree_insert_policy(tree, item, key, DEFAULT_POLICY);
}

rbtree* rbtree_insert_policy(rbtree *tree, void *item, keyt_t key, int policy)
{
	rbtree *node = rbtree_alloc();
	node->key = key;
	node->item = item;
	node->color = COLOR_RED;

	int modified;

	tree = _rbtree_bst_insert(tree, node, policy, &modified);

	if (!modified) {
		free(node);
	}
	else {
		while (node->parent && node->parent->color == COLOR_RED) {
			rbtree *u = _rbtree_u(node), *gp = _rbtree_gp(node), *p = node->parent;
			if(u && u->color==COLOR_RED) {//parent and uncle are red-> switch them to black
				node->parent->color = COLOR_BLACK;
				u->color = COLOR_BLACK;
				gp->color = COLOR_RED;
				node = gp;
			}
			else {
				if(p==gp->lchild) {
					if (node==p->rchild) {
						_rbtree_rotate_left(node);
						node = node->lchild;
						p = node->parent;
					}
					_rbtree_rotate_right(p);
					node->color = COLOR_RED;
					p->color = COLOR_BLACK;
					p->rchild->color = COLOR_RED;
				}
				else { /* p==gp->rchild */
					if(node==p->lchild) {
						_rbtree_rotate_right(node);
						node = node->rchild;
						p = node->parent;
					}
					_rbtree_rotate_left(p);
					node->color = COLOR_RED;
					p->color = COLOR_BLACK;
					p->lchild->color = COLOR_RED;
				}
			}
		}

		while (tree->parent)
			tree = tree->parent;

		tree->color = COLOR_BLACK; //Root must be black
	}
	return tree;
}

void _rbtree_flatten(rbtree *x, void **item_buffer, keyt_t *key_buffer, size_t *count)
{
	if (x) {
		_rbtree_flatten(x->lchild, item_buffer, key_buffer, count);
		key_buffer[*count] = x->key;
		item_buffer[(*count)++] = x->item;
		_rbtree_flatten(x->rchild, item_buffer, key_buffer, count);
	}
}

void *rbtree_search(rbtree *tree, keyt_t key)
{
	rbtree *ret = _rbtree_search(tree, key);
	return (ret) ? ret->item : NULL;
}

rbtree *rbtree_remove(rbtree *tree, keyt_t key, void **item_buf)
{
	rbtree *node = _rbtree_search(tree, key);
	*item_buf = node->item;

	//TODO: removes and balances
	int child_side=RIGHT;


	//Do the necessary magic to get to the case where node has only one child
	if(node->lchild) {
		//If node has two children, find sucessor (necessarily a one-child node)
		if (node->rchild) {
			rbtree *suc = node->rchild;
			for (; suc->lchild; suc = suc->lchild);
			node->key = suc->key;
			node->item = suc->item;
			node = suc;
			//Now node has at most one right child
			child_side = RIGHT;
		}
		else {
			child_side = LEFT;
		}
	}

	rbtree *child=CHILD(node, child_side), *p= node->parent;
	rbtree *to_destroy = NULL;

	// Artificially creates DOUBLE_BLACK node to simplify code
	if (!child) {
		child = (rbtree *) malloc(sizeof(rbtree));
		memset(child, 0, sizeof(rbtree));
		child->color = COLOR_DOUBLE_BLACK;
		to_destroy = child;
	}


	if (p) {
		_rbtree_update_child(p, child, SIDE(node));
	}
	else { //node is the root?
		assert(node==tree);
		tree = child;
	}

	// If one of node, node->child is RED (thus the other black)
	// Just move the child one level up and color it black
	if (node->color == COLOR_RED || (child->color == COLOR_RED)) {
		if (child) {
			child->color = COLOR_BLACK;
		}
	}
	else {
		while ((p=child->parent) || child->color==COLOR_DOUBLE_BLACK) {
			int sside = !SIDE(child); //Side of the sibling
			rbtree *s = CHILD(p, sside);
			if (s && s->color == COLOR_RED) {
				_rbtree_rotate(s, !sside);
				s->color = COLOR_BLACK;
				p->color = COLOR_RED;
			}
			else { //s->color==COLOR_BLACK
				//1. Test if all children are black
				if(!s || ((!s->rchild || s->rchild->color == COLOR_BLACK) &&
				          (!s->lchild || s->lchild->color == COLOR_BLACK))) {
					s->color = COLOR_RED;
					p->color = (p->color == COLOR_BLACK) ? COLOR_DOUBLE_BLACK : COLOR_BLACK;
					child = p;
				}
				else { // 2. One of the children of s is red
					//2.1 If the child is not aligned with s and its parent, rotate
					if ( !CHILD(s, sside) || CHILD(s, sside)->color != COLOR_RED) {
						s = _rbtree_rotate(CHILD(s, !sside), sside);
						s->color = COLOR_BLACK;
						CHILD(s, sside)->color = COLOR_RED;
					}
					//2.2 Now s and its red child are aligned
					child = _rbtree_rotate(s, !sside);
					child->color = COLOR_BLACK;
					if (child->lchild)
						child->lchild->color = COLOR_BLACK;
					if (child->rchild)
						child->rchild->color = COLOR_BLACK;
				}
			}
		}
	}

	if (to_destroy) {
		assert(!(to_destroy->lchild || to_destroy->rchild));
		if (SIDE(to_destroy) == LEFT)
			to_destroy->parent->lchild = NULL;
		else
			to_destroy->parent->rchild = NULL;
		free(to_destroy);
	}


	free(node);

	return tree;
}


size_t rbtree_flatten(rbtree *x, void **item_buffer, keyt_t *key_buffer)
{
	size_t count = 0;
	_rbtree_flatten(x, item_buffer, key_buffer, &count);
	return count;
}

void rbtree_flatprint(rbtree *x)
{
	if(x) {
		rbtree_flatprint(x->lchild);
		printf("%u ", x->key);
		rbtree_flatprint(x->rchild);
	}
}

int _rbtree_verify(rbtree *t, size_t cur_count, size_t *bcount) {
	if (!t) {
		if (*bcount) {
			return (cur_count+1 == *bcount);
		}
		else {
			*bcount = cur_count + 1;
			return 1;
		}
	}
	else {
		if (t->color == COLOR_RED) {
			if (t->parent && t->parent->color == COLOR_RED)
				return 0;
		}
		else
			cur_count++;
		return (_rbtree_verify(t->lchild, cur_count, bcount) ||
				_rbtree_verify(t->rchild, cur_count, bcount));
	}
}
int rbtree_verify(rbtree *t) {
	size_t bcount = 0;
	return _rbtree_verify(t, 0, &bcount);
}
