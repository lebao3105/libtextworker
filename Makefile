# Used for maintaining tasks.
# Copyright (C) 2024 Le Bao Nguyen and contributors.

# Programs to use
GT = xgettext
MSF = msgfmt
MSM = msgmerge

# Project infomations
COPYRIGHT = "(C) 2024 Le Bao Nguyen and contributors."
PKGVER = "0.1.4b1" # Change this corresponding to the app version
LOCALES = vi # Language codes, separated using spaces
POFILES = # Make later

# Targets
.PHONY: maketrans makepot genmo $(LOCALES) clean install build

## Generate translations
maketrans: makepot genmo

makepot:
	echo "[Translations] Making template..."
	$(GT) --copyright-holder=$(COPYRIGHT) --package-version=$(PKGVER) \
		--language=python -f po/POTFILES -d libtextworker -o po/libtextworker.pot

genmo: $(LOCALES)
$(LOCALES):
	echo "[Translations] Making po for $@..."
	$(MSM) po/$@.po po/textworker.pot -o po/$@.po

	echo "[Translations] Compiling po for $@..."

	if [ ! -d po/$@ ]; then \
		mkdir po/$@; \
	fi

	if [ ! -d po/$@/LC_MESSAGE ]; then \
		mkdir po/$@/LC_MESSAGE; \
	fi
	$(MSF) po/$@.po -o po/$@/LC_MESSAGE/$@.mo

install: maketrans
	$(pip) install .

build: maketrans
	$(pip) install build
	$(python3) -m build .

clean: $(wildcard po/*/LC_MESSAGES)
	rm -rf $?