CC=gcc
CFLAGS=-c -Wall
LDFLAGS=-mwindows
SOURCES=backdoor.c
OBJECTS=$(SOURCES:.c=.o)
EXECUTABLE=backdoor.exe

all: $(SOURCES) $(EXECUTABLE)
    
$(EXECUTABLE): $(OBJECTS) 
    $(CC) $(LDFLAGS) $(OBJECTS) -o $@

.c.o:
    $(CC) $(CFLAGS) $< -o $@