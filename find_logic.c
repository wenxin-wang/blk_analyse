#include <stdio.h>
#include <stdlib.h>
#include <asm/types.h>
#include <unistd.h>

/* i: input file
 * o: output file
 * b: block size
 * O: global offset
 */
#define S_OPTS  "i:o:b:O:L:"

void usage(void)
{
    fprintf(stderr, "block_to_range [option]\n");
    fprintf(stderr, "i: input file (Default: stdin)\n");
    fprintf(stderr, "o: output file (Default: stdout)\n");
    fprintf(stderr, "b: block size (Default: 4096)\n");
    fprintf(stderr, "O: global offset (Default: 0)\n");
    fprintf(stderr, "L: Logical block\n");
}

int main(int argc, char **argv)
{
    __u64 current;
    int bs, offset, logic;
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
            case 'L':
                logic = atoi(optarg);
                if(logic < 0) {
                    fprintf(stderr, "Logic %d : must not <0.\n", logic);
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
    logic /= bs;
    int i = 0;
    while(fscanf(input, "%Lu", &current) == 1) {
        if (i == logic) {
            fprintf(output, "%Lu\n", current*bs+offset);
            break;
        }
        i++;
    }
    return 0;
}
