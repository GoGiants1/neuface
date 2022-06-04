#!/usr/bin/env bash
source ~/anaconda3/etc/profile.d/conda.sh
conda activate dflab
cd ..
export DFL_PYTHON="python3"
export DFL_WORKSPACE="../workspace/"
export DFL_ROOT="../"
export DFL_SRC="../deepface_lab"

if [ ! -d "$DFL_WORKSPACE" ]; then
    mkdir "$DFL_WORKSPACE"
    mkdir "$DFL_WORKSPACE/data_src"
    mkdir "$DFL_WORKSPACE/data_src/aligned"
    mkdir "$DFL_WORKSPACE/data_src/aligned_debug"
    mkdir "$DFL_WORKSPACE/data_dst"
    mkdir "$DFL_WORKSPACE/data_dst/aligned"
    mkdir "$DFL_WORKSPACE/data_dst/aligned_debug"
    mkdir "$DFL_WORKSPACE/model"
fi
