# Documentation of NeuFace Lab Source Codes

## Directory Structure

```shell
neuface_lab
├── core
│   ├── cv2ex.py
│   ├── imagelib
│   │   ├── SegIEPolys.py
│   │   ├── blursharpen.py
│   │   ├── color_transfer.py
│   │   ├── common.py
│   │   ├── draw.py
│   │   ├── equalize_and_stack_square.py
│   │   ├── estimate_sharpness.py
│   │   ├── filters.py
│   │   ├── morph.py
│   │   ├── reduce_colors.py
│   │   ├── sd
│   │   ├── text.py
│   │   └── warp.py
│   ├── interact
│   │   └── interact.py
│   ├── joblib
│   │   ├── SubprocessGenerator.py
│   │   ├── SubprocessorBase.py
│   │   ├── ThisThreadGenerator.py
│   ├── leras
│   │   ├── archis
│   │   │   ├── DeepFakeArchi.py
│   │   ├── device.py
│   │   ├── initializers
│   │   ├── layers
│   │   ├── models
│   │   │   ├── ModelBase.py
│   │   │   ├── XSeg.py
│   │   ├── nn.py
│   │   ├── ops
│   │   └── optimizers
│   │       ├── AdaBelief.py
│   │       ├── ...
│   ├── mathlib
│   ├── mplib
│   ├── qtex
│   ├── osex.py
│   ├── pathex.py
│   ├── randomex.py
│   ├── stdex.py
│   └── structex.py
├── facelib
│   ├── FANExtractor.py
│   ├── FaceEnhancer.npy
│   ├── FaceEnhancer.py
│   ├── FaceType.py
│   ├── LandmarksProcessor.py
│   ├── S3FD.npy
│   ├── S3FDExtractor.py
│   ├── XSegNet.py
│   └── __init__.py
├── main.py
├── mainscripts
│   ├── ExportDFM.py
│   ├── Extractor.py
│   ├── FacesetEnhancer.py
│   ├── FacesetResizer.py
│   ├── Merger.py
│   ├── Sorter.py
│   ├── Trainer.py
│   ├── Util.py
│   ├── VideoEd.py
│   ├── XSegUtil.py
│   └── dev_misc.py
├── models
│   ├── ModelBase.py
│   ├── Model_SAEHD
│   │   ├── Model.py
│   │   └── __init__.py
│   ├── Model_XSeg
│   │   ├── Model.py
│   │   └── __init__.py
│   └── __init__.py
├── requirements-colab.txt
├── requirements-cuda.txt
└── samplelib

37 directories, 210 files
```

## Major Modules

`neuface_lab`를 root directory라고 가정하고 설명을 진행.

`core`, `facelib`, `mainscripts`, `models` 폴더에 핵심적인 로직이 저장되어 있다.

전체 오픈소스 기능 중 `XSegEditor`, `merger`는 사용되지 않았다.

### mainscripts

작성된 shell script 명령어가 [`main.py`](/deepface_lab/main.py)를 통해 parsing 후 진입하게 되는 기능별 entry point

- `ExportDFM`: 학습된 모델의 경로를 받아와 dfm 형식으로 export한다.
- `Extractor`: 이미지의 정보(얼굴의 위치, landmarks) 등을 계산하고, 얼굴을 detect하여 얼굴 부분만 crop 후 이미지로 저장한다. 이때 `S3FD`를 사용할 수 있다. [3](/train_scripts/3_extract_faces_from_src_images.sh), [4](/train_scripts/4_extract_faces_from_dst_images.sh)번 스크립트에서 얼굴 추출에 사용
- `FacesetEnhancer`: 얼굴 데이터셋을 정형화된 형식에 맞게 재가공하여 저장한다.
- `FacesetResizer`: 얼굴 데이터셋을 `Face-type`을 고려하여 크기를 변경하고, 마스킹도 이에 맞춰 저장한다.
- `Merger`: 학습된 모델을 읽어오고, 새로운 영상에 학습된 모델의 얼굴을 합성하는 모듈들을 실행한다. (**neufacelab**에서는 **이용하지 않음**) 1개 영상-> 1개 영상으로 대응되는 방식
- `Sorter`: 특정한 기준에 맞춰 이미지를 순서대로 나열한다. [3.1](/train_scripts/3.1_data_src_sort.sh), [4.1](/train_scripts/4.1_data_dst_sort.sh)에서 사용
- `Trainer`: 얼굴 모델을 학습시키는 과정을 모아 실행한다. [5](/train_scripts/5_train.sh)번 스크립트에서 사용
- `Util`: 파일로 저장되어 있는 각종 데이터(데이터셋 메타데이터, landmarks 등)를 처리한다. [3.3](/train_scripts/3.3_data_src_pack.sh), [3.4](/train_scripts/3.4_data_src_unpack.sh), [4.3](/train_scripts/4.3_data_dst_pack.sh)번 스크립트에서 사용
- `VideoEd`: 입력으로 주어지는 비디오를 편집할 수 있는 메소드를 제공한다. [1](/train_scripts/1_extract_image_from_src_video.sh), [2](/train_scripts/1_extract_image_from_dst_video.sh)
- `XSegUtil`: XSeg를 활용하여, 얼굴에서 머리카락 부분과 얼굴 부분을 분리하여 마스킹할 수 있는 메소드를 제공한다. [3.2](/train_scripts/3.2_Xseg_mask_apply_to_data_src.sh), [4.2](/train_scripts/4.2_Xseg_mask_apply_to_data_dst.sh)번 스크립트에서 사용한다.

