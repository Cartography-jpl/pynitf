# Simple makefile, just for convenience.

PYTHON = python
PYTEST = pytest
SPHINXBUILD = sphinx-build
SPHINXOPTS =

install:
	$(PYTHON) -m pip install . --no-deps --ignore-installed --no-cache-dir --no-index -vvv

check:
	export PYTHONPATH=$(shell pwd) && $(PYTEST) -rxXs tests

# Put it first so that "make" without argument is like "make help".
doc-help:
	@$(SPHINXBUILD) -M help doc doc/_build $(SPHINXOPTS)

doc-html: 
	@$(SPHINXBUILD) -M html doc doc/_build $(SPHINXOPTS)

doc-latex: 
	@$(SPHINXBUILD) -M latex doc doc/_build $(SPHINXOPTS)

doc-latexpdf: 
	@$(SPHINXBUILD) -M latexpdf doc doc/_build $(SPHINXOPTS)

#=================================================================
# Upload documentation to github pages
# *Note* I tend to forget this, but there needs to be a .nojekyll in
# the github pages for github to serve the page right. This can be done
# by just adding .nojekyll to doc/_build/html. This has already been done
# for this repository
github-pages: doc-html
	@echo "Note, this should usually be done from the main branch only"
	ghp-import doc/_build/html -m "Update pynitf documentation"
	@echo "You now need to push the gh-pages branch to github for these to be visible (git push origin gh-pages)"

