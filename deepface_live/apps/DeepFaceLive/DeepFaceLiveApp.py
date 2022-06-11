from ctypes import alignment
from pathlib import Path
from typing import List

from localization import L, Localization
from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import os as lib_os
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel

from . import backend
from .ui.QCameraSource import QCameraSource
from .ui.QFaceAligner import QFaceAligner
from .ui.QFaceDetector import QFaceDetector
from .ui.QFaceMarker import QFaceMarker
from .ui.QFaceMerger import QFaceMerger
from .ui.QFaceAnimator import QFaceAnimator
from .ui.QFaceSwapper import QFaceSwapper
from .ui.NSrcController import NSrcController
from .ui.QFileSource import QFileSource
from .ui.NDstController import NDstController
from .ui.QFrameAdjuster import QFrameAdjuster
from .ui.QStreamOutput import QStreamOutput
from .ui.widgets.QBCFaceAlignViewer import QBCFaceAlignViewer
from .ui.widgets.QBCFaceSwapViewer import QBCFaceSwapViewer
from .ui.widgets.QBCMergedFrameViewer import QBCMergedFrameViewer
from .ui.widgets.QBCFrameViewer import QBCFrameViewer

_HIDDEN_WIDTH   = 0
_PREVIEW_WIDTH  = 512
_PREVIEW_HEIGHT = int(_PREVIEW_WIDTH * 0.78)
_CONTROL_HEIGHT = int(_PREVIEW_HEIGHT*0.37)
_BAR_HEIGHT     = 25
_WINDOW_WIDTH   = 2 * _PREVIEW_WIDTH
_WINDOW_HEIGHT  = _PREVIEW_HEIGHT + _CONTROL_HEIGHT + _BAR_HEIGHT + 5

