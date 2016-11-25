all: clean build test

clean:
	rm -rf dist/ coverage.xml

virtualenv:
	if [ ! -d venv ]; then \
		virtualenv venv; \
		venv/bin/pip install -r requirements.txt; \
		venv/bin/pip install 'nose>=1.3.0' 'coverage>=4'; \
	fi

test: virtualenv
	venv/bin/nosetests --with-coverage --cover-xml

build:
	./setup.py sdist

publish:
	./setup.py sdist upload -r pypi
