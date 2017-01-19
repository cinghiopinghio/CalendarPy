YEAR=2017

run:
	python3 ./CalendarPy.py $(YEAR)


merge: $(YEAR)-??.pdf
	pdfjoin --a4paper --fitpaper false --landscape --outfile calendar-$(YEAR).pdf -- $(YEAR)-*.pdf 


clean:
	rm $(YEAR)*.pdf
