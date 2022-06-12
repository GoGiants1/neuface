from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QXPushButtonCSWSignal(QCSWControl):
    def __init__(self,  csw_signal : lib_csw.Signal.Client, reflect_state_widgets=None,
                        image=None,
                        text=None, button_size=None, flat=False,
                        csw_signal_tooggled=None, image_toggled=None,
                        **kwargs):
        """
        Implements lib_csw.Signal control as QXPushButton
        """
        if not isinstance(csw_signal, lib_csw.Signal.Client):
            raise ValueError('csw_signal must be an instance of Signal.Client')

        self._csw_signal = csw_signal
        self._image      = image

        self._is_toggleable      = csw_signal_tooggled != None
        self._toggled            = False
        self._csw_signal_toogled = csw_signal_tooggled
        self._image_toggled      = image_toggled

        btn = self._btn = qtx.QXPushButton(image=image, text=text, released=self.on_btn_released, fixed_size=button_size, flat=flat)

        super().__init__(csw_control=csw_signal, reflect_state_widgets=reflect_state_widgets,
                         layout=qtx.QXHBoxLayout([btn]), **kwargs)

    def on_btn_released(self):
        if self._is_toggleable:
            if self._toggled:
                self._csw_signal_toogled.signal()
            else: 
                self._csw_signal.signal()
            self._toggled = not self._toggled
            self._btn.set_image(self._image_toggled if self._toggled else self._image)
        else:
            self._csw_signal.signal()
