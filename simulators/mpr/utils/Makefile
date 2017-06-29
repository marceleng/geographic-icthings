OBJS = $(BUILDIR)/graph.o $(BUILDIR)/matrice.o $(BUILDIR)/rbtree.o $(BUILDIR)/llist.o

all: $(OBJS)
	$(AR) rsv $(BUILDIR)/datastructs.a $(OBJS) 

$(BUILDIR)/%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

