#include "gpsr_lib.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#define PI 3.1416

void gpsr_diff_2d (coordinate_t *result, coordinate_t *origin, coordinate_t* dest)
{
    result[0] = dest[0] - origin[0];
    result[1] = dest[1] - origin[1];
    return;
}

void gpsr_diff_3d (coordinate_t *result, coordinate_t *origin, coordinate_t* dest)
{
    result[0] = dest[0] - origin[0];
    result[1] = dest[1] - origin[1];
    result[2] = dest[2] - origin[2];
    return;
}

distance_t gpsr_dist_2d (coordinate_t *p1, coordinate_t *p2)
{
    distance_t result = 0;
    if (p1[0]>p2[0]) {
        result += (distance_t) (p1[0]-p2[0]) * (distance_t) (p1[0]-p2[0]);
    }
    else {
        result += (distance_t) (p2[0]-p1[0]) * (distance_t) (p2[0]-p1[0]);
    }

    if (p1[1]>p2[1]) {
        result += (distance_t) (p1[1]-p2[1]) * (distance_t) (p1[1]-p2[1]);
    }
    else {
        result += (distance_t) (p2[1]-p1[1]) * (distance_t) (p2[1]-p1[1]);
    }

    return result;
}

distance_t gpsr_dist_3d (coordinate_t *p1, coordinate_t *p2)
{
    distance_t result = 0;

    if (p1[0]>p2[0]) {
        result += (distance_t) (p1[0]-p2[0]) * (distance_t) (p1[0]-p2[0]);
    }
    else {
        result += (distance_t) (p2[0]-p1[0]) * (distance_t) (p2[0]-p1[0]);
    }

    if (p1[1]>p2[1]) {
        result += (distance_t) (p1[1]-p2[1]) * (distance_t) (p1[1]-p2[1]);
    }
    else {
        result += (distance_t) (p2[1]-p1[1]) * (distance_t) (p2[1]-p1[1]);
    }

    if (p1[2]>p2[2]) {
        result += (distance_t) (p1[2]-p2[2]) * (distance_t) (p1[2]-p2[2]);
    }
    else {
        result += (distance_t) (p2[2]-p1[2]) * (distance_t) (p2[2]-p1[2]);
    }

    return result;
}

/*
 * Get argument of point p
 */
distance_t gpsr_argument (coordinate_t *p)
{
    return (distance_t) (atan2((double) p[1], (double) p[0]));
}

/*
 * Get argument of vector (p2-p1)
 */
distance_t gpsr_vect_argument (coordinate_t *p1, coordinate_t *p2)
{
    coordinate_t diff[2];
    gpsr_diff_2d (&(diff[0]), p1, p2);
    return gpsr_argument(&diff[0]);
}

/*
 * Angle of (p4-p3,p2-p1)
 */
distance_t gpsr_vect_angle (coordinate_t *p1, coordinate_t *p2, coordinate_t *p3, coordinate_t* p4)
{
    return gpsr_vect_argument(p3,p4) - gpsr_vect_argument(p1,p2);	
}

int gpsr_change_face (coordinate_t *origin, coordinate_t *end,
        coordinate_t *curr_pos, coordinate_t *next_hop)
{
    coordinate_t s1[2], s2[2];
    int32_t determinant;
    float s,t;

    gpsr_diff_2d(&s1[0], origin, end);
    gpsr_diff_2d(&s2[0], curr_pos, next_hop);

    //TODO/mengueha/potential integer overflow here. We might want to use a uin64_t but that's expensive...
    determinant = s1[0] * s2[1] - s1[1] * s2[0];

    if (determinant == 0) { //Vectors are colinear
        //TODO check whether we are on the original segment
        return 0;
    }

    s = (float) (s1[0] * (origin[1] - curr_pos[1]) - s1[1] * (origin[0] - curr_pos[0])) / (float) determinant;
    t = (float) (s2[0] * (origin[1] - curr_pos[1]) - s2[1] * (origin[0] - curr_pos[0])) / (float) determinant;

    return (s >= 0 && s<=1 && t>=0 && t<=1);
}

