CFLAGS = -g -W -Wall

all: block_to_range find_logic

block_to_range:
find_logic:

.PHONY:
clean:
	rm -v *.o *.d block_to_range

#include $(subst .c,.d,$(source_files))

#%.d: %.c
	#$(CC) -M $(CPPFLAGS) $< > $@.$$$$; \
	#sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' < $@.$$$$ > $@; \
	#rm -f $@.$$$$