class QLiveSwap(qtx.QXWidget):
    def __init__(self, userdata_path : Path,
                       settings_dirpath : Path):
        super().__init__()

        dfm_models_path = userdata_path / 'dfm_models'
        dfm_models_path.mkdir(parents=True, exist_ok=True)

        animatables_path = userdata_path / 'animatables'
        animatables_path.mkdir(parents=True, exist_ok=True)

        output_sequence_path = userdata_path / 'output_sequence'
        output_sequence_path.mkdir(parents=True, exist_ok=True)

        # Construct backend config
        backend_db          = self.backend_db          = backend.BackendDB( settings_dirpath / 'states.dat' )
        backend_weak_heap   = self.backend_weak_heap   = backend.BackendWeakHeap(size_mb=2048)
        reemit_frame_signal = self.reemit_frame_signal = backend.BackendSignal()

        multi_sources_bc_out  = backend.BackendConnection(multi_producer=True)
        face_detector_bc_out  = backend.BackendConnection()
        face_marker_bc_out    = backend.BackendConnection()
        face_aligner_bc_out   = backend.BackendConnection()
        face_swapper_bc_out   = backend.BackendConnection()
        frame_adjuster_bc_out = backend.BackendConnection()
        face_merger_bc_out    = backend.BackendConnection()

        file_source    = self.file_source    = backend.FileSource   (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_out=multi_sources_bc_out, backend_db=backend_db)
        camera_source  = self.camera_source  = backend.CameraSource (weak_heap=backend_weak_heap, bc_out=multi_sources_bc_out, backend_db=backend_db)
        face_detector  = self.face_detector  = backend.FaceDetector (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=multi_sources_bc_out, bc_out=face_detector_bc_out, backend_db=backend_db )
        face_marker    = self.face_marker    = backend.FaceMarker   (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_detector_bc_out, bc_out=face_marker_bc_out, backend_db=backend_db)
        face_aligner   = self.face_aligner   = backend.FaceAligner  (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_marker_bc_out, bc_out=face_aligner_bc_out, backend_db=backend_db )
        face_animator  = self.face_animator  = backend.FaceAnimator (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_aligner_bc_out, bc_out=face_merger_bc_out, animatables_path=animatables_path, backend_db=backend_db )

        face_swapper   = self.face_swapper   = backend.FaceSwapper  (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_aligner_bc_out, bc_out=face_swapper_bc_out, dfm_models_path=dfm_models_path, backend_db=backend_db )
        frame_adjuster = self.frame_adjuster = backend.FrameAdjuster(weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_swapper_bc_out, bc_out=frame_adjuster_bc_out, backend_db=backend_db )
        face_merger    = self.face_merger    = backend.FaceMerger   (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=frame_adjuster_bc_out, bc_out=face_merger_bc_out, backend_db=backend_db )
        stream_output  = self.stream_output  = backend.StreamOutput (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_merger_bc_out, save_default_path=userdata_path, backend_db=backend_db)

        self.all_backends : List[backend.BackendHost] = [file_source, camera_source, face_detector, face_marker, face_aligner, face_animator, face_swapper, frame_adjuster, face_merger, stream_output]

        self.q_file_source    = QFileSource(self.file_source)
        self.q_camera_source  = QCameraSource(self.camera_source)
        self.q_face_detector  = QFaceDetector(self.face_detector).boot()
        self.q_face_marker    = QFaceMarker(self.face_marker).boot()
        self.q_face_aligner   = QFaceAligner(self.face_aligner).boot()
        self.q_face_animator  = QFaceAnimator(self.face_animator, animatables_path=animatables_path).boot()
        self.q_face_swapper   = QFaceSwapper(self.face_swapper, dfm_models_path=dfm_models_path)
        self.q_frame_adjuster = QFrameAdjuster(self.frame_adjuster).boot()
        self.q_face_merger    = QFaceMerger(self.face_merger).boot()
        self.q_stream_output  = QStreamOutput(self.stream_output).boot()

        self.q_ds_frame_viewer = QBCFrameViewer(backend_weak_heap, multi_sources_bc_out, preview_width=_PREVIEW_WIDTH)
        self.q_ds_fa_viewer    = QBCFaceAlignViewer(backend_weak_heap, face_aligner_bc_out, preview_width=0)
        self.q_ds_fc_viewer    = QBCFaceSwapViewer(backend_weak_heap, face_merger_bc_out, preview_width=0)
        self.q_ds_merged_frame_viewer = QBCMergedFrameViewer(backend_weak_heap, face_merger_bc_out, preview_width=_PREVIEW_WIDTH)

        # Neu-face UI
        self.n_dst_controller  = NDstController(self.file_source).boot()
        self.n_src_controller  = NSrcController(self.face_swapper, dfm_models_path=dfm_models_path, fixed_width=_PREVIEW_WIDTH).boot()

        q_nodes = qtx.QXWidgetHBox([    qtx.QXWidgetVBox([self.q_file_source, self.q_camera_source], spacing=0, fixed_width=_HIDDEN_WIDTH),
                                        qtx.QXWidgetVBox([self.q_face_detector,  self.q_face_aligner,], spacing=0, fixed_width=_HIDDEN_WIDTH),
                                        qtx.QXWidgetVBox([self.q_face_marker, self.q_face_animator, self.q_face_swapper], spacing=0, fixed_width=_HIDDEN_WIDTH),
                                        qtx.QXWidgetVBox([self.q_frame_adjuster, self.q_face_merger, self.q_stream_output], spacing=0, fixed_width=_HIDDEN_WIDTH),
                                    ], spacing=0, size_policy=('fixed', 'fixed'), fixed_height=_HIDDEN_WIDTH)

        q_view_nodes = qtx.QXWidgetHBox([   (qtx.QXWidgetVBox([self.q_ds_frame_viewer], fixed_width=_PREVIEW_WIDTH, fixed_height=_PREVIEW_HEIGHT), qtx.AlignTop),
                                            (qtx.QXWidgetVBox([self.q_ds_fa_viewer], fixed_width=_HIDDEN_WIDTH), qtx.AlignTop),
                                            (qtx.QXWidgetVBox([self.q_ds_fc_viewer], fixed_width=_HIDDEN_WIDTH), qtx.AlignTop),
                                            (qtx.QXWidgetVBox([self.q_ds_merged_frame_viewer], fixed_width=_PREVIEW_WIDTH, fixed_height=_PREVIEW_HEIGHT), qtx.AlignTop),
                                        ], spacing=0, size_policy=('fixed', 'fixed') )

        q_control_nodes = qtx.QXWidgetHBox([ qtx.QXWidgetVBox([self.n_dst_controller], fixed_width=_PREVIEW_WIDTH, fixed_height=_CONTROL_HEIGHT),
                                             qtx.QXWidgetVBox([self.n_src_controller], fixed_width=_PREVIEW_WIDTH, fixed_height=_CONTROL_HEIGHT),
                                           ], spacing=0, size_policy=('fixed', 'fixed') )

        self.setLayout(qtx.QXVBoxLayout( [ (qtx.QXWidgetVBox([q_nodes, q_view_nodes, q_control_nodes], fixed_width=_WINDOW_WIDTH, spacing=0), qtx.AlignCenter) ]))

        self._timer = qtx.QXTimer(interval=5, timeout=self._on_timer_5ms, start=True)

    def _process_messages(self):
        self.backend_db.process_messages()
        for backend in self.all_backends:
            backend.process_messages()

    def _on_timer_5ms(self):
        self._process_messages()

    def clear_backend_db(self):
        self.backend_db.clear()

    def initialize(self):
        for bcknd in self.all_backends:
            default_state = True
            if isinstance(bcknd, (backend.CameraSource, backend.FaceAnimator) ):
                default_state = False
            bcknd.restore_on_off_state(default_state=default_state)

    def finalize(self):
        # Gracefully stop the backend
        for backend in self.all_backends:
            while backend.is_starting() or backend.is_stopping():
                self._process_messages()

            backend.save_on_off_state()
            backend.stop()

        while not all( x.is_stopped() for x in self.all_backends ):
            self._process_messages()

        self.backend_db.finish_pending_jobs()

        self.q_ds_frame_viewer.clear()
        self.q_ds_fa_viewer.clear()