### core module & library

- `imagelib`: 이미지 처리 관련 모듈

  - warp
  - morph
  - filter
  - draw
  - blur
  - color_transfer
    등 다양한 이미지 변환을 수행함.

- `interact`: command line 명령어 수행 중 사용자와의 interaction을 관리.(keyboard, mouse input, etc.)

- `joblib`: 학습에 사용할 user level process와 thread를 만들고, multi-processing, multi-threading을 가능하게 해주는 라이브러리

- `leras`: like lighter keras. lightweight neural network library written from scratch based on `pure tensorflow` without keras.([detail](/deepface_lab/core/leras/nn.py))

  - neufacelab에서 사용할 `neural-network`와 관련된 라이브러리
  - [`DeepFakeArchi.py`](/deepface_lab/core/leras/archis/DeepFakeArchi.py)에 학습에 사용되는 인코더, 디코더, Inter(AB, B)의 구조가 선언되어있다.
  - `leras/layers` 에는 convolution layer나 BatchNorm2D, Dense Layer 등 다양한 종류의 layer가 선언되어 있음.
  - [`leras/models`](/deepface_lab/core/leras/models/)에 `Xseg`(얼굴에 관한 마스킹을 진행하는 모델) 모델과, ModelBase 등이 구현되어 있다.
  - [`leras/optimizer`](/deepface_lab/core/leras/optimizers/AdaBelief.py)에는 이번 프로젝트를 진행하며 사용한 AdaBelief optimizer 구현되어 있다.
  - `device.py`는 학습할 때 사용할, 최적의 CPU나 GPU 디바이스를 찾고, 리소스 관리에 사용된다.
  - `nn.py`는 `neural-network` 클래스를 구현한 것이며, high-level에서 디바이스 정보를 저장하고, 뉴럴넷을 초기화한다.
  - 그외에 leras 폴더 내의 `\*ex.py`는 ex 앞의 단어 cv2, os, path, random, std, struct 등 leras에서 사용할 기능별 `helper function`이 저장되어 있다.

### facelib

- `FaceType.py`: `Whole Face`로 학습을 진행했으며 그 이외에 open source에서 정의한 Face-type 들이 선언되어 있다.
- `FANExtractor`: face-alignment를 찾아내고, [3번](/train_scripts/3_extract_faces_from_src_images.sh),[4번](/train_scripts/4_extract_faces_from_dst_images.sh) 스크립트에서 얼굴을 찾아서 정렬하여 새로운 이미지로 저장할 떄 사용.
- `LandmarksProcessor.py`: 얼굴의 랜드마크를 찾아주는 module
- `S3FDExtractor.py`: S3FD -> Single Shot Scale-invariant Face Detector라는 뜻으로 Face-detection을 수행하는 모듈이다. 작은 얼굴을 잘 찾아낸다.
- `XSegNet.py`: 학습시켜둔 XSeg model을 이용해서 이미지의 얼굴을 masking할 때 사용한다. [3.2](/train_scripts/3.2_Xseg_mask_apply_to_data_src.sh), [4.2](/train_scripts/4.2_Xseg_mask_apply_to_data_dst.sh)

### models

neuface_lab에서는 [SAEHD 모델](/deepface_lab/models/Model_SAEHD/Model.py)을 사용하여 학습을 진행했다.

