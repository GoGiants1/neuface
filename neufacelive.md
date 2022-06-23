# Documentation of NeuFace Live Source Codes

## Directory Structure

```
neuface
└── deepface_live
    ├── apps
    |   └── DeepFaceLive
    |       ├── backend
    |       │   ├── BackendBase.py
    |       │   ├── CameraSource.py
    |       │   ├── FaceAligner.py
    |       │   ├── FaceAnimator.py
    |       │   ...
    |       ├── ui
    |       │   ├── NDstController.py
    |       │   ├── NSrcController.py
    |       │   ...
    |       └── DeepFaceLiveApp.py
    └── modelhub
        └── DFLive
            └── DFMModel.py
```

위 디렉토리 구조는 Neu-Face에서 수정하거나, 직접적으로 연관이 있는 파일을 나열한 것이다. 위에는 표시하지 않았지만, 다른 파일들도(eg. `apps/ui/widgets`) 동작에 관여한다.

## Common Properties

### Subclasses of BackendHost and BackendWorker

모든 모듈은 BackendHost의 subclass와, BackendWorker의 subclass로 이루어진다.

BackendHost의 subclass는 모듈 간 정보 교환을 위한 기본적인 세팅을 다룰 뿐이고, 각 모듈의 핵심은 BackendWorker의 subclass에 구현된다.

### Main Component of Subclasses of BackendWorker

#### `on_start`

기본적인 변수 선언 및 초기화를 하는 메소드이다.

#### `on_tick`

프레임 각각을 합성할 때마다 사용되는 메소드이다. 각 모듈의 근본적인 작동 코드는 이 메소드에 구현이 되어있다.

#### 중요한 변수

- `bcd`: 다른 모듈로 넘겨주고 싶은 데이터를 저장할 수 있는 변수이다. 이것의 메소드는 BackendBase.py에 구현되어 있다. 주로 `setter`, `getter` 용으로만 사용한다.

### WorkerState

각 모듈마다 저장되어야 하는 상태 변수들을 선언해놓은 class이다. 다른 모듈과 공유되지 않는다. Worker에서 `get_state()`를 통해 이 변수들을 사용한다.

# Summary for each module

## FileSource

파일로부터 Dst를 읽어올 때, Dst로 사용할 프레임을 `bcd`에 저장한다.

## CameraSource

웹캠을 사용할 수 있는 경우에, 카메라로 부터 받은 Dst로 사용할 프레임을 `bcd`에 저장하는 모듈이다.

## FaceAligner

Dst 프레임을 얼굴의 각도에 맞춰서 회전 및 확대시키는 모듈이다.
Dst 프레임 이미지를 받아, `bcd`에 `align_img`와 `align_mask_img`를 전달한다.

## FaceDetector

Dst 프레임에서 얼굴이 어느 위치에 있는지 찾아 `bcd`에 `BackendFaceSwapInfo` 라는 형식으로 추가한다. 사전에 알려진 detector가 3개 구현이 되어있고, 현재 기본값으로는 YOLOv5를 사용한다.

## FaceMarker

Dst 프레임과 FaceDetector에서 찾아낸 얼굴 위치를 받아오고, 그 범위 안에서 landmark를 찾아 FLandmarks2D 라는 형식으로 `bcd`에 저장한다. 현재 기본값으로는 google_facemesh를 사용한다.

## FaceAnimator

TPSMM Model을 사용하여 간단하게 움직이는 얼굴을 만드는 모듈이다. 하지만 여기에서는 사용되지 않는다.

## FaceSwapper

Dst 프레임, FaceDetector와 FaceMarker에서 찾아낸 얼굴 정보, dfm Model을 활용하여 새로운 얼굴 이미지, 그 이미지의 마스킹 정보를 만들어 `bcd`에 저장한다.

## FaceMerger

Dst 프레임, FaceDetector와 FaceMarker에서 찾아낸 얼굴 정보, FaceSwapper에서 생성한 새로운 얼굴 이미지와 마스크 프레임을 받아와 합성한 프레임을 `bcd`에 저장한다. 실질적인 마스킹과 Blending이 적용된다.

## FrameAdjuster

Face-off가 오래걸려 프레임 드랍이 일어날 수 있을때, 이전 프레임을 재활용하여 사용한다.

## StreamOutput

합성된 최종 결과물을 실제로 띄우기 위한 모듈이다.

