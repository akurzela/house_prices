Global system setup
-------------------
1. Install [pyenv](https://github.com/pyenv/pyenv)
2. Install [Python build dependencies](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
3. Install [Poetry](https://poetry.eustace.io/docs/)
4. Ensure virtual environments are created in project root directories
  ```
    poetry config --local virtualenvs.in-project true
  ```

Project setup
-------------
1. Install Python version specified in [.python-version](.python-version)
  ```
    pyenv install <version>
  ```
2. Download and install dependencies in local virtual environment
  ```
    poetry install
  ```
