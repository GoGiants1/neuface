# Neu-Face

## How to Pre-Processing

새로운 모델 학습을 시작할 때, `bash clear_workspace.sh`를 실행하면, workspace 폴더 초기화
초기화 이후 `workspace/model` 폴더에 `GenericXseg.zip`에 있는 파일들을 위치시켜야 masking 적용 가능.
숫자가 매겨진 순서대로 스크립트 실행

### Extract images from video

`workspace` 폴더에 `data_src.*` 로 비디오를 위치시키고 실행해야 함.
`workspace` 폴더에 `data_dst.*` 로 비디오를 위치시키고 실행해야 함.

- `1_extract_image_from_src_video`: 교체시킬(src) 얼굴이 있는 영상에서 `프레임별`로 `이미지 추출`

  - 입력: 영상(mp4, avi ,wmv 등 다양한 형식 지원(`workspace/data_src.*`)
  - 출력: 프레임별로 추출된 사진(fps 설정 가능)(`workspace/data_src/*.png`)
  - 프레임별로 사진이 추출되어 있는 경우 생략 가능

- `2_extract_image_from_dst_video`: 학습에 사용할 임의의 얼굴(random faces)들이 있는 영상을 `프레임별`로 `이미지 추출`
  - 입력: 영상(mp4, avi ,wmv 등 다양한 형식 지원(`workspace/data_dst.*`)
  - 출력: 프레임별로 추출된 사진(fps 설정 가능)(`workspace/data_dst/*.png`)
  - 프레임별로 사진이 추출되어 있는 경우 생략 가능
  - `assets` 폴더에 제공된 `random dst faceset`를 사용하면 이 과정 생략 가능

### Face detection, Masking, Selection

프레임 별로 추출한 사진에서 얼굴만을 추출하고, 마스킹을 적용한 다음, 수작업으로 데이터를 선별하는 작업.

- `3_extract_faces_from_src_images`: 프레임별로 추출된 사진에서 얼굴만 인식해서 추출한 다음 `workspace/data_src/alinged` 폴더에 저장

  - 입력: `workspace/data_src/*.png`에 저장된 사진(`1번` 스크립트 실행 결과물)
  - 출력: `workspace/data_src/aligned/*.png` 경로에 얼굴만 뽑아낸 사진들이 순서대로 저장

- `3.1_data_src_sort`: 5번 옵션으로 전체적인 얼굴 사진을 유사도 분포를 기준으로 정렬해 줌. 여기서 손으로 얼굴을 가리는 사진, 타겟 얼굴과 지나치게 다른 사진, 얼굴이 방향이 올바른 자세(정수리가 12시 방향, 목이 6시 방향)이 아닌 사진 등을 삭제해준다.(수동) 여러가지 정렬 옵션이 있으므로 다양하게 정렬해보고, 중복되는 얼굴, 흐린 얼굴들도 추가로 제거.

  - 입력: `3번` 스크립트 실행 결과물(`workspace/data_src/aligned/*.png`)
  - 출력: 새로운 기준에 맞게 정렬된 사진들(`workspace/data_src/aligned/*.png`)
  - 정렬 후 삭제의 기준
    ![img](https://i.imgur.com/UAtctbK.png)
    - 초록: 좋은 데이터
    - 빨강: 얼굴 정렬이 좋지 않음 -> 삭제
    - 파랑: 얼굴 위에 다른 장애물이 존재 -> 삭제
    - 노랑: blurry한 얼굴 -> 삭제 되어야하나, 다른 데이터에는 없는 얼굴 각도를 가진 경우 남길 수도 있음
    - 보라: 다른 사람의 얼굴 -> 삭제
    - 핑크: 잘려나간 얼굴 -> 삭제가 바람직
    - 주황: 너무 어둡운 or 밝은 or overexposed or 명암이 낮은 or 포토샵이 많이 되어 있어서 실제 얼굴과 많이 다른 경우 -> 삭제
  - 정렬 기준
    - [0] blur - sorts by image blurriness (determined by contrast), fairly slow sorting method and unfortunately not perfect at detecting and correctly sorting blurry faces.
    - [1] motion blur - sorts images by checking for motion blur, good for getting rid of faces with lots of motion blur, faster than [0] blur and might be used as an alternative but similarly to [0] not perfect.
    - [2] face yaw direction - sorts by yaw (from faces looking to left to looking right).
    - [3] face pitch direction - sorts by pitch (from faces looking up to looking down).
    - [4] face rect size in source image - sorts by size of the face on the original frame (from biggest to smallest faces). Much faster than blur.
    - [5] histogram similarity - sort by histogram similarity, dissimilar faces at the end, useful for removing drastically different looking faces, also groups them together.
    - [6] histogram dissimilarity - as above but dissimilar faces are on the beginning.
    - [7] brightness - sorts by overall image/face brightness.
    - [8] hue - sorts by hue.
    - [9] amount of black pixels - sorts by amount of completely black pixels (such as when face is cut off from frame and only partially visible).
    - [10] original filename - sorts by original filename (of the frames from which faces were extracted). without \_0/\_1 suffxes (assuming there is only 1 face per frame).
    - [11] one face in image - sorts faces in order of how many faces were in the original frame.
    - [12] absolute pixel difference - sorts by absolute difference in how image works, useful to remove drastically different looking faces.
    - [13] best faces - sorts by several factors including blur and removes duplicates/similar faces, has a target of how many faces we want to have after sorting, discard faces are moved to folder "aligned_trash".
      - **비추천** -> 성능이 나쁨
    - [14] best faces faster - similar to best faces but uses face rect size in source image instead blur to determine quality of faces, much faster than best faces.
      - **비추천**

- `3.2_Xseg_mask_apply_to_data_src`: 미리 학습된 Xseg 모델(`GenericXseg.zip`의 내용물)을 통해서 얼굴의 형태를 masking 해서 합성을 자연스럽게 해준다.

  - 실행 전 요구사항: `assets/GenericXseg.zip`의 압축을 풀어서 `workspace/model` 경로에 둔다.
  - 입력: `workspace/data_src/aligned/*.png`
  - 출력: `workspace/data_src/aligned/*.png`
  - GenericXseg 에 들어있는 학습된 모델이 없다면 성능이 낮음

- `3.3_data_src_pack`: 얼굴 사진들을 `.pak`이라는 형식으로 압축
  - 입력: `workspace/data_src/aligned/*.png`
  - 출력: `workspace/data_src/aligned/faceset.pak`
  - 학습을 진행할 때, data loading 을 빠르게 하고, 편하게 데이터를 이동시킬 수 있게 함.
- `3.4_data_src_unpack`: 압축한 `.pak`형식의 파일을 원래 이미지 파일들로 압축 해제
  - 입력: `workspace/data_src/aligned/faceset.pak`
  - 출력: `workspace/data_src/aligned/*.png`

`4~4.3`은 위와 매우 유사하므로 생략.

## How to Train Model

`pretrained_model.zip`의 압축을 푼 다음, `workspace/model` 폴더 내에 위치시켜야 한다.

`data_src/aligned/faceset.pak`, `data_dst/aligned/faceset.pak`이 위치해 있어야함.

`data_dst/aligned/faceset.pak`은 `random_dst_face_set.zip`에 있는 faceset 사용.(이미 전처리(`4 ~ 4.3` 과정) 완료된 6만장 가량의 얼굴 사진들)

`data_src/aligned`에는 `3.3번 스크립트`로 만든 faceset 사용

타겟 얼굴이 바뀔 때마다, pretrained 모델을 새로운 것으로 초기화해준다.(itration이 0인 것으로)

- `5_train`: 실시간으로 합성될 얼굴을 GAN으로 학습한다.
  - usage: `bash 5_train.sh {$target_backup_iteration}` -> `bash 5_train.sh 10000`
  - 학습 설정은 기존에 설정대로 진행하면 되지만 iteration 목표치를 따로 설정해주지 않는다면 무한히 학습을 진행하게 된다.
  - 입력: command line argument 1개(`target_backup_iteration`), 전처리가 완료된 faceset(`workspace/data_src/aligned/faceset.pak`, `workspace/data_dst/aligned/faceset.pak`)
  - 출력: `.dfm` 파일(neuface_live에 사용할 모델 파일), encoder, decoder, interAB, interB, src_dst_opt(`numpy.ndarray` 저장, `.npy`), data.dat, summary.txt(학습 진행 상황 요약, 파라미터 설정, 현재 iteration 등)

## etc.

- `clear_workspace.sh`: `workspace` 폴더 초기화

  - 파일들이 모두 삭제되고 다시 빈 폴더가 생성되므로 백업 필요

- `env.sh`: 환경변수 설정, 가상환경 활성화 및 초기 폴더 설정

- `exportDFM.sh`: 학습된 모델들을 수동으로 `.dfm` 파일로 변환하여 neuface_live에 사용
