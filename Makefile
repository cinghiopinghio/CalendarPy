YEAR:=$(shell grep year config.yaml | cut -d\  -f2)

.PHONY: run merge clean all

run:
	echo $(YEAR)
	python3 ./CalendarPy.py


merge: $(YEAR)-??.pdf
	pdfjoin --a4paper --fitpaper false --landscape --outfile calendar-$(YEAR).pdf -- $(YEAR)-*.pdf


clean:
	rm $(YEAR)*.pdf


all:	run merge clean
	@echo Get your calendar
