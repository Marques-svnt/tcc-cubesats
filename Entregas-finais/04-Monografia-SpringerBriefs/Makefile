# Makefile for Springer Nature Monograph (SNmono.cls / svmono.cls)
# Monograph: Structural Optimization of a 1U CubeSat Chassis with Auxetic Metamaterials
# Author: Gabriel Marques de Andrade (UESC, 2026)

MAIN = main
PDF = $(MAIN).pdf
SRC = $(MAIN).tex references.bib $(wildcard frontmatter/*.tex) $(wildcard chapters/*.tex) $(wildcard appendices/*.tex)

.PHONY: all clean distclean view test

all: $(PDF)

$(PDF): $(SRC)
	pdflatex -interaction=nonstopmode $(MAIN).tex
	bibtex $(MAIN)
	makeindex $(MAIN).idx -s svind.ist
	pdflatex -interaction=nonstopmode $(MAIN).tex
	pdflatex -interaction=nonstopmode $(MAIN).tex

clean:
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.idx *.ind *.ilg *.lof *.lot *.fls *.fdb_latexmk DescriptionTexts.txt
	rm -f frontmatter/*.aux chapters/*.aux appendices/*.aux

distclean: clean
	rm -f $(PDF)
