# My Package Manager

このリポジトリは『エムスリーテックブック5』における『自作Python Package Manager入門』を実行するためのリポジトリである。

## Installation

```sh
poetry install
poetry build
pip install dist/*.whl
```

## Run mypa

```sh
cd example_package

# make mypa.lock
mypa lock

# make `.mypaenv` and install requires packages
mypa install

# run mypaenv python
mypa run python src/main.py

# build example_package
mypa build

# install example_package
pip install dist/*.whl

# run example_package
python -c "from example_package.main import get; get()"
```
