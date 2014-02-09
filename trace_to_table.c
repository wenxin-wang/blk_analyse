#include <stdio.h>
#include <stdlib.h>

#include "record.h"

int main()
{
    struct record r; 
    printf("%ld\n", sizeof(r));
    return 0;
}
