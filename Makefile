source_files = trace_to_table.c record.c
objects = trace_to_table.o record.o

CFLAGS = -g -W -Wall

all: trace_to_table block_to_range

trace_to_table: ${objects}

block_to_range:

.PHONY:
clean:
	rm -v *.o *.d trace_to_table block_to_range

include $(subst .c,.d,$(source_files))

%.d: %.c
	$(CC) -M $(CPPFLAGS) $< > $@.$$$$; \
	sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' < $@.$$$$ > $@; \
	rm -f $@.$$$$

