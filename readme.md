# Neu-Face

## Pre-Processing

새로운 모델 학습을 시작할 때, `bash clear_workspace.sh`를 실행하면, workspace 폴더 초기화
초기화 이후 `workspace/model` 폴더에 `GenericXseg.zip`에 있는 파일들을 위치시켜야 masking 적용 가능.
숫자가 매겨진 순서대로 스크립트 실행

### `1 ~ 2 scripts`

`workspace` 폴더에 `data_src.*` 로 비디오를 위치시키고 실행해야 함.
`workspace` 폴더에 `data_dst.*` 로 비디오를 위치시키고 실행해야 함.

### `3 ~ 3.3`

프레임 별로 추출한 사진에서 얼굴만을 추출하고, 마스킹을 적용한 다음, 수작업으로 데이터를 선별하는 작업.

- `3`: 프레임별로 추출된 사진에서 얼굴만 인식해서 추출한 다음 `workspace/data_src/alinged` 폴더에 저장.
- `3.1`: 5번 옵션으로 전체적인 얼굴 사진을 유사도 분포를 기준으로 정렬해 줌. 여기서 손으로 얼굴을 가리는 사진, 타겟 얼굴과 지나치게 다른 사진, 얼굴이 방향이 올바른 자세(정수리가 12시 방향, 목이 6시 방향)이 아닌 사진 등을 삭제해준다.(수동) 여러가지 정렬 옵션이 있으므로 다양하게 정렬해보고, 중복되는 얼굴, 흐린 얼굴들도 추가로 제거.

- `3.2`: 기 학습된 Xseg 모델을 통해서 얼굴의 형태를 masking 해서 합성을 자연스럽게 해준다.
- `3.3`: 학습을 진행할 때, data loading 을 빠르게 하고, 편하게 데이터를 이동시킬 수 있게 함.
- `4~4.3`은 위와 동일하므로 생략.

### `5_train.sh`

`pretrained model`을 model 폴더 내에 위치시켜야 하고, `data_src/aligned`, `data_dst/aligned`에 packing 된 faceset.pak이 존재해야 함.

`data_dst/aligned`에는 `RTM WF Faceset.zip`에 있는 faceset 사용.

`data_src/aligned`에는 3번 스크립트로 만든 faceset 사용

- 타겟 얼굴이 바뀔 때마다, pretrained 모델을 새로운 것으로 초기화해준다.(itration이 0인 것으로)
- usage: `bash 5_train.sh {$target_backup_iteration}` -> `bash 5_train.sh 10000`
- 학습 설정은 기존에 설정대로 진행하면 되지만 iteration 목표치를 따로 설정해주지 않는다면 무한히 학습을 진행하게 된다.
