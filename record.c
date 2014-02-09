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
