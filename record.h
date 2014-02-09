#ifndef RECORD_H
#define RECORD_H

#include <asm/types.h>

struct time {
    __u32 sec;
    __u32 nanosec;
};

struct record {
    __u64 offset;
    __u32 len;
    __u32 marks; /* mark if this is merged */
    struct time Q;
    struct time G;
    struct time I;
    struct time D;
    struct time M;
    struct time C;
    struct record *next;
};

#endif /* end of include guard: RECORD_H */
