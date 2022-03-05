# \ var
MODULE  = $(notdir $(CURDIR))
OS      = $(shell uname -o|tr / _)
NOW     = $(shell date +%d%m%y)
REL     = $(shell git rev-parse --short=4 HEAD)
BRANCH  = $(shell git rev-parse --abbrev-ref HEAD)
PEPS    = --ignore=E265,E302,E401,E402,E702
# / var

# \ tool
CURL = curl -L -o
CF   = clang-format-11 -style=file -i
PY   = $(shell which python3)
PIP  = $(shell which pip3)
PEP  = $(shell which autopep8)
# / tool

# \ src
Y += $(MODULE).py
S += $(Y)
# / src

# \ all
all: $(PY) $(MODULE).py
	$^ $@ && $(MAKE) tmp/format_py
# / all

# \ format
tmp/format_py: $(Y)
	$(PEP) $(PEPS) -i $? && touch $@

doc:

doxy: doxy.gen
	rm -rf docs ; doxygen $< 1>/dev/null

# \ install

.PHONY: install update
install: $(OS)_install
	$(MAKE) update
update: $(OS)_update
	$(PIP) install --user -U    pip autopep8 pytest
	$(PIP) install --user -U -r requirements.txt

.PHONY: GNU_Linux_install GNU_Linux_update
GNU_Linux_install GNU_Linux_update:
	sudo apt update
	sudo apt install -u `cat apt.txt`

# \ merge
MERGE  = Makefile README.md .gitignore .clang-format doxy.gen $(S)
MERGE += apt.txt requirements.txt
MERGE += .vscode bin doc lib src tmp

dev:
	git push -v
	git checkout $@
	git pull -v
	git checkout shadow -- $(MERGE)
	$(MAKE) doxy ; git add -f docs

shadow:
	git push -v
	git checkout $@
	git pull -v
