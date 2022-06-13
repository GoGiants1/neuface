#!/bin/bash

if [ "$1" == "--backup" ]; then
	cp -r ../workspace/model ../workspace/model_backup
fi

if [ "$#" == "2" ] && [ "$1" == "--path" ]; then
	python main.py exportdfm --model-dir "$2" --model SAEHD 
else
	python main.py exportdfm --model-dir ../workspace/model --model SAEHD
fi
exit
