## Installation
```sh
poetry shell        #Run local environment
poetry install      # install project dependencies in local env?
pip install --editable .    # install project in local environemt so executable is generated
```

## Usage
```sh
accountant purchase
```

# Regression tests
1. Change dir to importers
`cd importers`
2. Run tests
`pytest` 
if files does not exists use 
`pytest --generate` instead
