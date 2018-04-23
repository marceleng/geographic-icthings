#ifndef __GPSR_LIB_H__
#define __GPSR_LIB_H__

#include <stdint.h>
#include <stdlib.h>
#include <stddef.h>

typedef uint32_t coordinate_t;
#define COORD_MAX UINT32_MAX
typedef double distance_t;

#define MODE_GREEDY 0
#define MODE_PERIMETER 1

/*
 * Loads of macros to access coordinates from a super structure
 * * Mainly, we assume that there is a `struct neighbor` that has a `coor_member` member of type coordinate_t[]
 * Superstruct is a struct neighbor[]
 * Thus all corresponding functions have the following arguments first:
 * (char* superstruct, size_t sizeof_superstruct, ...)
 */

/*
 * Macros to retranslate result as coordinate pointers to the superstructure
 */
#define GPSR_RESTORE(superstruct, coord_member, result) result -= offsetof(typeof(superstruct[0]),coord_member)
//#define GPSR_RESTORE (superstruct, coord_member, result) result -= ((char*) &(superstruct[0].coord_member) - (char*) &superstruct[0])
#define GPSR_RESTORE_ALL(superstruct, coord_member, results, nb_results) \
	for (int i=0; i<nb_results; i++) GPSR_RESTORE(superstruct, coord_member, results[i])


/*
 * Macro to use for all function calls that require to send the whole neighborhood
 * It allows to access the coordinates of the neighbors from a superstructure without any copy
 */
#define GPSR_CALL(func, superstruct, coord_member, ...) \
	func((char*) &((superstruct[0])->coord_member), sizeof(superstruct[0]), __VA_ARGS__)

/*
 * Finds the closest neighbour to dest and returns a pointer to its coordinates
 * Returns null if we are at a local maximum
 */
char* gpsr_greedy_fwd_2d (char* nbr_superstruct, size_t dist, int nb_of_neigh,
		coordinate_t *curr_pos, coordinate_t *dest);

/*
 * Finds next neighbour in perimeter mode and returns a pointer to its coordinates
 * TODO: add flag to chose between left- and right-hand rule
 */
char* gpsr_perimeter_fwd_2d (char* nbr_superstruct, size_t dist, int nb_of_neigh,
		coordinate_t *curr_pos, coordinate_t *dest, coordinate_t *perimeter_entry);

/*
 * Stores the planarized neighborhood in buffer new_neigh
 * Returns number of neighbors in relative neighborhood graph
 */
int gpsr_rr_graph (char* nbr_superstruct, size_t dist, int nb_of_neigh,
		coordinate_t* curr_pos, char** new_neigh);

char* gpsr_fwd (char* nbr_superstruct, size_t dist, int nb_of_neigh,
		coordinate_t *curr_pos, coordinate_t *dest, coordinate_t* face_orig, uint8_t *mode);
#endif
