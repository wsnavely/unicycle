PYLINTFLAGS = -rn --rcfile pylintrc
PYTHONFILES = unicycle.py command.py

pylint: ; @for py in ${PYTHONFILES}; do echo "Linting $$py"; pylint ${PYLINTFLAGS} $$py; done
