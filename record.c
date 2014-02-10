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

struct record *find_or_add_by_offset(struct record *h, __u64 _offset)
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

void cp_time(struct time *t, struct time *t1) {
    t->sec = t1->sec;
    t->nanosec = t1->nanosec;
}

int set_field(struct record *r, char field, struct time *t) {
    switch (field) {
        case 'A':
            cp_time(&r->A, t);
            return 0;
        case 'Q':
            cp_time(&r->Q, t);
            return 0;
        case 'G':
            cp_time(&r->G, t);
            return 0;
        case 'I':
            cp_time(&r->I, t);
            return 0;
        case 'D':
            cp_time(&r->D, t);
            return 0;
        case 'M':
            cp_time(&r->M, t);
            return 1;
        case 'C':
            cp_time(&r->C, t);
            return 1;
        default:
            return -1;
    }
}

/* I/O functions */

void fscan_time(FILE *fd, struct time *t) {
    fscanf(fd, "%u.%u", &t->sec, &t->nanosec);
}

int fscan_add_record(FILE *fd, struct record **ph) {
    char c[4];
    __u64 _offset;
    __u32 _len;
    int i, ret;
    struct time t;
    struct record *r;

    fscanf(fd, "%Lu + %u", &_offset, &_len);
    r=*ph;
    while(r) {
        if(r->offset == _offset)
            break;
        r=r->next;
    }

    if(!r) {
        r=record_alloc();
        r->offset = _offset;
        r->len = _len;
        add_record(ph, r);
    }
    else if(r->len < _len) { /* merged! */
        /* Don't know what to do... */
    }

    fscanf(fd, "%s", c);
    fscan_time(fd, &t);
    for(i=0; c[i]!='\0' && i<4; i++) {
        ret=set_field(r, c[i], &t);
        if(ret != -1) break;
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
