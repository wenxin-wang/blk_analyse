CFLAGS = -g -W -Wall

all: block_to_range

block_to_range:

.PHONY:
clean:
	rm -v *.o *.d block_to_range

#include $(subst .c,.d,$(source_files))

#%.d: %.c
	#$(CC) -M $(CPPFLAGS) $< > $@.$$$$; \
	#sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' < $@.$$$$ > $@; \
	#rm -f $@.$$$$
