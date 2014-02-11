#include <stdio.h>
#include <stdlib.h>
#include <asm/types.h>
#include <unistd.h>

/* i: input file
 * o: output file
 * b: block size
 * O: global offset
 */
#define S_OPTS  "i:o:b:O:"

void usage(void)
{
    fprintf(stderr, "block_to_range [option]\n");
    fprintf(stderr, "i: input file (Default: stdin)\n");
    fprintf(stderr, "o: output file (Default: stdout)\n");
    fprintf(stderr, "b: block size (Default: 4096)\n");
    fprintf(stderr, "O: global offset (Default: 0)\n");
}

int main(int argc, char **argv)
{
    __u64 start, current, last;
    int bs, offset;
    FILE *input, *output;
    int opt;

    /* Default Values */
    input = stdin;
    output = stdout;
    bs = 4096;
    offset = 0;

	while ((opt = getopt(argc, argv, S_OPTS)) != -1) {
        switch(opt) {
            case 'i':
                input = fopen(optarg, "r");
                if(!input) {
                    perror(optarg);
                    exit(1);
                }
                break;
            case 'o':
                output = fopen(optarg, "w");
                if(!output) {
                    perror(optarg);
                    exit(1);
                }
                break;
            case 'b':
                bs = atoi(optarg);
                if(bs <= 0) {
                    fprintf(stderr, "Block size %d : must be a positive integer.\n", bs);
                    exit(1);
                }
                break;
            case 'O':
                offset = atoi(optarg);
                if(offset <= 0) {
                    fprintf(stderr, "Offset %d : must be a positive integer.\n", offset);
                    exit(1);
                }
                break;
            default:
                usage();
                exit(1);
        }
    }

    bs /= 512;
    if(fscanf(input, "%Lu", &current) != 1) { fprintf(stderr, "No input!\n"); exit(1); }
    start = last = current;
    while(fscanf(input, "%Lu", &current) == 1) {
        if( current != last + 1 ) {
            fprintf(output, "%Lu - %Lu\n", offset + start*bs, offset + last*bs);
            start = current;
        }
        last = current;
    }
    if(start != current) {
        fprintf(output, "%Lu - %Lu\n", offset + start*bs, offset + last*bs);
    }
    return 0;
}
