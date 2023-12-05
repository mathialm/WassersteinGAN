#!/bin/sh

pip install .

python bin/build_tfrecord.py --data celeba -r 64 -c 108