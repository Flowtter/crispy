VENV = crispy
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

run: $(VENV)/bin/activate
	$(PYTHON) src/main.py


$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt


clean:
	rm -rf __pycache__
	rm -rf $(VENV)

.PHONY: run clean
