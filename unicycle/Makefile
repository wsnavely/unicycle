PYLINTFLAGS = -rn --rcfile pylintrc
PYTHONFILES = uc.py command.py solvers.py

pylint: ; @for py in ${PYTHONFILES}; do echo "Linting $$py"; pylint ${PYLINTFLAGS} $$py; done
