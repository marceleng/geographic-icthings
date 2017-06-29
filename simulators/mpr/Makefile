export CC = gcc
export CFLAGS = -Wall -std=gnu99 -g
export LFLAGS = -std=gnu99
LIBS = $(BUILDIR)/datastructs.a -lm

export BUILDIR = $(shell pwd)/build
.PHONY: utils

OBJS = $(BUILDIR)/mpr.o $(BUILDIR)/main.o

all: create_dir utils $(OBJS)
	$(CC) $(LFLAGS) $(OBJS) -o mpr_flood_sim $(LIBS)

$(BUILDIR)/%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

create_dir:
	mkdir -pm 777 $(BUILDIR)

utils:
	$(MAKE) -C utils

clean:
	rm -fr $(BUILDIR)

dist-clean: clean
	rm -f mpr_flood_sim
