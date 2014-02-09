#ifndef RECORD_H
#define RECORD_H

#include <stdio.h>
#include <asm/types.h>

struct time {
    __u32 sec;
    __u32 nanosec;
};

struct record {
    __u64 offset;
    __u32 len;
    __u32 marks;
    struct time A;
    struct time Q;
    struct time G;
    struct time I;
    struct time D;
    struct time M;
    struct time C;
    struct record *next;
};

enum {
    MARK_READ = 1<<0,
    MARK_WRITE = 1<<1,
    MARK_MERGE = 1<<2,
};

struct record *record_alloc(void);
void record_free(struct record *r);
struct record *find_by_offset(struct record *h, __u64 _offset);
void add_record(struct record **ph, struct record *r);
void rm_record(struct record **pr);

void fscan_time(FILE *fd, struct time *t);
int fscan_record(FILE *fd, struct record *r);
void fprint_time(FILE *fd, struct time t);
void fprint_record(FILE *fd, struct record *r);

#endif /* end of include guard: RECORD_H */
