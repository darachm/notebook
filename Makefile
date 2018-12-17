

.PHONY: all
all: 
	@echo all

.notes.yaml: notes.yaml
	python3 scripts/intake_notes.py
	touch .notes.yaml