## BackendBase

위의 모듈 사이에서 전달되는 데이터나 상위 클래스가 선언되어 있는 모듈이다.
face에서 찾아낸 데이터에 관련된 것은 BackendFaceSwapInfo에서, 전반적인 세팅 값이나 중간 결과값들은 BackendConnectionData에서 관리한다.

또한, 자동으로 backend가 실행될 수 있도록, 여러 설정을 기본값으로 수행하는 `boot()` 함수를 구현하였다. 이 함수는 자신을 반환하여, `instance = MyBackend().boot()` 꼴로 인스턴스화와 동시에 가동하는 방식으로 사용하였다.

## DFMModel

dfm으로 저장되어 있는 모델을 불러올 수 있게 도와주는 모듈이다. 로컬 폴더에 dfm 파일을 저장하는 방법, DFMModel.py의 get_available_models_info에 DFMModelInfo를 직접 추가하는 방법으로 dfm 모델을 불러올 수 있다. DFMModelInfo를 추가한다면 url을 통해 서버에 있는 모델 파일을 다운로드 받을 수 있다.

# GUI of Neu-Face Live

![neuface_gui](https://user-images.githubusercontent.com/35912840/175318067-09e55d69-94a3-4da7-88fb-eb92521fa092.png)
기본적으로 GUI는 pyqt6를 사용하여 구현되어 있다. 위에서 설명한 backend에서 기능을 수행하고, GUI는 backend와 통신하며 사용자에게 인터페이스를 제공한다.

## DeepFaceLiveApp

이 모듈은 GUI의 메인창을 담당한다. `DeepFaceLiveApp`는 Main Window로 기본 바탕이 되는 창이고, 이 위에 `QDFLAppWindow`가 그려지게 된다. 우리의 디자인에 맞게 창을 변경하기 위해 `QDFLAppWindow`의 기본 창 테두리를 없애고, 위에 로고와 제목을 추가하였다. 이때 기본 창 테두리를 없애서 창 닫기, 최소화 버튼 그리고 드래그로 창 옮기기 기능을 직접 만들어주었다.  
`QLiveSwap`은 실제로 backend와 통신하며 인터페이스를 그린다. 그를 위해 여러 backend들의 instance와 ui의 instance를 생성한다. 우리는 여러 하이퍼 파라미터를 자동으로 설정하고, 백엔드를 자동 실행하기 위해 `BackendBase`에서 auto-boot 기능(위 [BackendBase](#backendbase)->`boot()`함수)을 직접 구현하여 사용하였다.

## NDstController

이 모듈은 `FileSource`를 backend로 사용하는 GUI이다. 합성을 수행할 dst입력을 통제하는 패널을 그린다. 위 그림의 1.과 2.를 담당한다.

## NSrcController

이 모듈은 `FaceSwapper`를 backend로 사용하는 GUI이다. 합성된 결과인 merged에서 후처리를 조정하는 패널을 그린다. 위 그림의 3.과 4.를 담당한다. 여기서 설정된 `poisson_size`값은 `FaceSwapper`를 거쳐 `FaceMerger`로 전달된다.

# Modified Parts

- FaceSwapper [`Line 58:59,133:154,269:270,281:283,350:356,403:404,425:426,440:441`]
  - 새로 추가한 슬라이더에 맞게 Gaussian Sharpen 수치 조정할 수 있도록 수정
  - 새로 추가한 슬라이더에서 Poisson Blending 수치를 bcd에 저장하도록 추가
- FaceMerger [`Line 210,244:254,279,357,370,372`]
  - Poisson Blending이 켜져있으면 Poisson Blending을 적용하도록 추가
- BackendBase [`Line 62,135,136`]
  - Poisson Blending 수치를 전달할 수 있도록 변수 및 `setter`, `getter` 추가
- DFMModel [`Line 53:63`]
  - 직접 학습한 모델을 특정 url에 업로드를 하고 다운로드 받는 방식으로 추가
- DeepFaceLiveApp [`Line 30:38, 97:117, 164, 169:209, 225:231`]
  - GUI의 메인 창을 담당하는 파일이다.
- NDstController
  - Dst 입력을 통제하기 위해 새로 생성한 GUI 이다.
- NSrcController
  - Src 입력을 통제하기 위해 새로 생성한 GUI 이다.
