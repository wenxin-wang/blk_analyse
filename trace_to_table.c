#include <stdio.h>
#include <stdlib.h>

#include "record.h"

int main()
{
    struct record *head;
    struct record *p;
    char c;

    head=NULL;
    fscan_add_record(stdin, &head);
    while(c=fgetc(stdin) != '\n' && c != EOF) ;
    fscan_add_record(stdin, &head);

    p=head;
    while(p) {
        fprint_record(stdout, p);
        p=p->next;
    }
    while(head) {
        rm_record(&head);
    }
    return 0;
}
