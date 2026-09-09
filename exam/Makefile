PYTHON ?= python3
CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Wpedantic

TARGET := luck_examine
SOURCE := luck_examine.cpp
DATA := exam_data.txt
PLOT := exam_plot.svg

.PHONY: all run python clean

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CXX) $(CXXFLAGS) $< -o $@

run: $(TARGET)
	./$(TARGET)

python:
	$(PYTHON) luck_examine.py

clean:
	$(RM) $(TARGET)
