#include <stdio.h>
#include <stdlib.h>

#include "record.h"

int main()
{
    struct record *head;
    struct record *p;
    char c;

    head=NULL;
    while(fscan_add_record(stdin, &head) != -2) {
        while((c=fgetc(stdin)) != '\n' && c != EOF) ;
    }

    p=head;
    fprintf(stdout, "Offset and Length   A               Q               G               I               D               M               C\n");
    while(p) {
        fprint_record(stdout, p);
        p=p->next;
    }
    while(head) {
        rm_record(&head);
    }
    return 0;
}
