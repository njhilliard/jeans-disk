CC       =  gcc
CCSTD    =  -std=c99
WFLAGS   = -Wall -Wextra -Wconversion -Wshadow
OPTIMIZE = -O3 -march=native -mfpmath=sse -DNDEBUG -fPIC

SRCS  = tipsy.c
OBJS := $(patsubst %.c, %.o, $(SRCS))
LIB   = libtipsy.so

.DEFAULT_GOAL = all

.PHONY = all
all: $(LIB)

$(LIB): $(OBJS)
	@ echo Building shared library '$@'...
	@ $(CC) -shared -Wl,-soname,$(LIB) -o $@ $^

%.o: %.c
	@ echo Compiling $<...
	@ $(CC) $(CCSTD) $(CFLAGS) $(OPTIMIZE) -c $< -o $@

.PHONY = clean
clean:
	@ echo Cleaning...
	@ rm -f $(OBJS)

.PHONY = dist-clean
dist-clean: clean
	@ rm -f $(LIB)