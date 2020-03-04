# Simple makefile, just for convenience.

PYTHON = python
PYTEST = pytest
SPHINXBUILD = sphinx-build
SPHINXOPTS =
PYTEST_OPTS = -n auto

install:
	$(PYTHON) -m pip install . --no-deps --ignore-installed --no-cache-dir --no-index -vvv

# install to "develop" mode. This sets up a link to the source code, so we
# can modify the source and immediately see the results in using pynitf
install-develop:
	$(PYTHON) setup.py develop

# variation that installs the source into $AFIDSPYTHONTOP, since this
# is something we commonly do during development.
install-develop-afids:
	$(PYTHON) setup.py develop --prefix $(AFIDSPYTHONTOP)

check:
	export PYTHONPATH=$(shell pwd) && $(PYTEST) $(PYTEST_OPTS) -rxXs tests

# Put it first so that "make" without argument is like "make help".
doc-help:
	@export PYTHONPATH=$(shell pwd) && $(SPHINXBUILD) -M help doc doc/_build $(SPHINXOPTS)

doc-html: 
	@export PYTHONPATH=$(shell pwd) && $(SPHINXBUILD) -M html doc doc/_build $(SPHINXOPTS)

doc-latex: 
	@export PYTHONPATH=$(shell pwd) && $(SPHINXBUILD) -M latex doc doc/_build $(SPHINXOPTS)

doc-latexpdf: 
	@export PYTHONPATH=$(shell pwd) && $(SPHINXBUILD) -M latexpdf doc doc/_build $(SPHINXOPTS)

#=================================================================
# Upload documentation to github pages
# *Note* I tend to forget this, but there needs to be a .nojekyll in
# the github pages for github to serve the page right. This can be done
# by just adding .nojekyll to doc/_build/html. This has already been done
# for this repository. Newer versions of ghp-import also have a "-n" option
# to add the .nojekyll file
github-pages: doc-html
	@echo "Note, this should usually be done from the main branch only"
	ghp-import -n doc/_build/html -m "Update pynitf documentation"
	@echo "You now need to push the gh-pages branch to github for these to be visible (git push origin gh-pages)"