앞서 설명한 부분들을 종합하여 이용하는 부분이다. 전체적인 학습 모델 객체를 생성하고, 초기화를 진행하고, 학습을 진행하는 메서드도 함께 구현되어 있다. 각종 하이퍼파라미터 설정 및 저장이 이루어진다.

## What we contribute

### main.py

DeepFace Lab을 실행하는 파이썬 main 파일이다. cli 인자로 넘겨주는 값에 따라 train, export, merge 등을 진행한다.
우리의 프로젝트에 맞춰, train 과정에서 자동으로 export를 할 수 있도록 `export-iter` 인자를 추가하였다.

```shell
bash 5_train.sh 1000
```

위와 같이 `5_train.sh`를 실행할 때 export 회차 주기를 넘기면 자동으로 `export-iter`로 들어가도록 하였다.

### Export DFM

```python
# deepface_lab/mainscripts/ExportDFM.py
def main(model_class_name, saved_models_path, silent_start=False, cpu_only=False):
    model = models.import_model(model_class_name)(
                        is_exporting=True,
                        saved_models_path=saved_models_path,
                        silent_start=silent_start,
                        cpu_only=cpu_only)
    model.export_dfm ()
```

dfm 모델을 추출하는 모듈이다. 원래는 `cpu_only`의 기본값이 True로 추출한 모델을 GPU 환경에서 사용할 수 없도록 제한되어 있었다. 이것을 해제하고, `silend_start` 인자를 추가하여 추가적인 메시지가 나오지 않게 설정할 수 있도록 하였다.

### Iteral Export

```py
# deepface_lab/models/ModelBase.py
def export_dfm_iter(self, rename=True):
    output_path = self.get_strpath_storage_for_file('model.dfm')
    iter_path = self.get_strpath_storage_for_file(f'model_{self.iter}.dfm')
    try:
        self.export_dfm()
        if rename: os.rename(output_path, iter_path)
        io.log_info(f"Export DFM iter: {self.iter} Success.\r\n")
    except e:
        io.log_info("Export DFM Failed.\r\n")
```

이는 주기적인 모델 추출이 가능하도록 하는 함수이다. 실제로 `export`를 수헹하는 것은 `export_dfm()`함수로 이 함수에서는 로그를 남기고, 추출 과정 중 발생할 수 있는 에러를 핸들링한다.

```python
# deepface_lab/mainscripts/Trainer.py
def trainerThread(""" arguments """):
    ...
    def model_exportDFM() :
        try: # SAEHD only
            model.export_dfm_iter()
        except:
            pass

    ...

    for i in itertools.count(0,1):

        ...
        if model.get_iter() == 1:
            model_save()
        elif not (model.get_iter() % export_iter):
            model_exportDFM()
        ...
```

이렇게 구현된 `export_dfm_iter()`는 `Trainer`에서 각 주기마다 호출된다. 그 결과 학습 결과가 저장되는 위치에 dfm 모델이 저장된다.  
한편, `op`에도 `export`를 등록하여, 명령어로 사용 가능하도록 추가하였다.

### Hyper-parameter Searching

다양한 가설을 바탕으로 학습을 진행하였다. 그 후 Morpheus 3D의 요구사항에 부합하는 모델 학습 파라미터를 찾았다.
| Parameter | Value | Parameter | Value |
|--------------------------|---------------|------------------------------|-----------------|
| Resolution | 224 | Face_type | Wf |
| Models_opt_on_gpu | True | Archi | Liae-udt |
| Ae_dims | 512 | E_dims | 64 |
| D_dims | 64 | D_mask_dims | 32 |
| Masked_training | True | Eyes_mouth_prio | True |
| Uniform_yaw | True | Blur_out_mask | True |
| Adabelief | True | Lr_dropout | Y |
| Random_warp | True | Random_hsv_power | 0.0 |
| True_face_power | 0.0 | Face_style_power | 0.0 |
| Bg_style_power | 0.0 | Ct_mode | None |
| Clipgrad | False | Pretrain | False |
| Autobackup_hour | 0 | Write_preview_history | True |
| Target_iter | 500000 | Random_src_flip | Alse |
| Random_dst_flip | True | Batch_size | 12 |
| Gan_power | 0.0 | Gan_patch_size | 28 |
| Gan_dims | 16 | | |

### Optimize Pre-processing workflow

쉘 스크립트 작성을 통해서 전처리 과정을 부담없이 진행할 수 있게 자동화하였으며, 자세한 [사용법](readme.md/#how-to-pre-processing)을 제공하였다.
