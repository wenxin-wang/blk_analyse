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
    r->offset=0;
    r->len=0;
    r->marks=0;
    r->A.sec=0;
    r->A.nanosec=0;
    r->Q.sec=0;
    r->Q.nanosec=0;
    r->G.sec=0;
    r->G.nanosec=0;
    r->I.sec=0;
    r->I.nanosec=0;
    r->D.sec=0;
    r->D.nanosec=0;
    r->M.sec=0;
    r->M.nanosec=0;
    r->C.sec=0;
    r->C.nanosec=0;
    r->next=NULL;
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

void add_record(struct record **ph, struct record *r) {
    r->next=(*ph);
    *ph=r;
}

void rm_record(struct record **pr) {
    struct record *r;
    r=*pr;
    if(r) {
        *pr=r->next;
        record_free(r);
    }
}

/* I/O functions */

void fscan_time(FILE *fd, struct time *t) {
    fscanf(fd, "%u.%u", &t->sec, &t->nanosec);
}

int fscan_record(FILE *fd, struct record *r) {
    char c[4];
    int i, ret;
    fscanf(fd, "%s", c);
    ret=0;
    for(i=0; c[i]!='\0' && i<4; i++) {
        switch (c[i]) {
            case 'A':
                fscan_time(fd, &r->A);
                i=5; /* Dirty hack */
                break;
            case 'Q':
                fscan_time(fd, &r->Q);
                i=5; /* Dirty hack */
                break;
            case 'G':
                fscan_time(fd, &r->G);
                i=5; /* Dirty hack */
                break;
            case 'I':
                fscan_time(fd, &r->I);
                i=5; /* Dirty hack */
                break;
            case 'D':
                fscan_time(fd, &r->D);
                i=5; /* Dirty hack */
                break;
            case 'M':
                fscan_time(fd, &r->M);
                i=5; /* Dirty hack */
                ret=1;
                break;
            case 'C':
                fscan_time(fd, &r->C);
                i=5; /* Dirty hack */
                ret=1;
                break;
            default:
                ret=-1;
                break;
        }
    }

    if(ret==-1) {
        fprintf(stderr, "Unknown Action %s.\n", c);
    }

    fscanf(fd, "%s", c);
    switch (c[0]) {
        case 'W':
            r->marks |= MARK_WRITE;
            break;
        case 'R':
            r->marks |= MARK_READ;
            break;
        default:
            fprintf(stderr, "Unknown RWBS %s.\n", c);
            break;
    }
    fscanf(fd, "%Lu + %u", &r->offset, &r->len);

    return ret;
}

void fprint_time(FILE *fd, struct time t){
    fprintf(fd, "%5u.%-9u", t.sec, t.nanosec);
}

void fprint_record(FILE *fd, struct record *r){
    fprintf(fd, "%10Lu+%-4u ", r->offset, r->len);
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
