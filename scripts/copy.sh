#!/bin/bash
if [ "$#" == "1" ];then
    sudo cp $1/*.dfm ../deepface_live/build/linux/data/dfm_models/
else
    echo "Please give the path of the folder"

fi