class QDFLAppWindow(qtx.QXWindow):

    def __init__(self, userdata_path, settings_dirpath):
        self.m_flag = False
        super().__init__(save_load_state=True, size_policy=('minimum', 'minimum') )

        self._userdata_path = userdata_path
        self._settings_dirpath = settings_dirpath
        self.setWindowFlag(qtx.Qt.WindowType.FramelessWindowHint)

        self.q_live_swap = None
        self.q_live_swap_container = qtx.QXWidget()

        def mousePressEvent(event):
            if event.button()==qtx.Qt.MouseButton.LeftButton:
                self.m_flag = True
                self.m_Position = event.pos()
                event.accept()

        def mouseMoveEvent(event):
            if qtx.Qt.MouseButton.LeftButton and self.m_flag:  
                self.move(self.pos() - (self.m_Position - event.pos()))
                self.m_position = event.pos()
                event.accept()

        def mouseReleaseEvent(event):
            self.m_flag=False
            event.accept()

        self.content_l = qtx.QXVBoxLayout()
        self.q_title = qtx.QXPushButton(image=QXImageDB.app_icon(), text='NeuFaceLive', flat=True, fixed_width=_WINDOW_WIDTH-_BAR_HEIGHT*3, fixed_height=_BAR_HEIGHT)
        self.q_title.mousePressEvent = mousePressEvent
        self.q_title.mouseMoveEvent = mouseMoveEvent
        self.q_title.mouseReleaseEvent = mouseReleaseEvent

        self.q_minimize_btn = qtx.QXPushButton(image=QXImageDB.minimize_outline('white'), flat=True, fixed_width=int(_BAR_HEIGHT*1.5), fixed_height=_BAR_HEIGHT)
        self.q_minimize_btn.connect_signal(self.showMinimized, self.q_minimize_btn.clicked)

        self.q_close_btn = qtx.QXPushButton(image=QXImageDB.close_outline('white'), flat=True, fixed_width=int(_BAR_HEIGHT*1.5), fixed_height=_BAR_HEIGHT)
        self.q_close_btn.connect_signal(self.__close, self.q_close_btn.clicked)

        self.titlebar = qtx.QXWidgetHBox([  self.q_title, self.q_minimize_btn, self.q_close_btn ])

        self.setLayout( qtx.QXVBoxLayout([self.titlebar, qtx.QXWidget(layout=self.content_l) ]))

        self.call_on_closeEvent(self._on_closeEvent)

        q_live_swap = self.q_live_swap = QLiveSwap(userdata_path=self._userdata_path, settings_dirpath=self._settings_dirpath)
        q_live_swap.initialize()
        self.content_l.addWidget(q_live_swap)
        self.setFixedWidth(_WINDOW_WIDTH)
        self.setMaximumWidth(_WINDOW_WIDTH)
        self.setFixedHeight(_WINDOW_HEIGHT)
        self.setMaximumHeight(_WINDOW_HEIGHT)

    def _on_reset_modules_settings(self):
        if self.q_live_swap is not None:
            self.q_live_swap.clear_backend_db()
            qtx.QXMainApplication.inst.reinitialize()

    def _on_cb_process_priority_choice(self, prio : lib_os.ProcessPriority, _):
        lib_os.set_process_priority(prio)

        if self.q_live_swap is not None:
            qtx.QXMainApplication.inst.reinitialize()

    def finalize(self):
        self.q_live_swap.finalize()

    def _on_closeEvent(self):
        self.finalize()

    def __close(self):
        self.finalize()
        self.close()


class DeepFaceLiveApp(qtx.QXMainApplication):
    def __init__(self, userdata_path):
        self.userdata_path = userdata_path
        settings_dirpath = self.settings_dirpath =  userdata_path / 'settings'
        if not settings_dirpath.exists():
            settings_dirpath.mkdir(parents=True)
        super().__init__(app_name='NeuFaceLive', settings_dirpath=settings_dirpath)

        self.setFont( QXFontDB.get_default_font() )
        self.setWindowIcon( QXImageDB.app_icon().as_QIcon() )

        splash_wnd = self.splash_wnd =\
            qtx.QXSplashWindow(layout=qtx.QXVBoxLayout([ (qtx.QXLabel(image=QXImageDB.splash_deepfacelive()), qtx.AlignCenter)
                                                       ], contents_margins=20))

        self._dfl_wnd = None
        self._t = qtx.QXTimer(interval=1666, timeout=self._on_splash_wnd_expired, single_shot=True, start=True)
        self.initialize()

    def on_reinitialize(self):
        self.finalize()

        import gc
        gc.collect()
        gc.collect()

        self.initialize()
        self._dfl_wnd.show()

    def initialize(self):
        Localization.set_language( self.get_language() )

        if self._dfl_wnd is None:
            self._dfl_wnd = QDFLAppWindow(userdata_path=self.userdata_path, settings_dirpath=self.settings_dirpath)

    def finalize(self):
        if self._dfl_wnd is not None:
            self._dfl_wnd.close()
            self._dfl_wnd.deleteLater()
            self._dfl_wnd = None

    def _on_splash_wnd_expired(self):
        self._dfl_wnd.show()

        if self.splash_wnd is not None:
            self.splash_wnd.hide()
            self.splash_wnd.deleteLater()
            self.splash_wnd = None
