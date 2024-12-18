.PHONY: all run install clean

all: install run  

run:
	$(PYTHON_BIN) $(MAIN_FILE)

install:
	python3 -m venv $(VENV_DIR)
	$(PIP_BIN) install --upgrade pip
	$(PIP_BIN) install -r $(REQUIREMENTS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf $(VENV_DIR)
