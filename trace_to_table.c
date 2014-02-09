#include <stdio.h>
#include <stdlib.h>

#include "record.h"

int main()
{
    struct record *head; 
    head=record_alloc();
    record_free(head);
    return 0;
}
