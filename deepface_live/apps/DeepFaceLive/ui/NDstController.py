from localization import L
from resources.gfx import QXImageDB
from xlib import qt as qtx

from ..backend import FileSource
from .widgets.QBackendPanel import QBackendPanel
from .widgets.QButtonCSWDynamicSingleSwitch import \
    QButtonCSWDynamicSingleSwitch
from .widgets.QErrorCSWError import QErrorCSWError
from .widgets.QPathEditCSWPaths import QPathEditCSWPaths
from .widgets.QSliderCSWNumbers import QSliderCSWNumbers
from .widgets.QXPushButtonCSWSignal import QXPushButtonCSWSignal


class NDstController(QBackendPanel):
    def __init__(self, backend : FileSource):
        cs = backend.get_control_sheet()

        q_input_type  = QButtonCSWDynamicSingleSwitch(cs.input_type, horizontal=True, radio_buttons=True)
        q_input_paths = QPathEditCSWPaths(cs.input_paths)
        q_error       = QErrorCSWError(cs.error)

        btn_size = (32,32)
        btn_play_pause = QXPushButtonCSWSignal(cs.play,  image=QXImageDB.play_circle_outline('white'),  button_size=btn_size,
                                               csw_signal_tooggled=cs.pause, image_toggled=QXImageDB.pause_circle_outline('white'))
        q_frame_slider = QSliderCSWNumbers(cs.frame_index, cs.frame_count)

        main_l = qtx.QXVBoxLayout([q_input_type,
                                   q_input_paths,
                                   q_error, qtx.QXWidgetVBox([], spacing=0, fixed_height=10),
                                   qtx.QXFrameHBox([2, btn_play_pause, q_frame_slider], spacing=5)
                                   ], spacing=5)

        super().__init__(backend, L('Dst Controller'),
                         layout=main_l, content_align_top=True)

