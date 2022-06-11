from pathlib import Path

from localization import L
from resources.gfx import QXImageDB
from xlib import qt as qtx

from ..backend import FaceSwapper
from .widgets.QBackendPanel import QBackendPanel
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QComboBoxCSWDynamicSingleSwitch import \
    QComboBoxCSWDynamicSingleSwitch
from .widgets.QErrorCSWError import QErrorCSWError
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QLabelPopupInfoCSWInfoLabel import QLabelPopupInfoCSWInfoLabel
from .widgets.QProgressBarCSWProgress import QProgressBarCSWProgress
from .widgets.QSliderCSWNumber import QSliderCSWNumber
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber


class NSrcController(QBackendPanel):
    def __init__(self, backend : FaceSwapper, dfm_models_path : Path):
        self._dfm_models_path = dfm_models_path

        cs = backend.get_control_sheet()

        btn_open_folder = self.btn_open_folder = qtx.QXPushButton(image = QXImageDB.eye_outline('light gray'), tooltip_text='Reveal in Explorer', released=self._btn_open_folder_released, fixed_size=(24,22) )

        q_select_label  = QLabelPopupInfo(label=L('Select the Device and Model'), popup_info_text=L('@common.help.device') )
        q_device        = QComboBoxCSWDynamicSingleSwitch(cs.device, reflect_state_widgets=[q_select_label])
        q_model         = QComboBoxCSWDynamicSingleSwitch(cs.model, reflect_state_widgets=[q_select_label, btn_open_folder])

        q_model_dl_error = self._q_model_dl_error = QErrorCSWError(cs.model_dl_error)
        q_model_dl_progress = self._q_model_dl_progress = QProgressBarCSWProgress(cs.model_dl_progress)

        q_model_info_label = self._q_model_info_label = QLabelPopupInfoCSWInfoLabel(cs.model_info_label)

        q_poisson_label     = QLabelPopupInfo(label=L('Poisson') )
        q_poisson_enable    = QCheckBoxCSWFlag(cs.poisson_enable, reflect_state_widgets=[q_poisson_label])
        q_poisson_size      = QSliderCSWNumber(cs.poisson_size, reflect_state_widgets=[q_poisson_label])

        grid_l = qtx.QXGridLayout( spacing=5)
        row = 0
        grid_l.addWidget(q_select_label, row, 0, alignment=qtx.AlignLeft | qtx.AlignVCenter  )
        row += 1
        grid_l.addWidget(qtx.QXWidgetHBox([q_device], fixed_width=150), row, 0)
        grid_l.addWidget(qtx.QXWidgetHBox([q_model], fixed_width=300), row, 1)
        grid_l.addWidget(qtx.QXWidgetHBox([btn_open_folder, q_model_info_label], fixed_width=60), row, 2)
        row += 1
        grid_l.addWidget(qtx.QXWidgetVBox([], fixed_height=10), row, 0, 1, 2 )
        row += 1
        grid_l.addLayout(qtx.QXHBoxLayout([q_poisson_label, 2, q_poisson_enable, 2, q_poisson_size ]), row, 0, 1, 3 )
        row += 1
        grid_l.addWidget(q_model_dl_progress, row, 0, 1, 3 )
        row += 1
        grid_l.addWidget(q_model_dl_error, row, 0, 1, 3 )
        row += 1
        grid_l.addWidget(qtx.QXWidgetVBox([], fixed_height=25), row, 0, 1, 3 )

        super().__init__(backend, L('Src Controller'),
                         layout=qtx.QXVBoxLayout([grid_l]) )


    def _btn_open_folder_released(self):
        qtx.QDesktopServices.openUrl(qtx.QUrl.fromLocalFile( str(self._dfm_models_path) ))