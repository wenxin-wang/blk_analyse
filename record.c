#include <stdio.h>
#include <stdlib.h>
#include "record.h"

struct record *record_alloc(void) {
    struct record *r;

    r=malloc(sizeof(*r));
    if(!r) {
        printf("Malloc for record failed!\n");
        exit(1);
    }
    return r;
}

void record_free(struct record *r) {
    free(r);
}

struct record *find_by_offset(struct record *h, __u64 _offset)
{
    while(h) {
        if(h->offset == _offset)
            return h;
        h=h->next;
    }
    return NULL;
}

void fscan_record(FILE *fd, struct record *r){
}

void fprint_time(FILE *fd, struct time t){
    fprintf(fd, "%5d.%-9d", t.sec, t.nanosec);
}

void fprint_record(FILE *fd, struct record *r){
    fprintf(fd, "%10d+%-4d\t", r->offset, r->len);
    fprint_time(fd, r->A);
    fprintf(fd, " ");
    fprint_time(fd, r->Q);
    fprintf(fd, " ");
    fprint_time(fd, r->G);
    fprintf(fd, " ");
    fprint_time(fd, r->I);
    fprintf(fd, " ");
    fprint_time(fd, r->D);
    fprintf(fd, " ");
    fprint_time(fd, r->M);
    fprintf(fd, " ");
    fprint_time(fd, r->C);
    fprintf(fd, "\n");
}