char* gpsr_greedy_fwd_2d (char *nbr_struct, size_t dist, int nb_of_neigh, coordinate_t *curr_pos, coordinate_t* dest)
{
    distance_t curr_min_dist = gpsr_dist_2d (curr_pos, dest), curr_dist;
    char *curr_min_pos = NULL, *curr_nbr = nbr_struct;
    int i;

    for (i=0; i<nb_of_neigh; i++) {
        curr_dist = gpsr_dist_2d ((coordinate_t *) curr_nbr, dest);
        if (curr_dist < curr_min_dist) {
            curr_min_pos = curr_nbr;
            curr_min_dist = curr_dist;
        }
        curr_nbr += dist;
    }

    return curr_min_pos;
}

char* gpsr_perimeter_fwd_2d (char* nbr_superstruct, size_t dist, int nb_of_neigh,
        coordinate_t *curr_pos, coordinate_t *dest, coordinate_t *perimeter_entry)
{
    distance_t curr_angle, min_angle=PI;
    char *min_pos = NULL, *curr_nbr = nbr_superstruct;
    int i;

    for(i=0; i<nb_of_neigh; i++) {
        curr_angle = gpsr_vect_angle (perimeter_entry, dest,
                curr_pos, (coordinate_t *) curr_nbr); //TODO check order
        if (curr_angle > 0 && curr_angle < min_angle) {
            min_pos = curr_nbr;
            min_angle = curr_angle;
        }
        curr_nbr += dist;
    }

    return min_pos;
}

int gpsr_rr_graph (char* nbr_superstruct, size_t dist, int nb_of_neigh, coordinate_t* curr_pos, char** new_neigh)
{
    int i,j,new_nb_of_neigh=0;
    distance_t d1,d2,d3;
    coordinate_t *n1, *n2;

    for (i=0; i<nb_of_neigh; i++) {
        n1 = (coordinate_t *) (nbr_superstruct + dist*i);
        d1 = gpsr_dist_2d (curr_pos, n1);
        for (j=0; j<nb_of_neigh; j++) {
            if (j==i) continue;
            n2 = (coordinate_t *) (nbr_superstruct + dist*j);
            d2 = gpsr_dist_2d (curr_pos,n2);
            d3 = gpsr_dist_2d (n1,n2);
            if (d1 < ((d2 < d3) ? d3 : d2)) { /* There's a conflicting neighbor -> we remove the link */
                break;
            }
            if (j==nb_of_neigh-1) //Then we keep the link
                new_neigh[new_nb_of_neigh++] = nbr_superstruct + dist*i;
        }
    }

    return new_nb_of_neigh;
}

char* gpsr_fwd (char* nbr_superstruct, size_t dist, int nb_of_neigh,
        coordinate_t *curr_pos, coordinate_t *dest, coordinate_t *face_orig, uint8_t *mode)
{
    char *result = NULL;
    char *new_neigh[nb_of_neigh];

    switch (*mode) {
        case MODE_GREEDY:
            goto greedy;
        case MODE_PERIMETER:
            if (gpsr_dist_2d(curr_pos, dest) < gpsr_dist_2d(face_orig, dest)) {
                *mode = MODE_GREEDY;
                goto greedy;
            }
            goto perimeter;
        default:
            printf("iot_geo_lib: unknown mode %u\n", *mode);
            goto done;
    }
greedy:
    result = gpsr_greedy_fwd_2d (nbr_superstruct, dist, nb_of_neigh, curr_pos, dest);
    if (result) { /* We have a closer neighbor, thus we are done */
        goto done;
    }
    *mode = MODE_PERIMETER;
    memcpy(face_orig, curr_pos, sizeof(coordinate_t)*2);
perimeter: ;
           int new_nb_of_neigh = gpsr_rr_graph (nbr_superstruct, dist, nb_of_neigh, curr_pos, &new_neigh[0]);
           result = gpsr_perimeter_fwd_2d ((char*) new_neigh, dist, new_nb_of_neigh, curr_pos,
                   dest, face_orig);
done:
           return result;
}
