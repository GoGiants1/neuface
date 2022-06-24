# Neu-Face Live 실행

```
neuface
├── train_scripts
├── scripts
|   ├── main.sh
|   ├── move.sh
|   └── prepare.sh
|
├── deepface_live
|   ├── build
|   |   └── linux
|   |       ├── data
|   |       |   └── dfm_models
|   |       |
|   |       ├── Dockerfile
|   |       ├── example.sh
|   |       └── start.sh
|   └── main.py
|
└── deepface_lab
```

## 1. dfm 모델 생성
deepface_lab을 사용하여 `dfm`모델을 생성한다. 이에 대한 자세한 설명은 Neu-Face Lab에 정리하였다.

## 2. live로 dfm 모델 이동
neuface/deepface_live/build/linux/data/dfm_models로 사용하고자하는 dfm 모델을 이동한다.
이 과정을 돕기 위해 neuface/scripts/move.sh 를 만들어두었다.

``` shell
#pwd : neuface/scripts
bash ./move.sh ../deepface_live/models/
```
위와 같이 스크립트를 실행하면, 인자로 준 경로 하위에 있는 모든 dfm 모델을 이동한다.

## 3. Neu-Fae Live 실행
dfm 모델을 준비한 뒤 live를 구동하는 방법은 docker를 사용하는 방법과 로컬에서 구동하는 방법 두 가지가 있다.

### 3-1. docker 실행
``` shell
#pwd : neuface/deepface_live/build/linux
./start.sh
```

위 명령어를 실행하면, 동일 폴더에 있는 Docekrfile을 구동하여 docker 환경에서 live를 구동한다.

### 3-2. local 실행
``` shell
#pwd : neuface/scripts
bash ./prepare.sh
bash ./main.sh
```
로컬 환경에서 실행하는 경우, prepare.sh로 환경을 설정한 뒤에, main.sh로 live를 실행한다.
단, 이는 회사에서 제공해준 서버에선 ubuntu 버전이 너무 낮아, pyqt6가 설치되지 않는다.
(따라서 서버 환경에서는 테스트해보지 못했다.)