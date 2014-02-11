#include <stdio.h>
#include <stdlib.h>

#include "record.h"

int main()
{
    struct record *head, *p;
    int ret;
    char c;

    head=NULL;
    fprintf(stdout, "Offset and Length   A               Q               G               I               D               M               C\n");
    while((ret=handle_record(stdin, &head)) != -2) {
        while((c=fgetc(stdin)) != '\n' && c != EOF) ;
    }

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
