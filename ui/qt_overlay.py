"""Anti-aliased, click-through prediction overlay backed by PyQt6."""

import ctypes
import sys

from PyQt6.QtCore import QLineF, QRectF, Qt, qInstallMessageHandler
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget


def _qt_message_handler(_mode, context, message):
    """Suppress Qt's harmless duplicate-DPI-context warning from Tk startup."""
    if context.category == 'qt.qpa.window' and (
        message.startswith('SetProcessDpiAwarenessContext() failed: Access is denied.')
        or message.startswith("Qt's default DPI awareness context is")
    ):
        return
    sys.stderr.write(f'{message}\n')


qInstallMessageHandler(_qt_message_handler)


class PredictionOverlay(QWidget):
    """A transparent full-screen vector surface used only for predictions."""

    def __init__(self):
        # Tk has already established this process's DPI context.  Keep Qt in
        # 96-DPI logical coordinates so its full-screen geometry matches the
        # screen coordinates used by the simulator and avoids a Qt warning.
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi, True)
        app = QApplication.instance()
        self._app = app if app is not None else QApplication(sys.argv[:1])
        super().__init__()
        self._lines = []
        self._circles = []
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        screen = self._app.primaryScreen()
        self.setGeometry(screen.geometry())
        self.show()
        self._enable_native_click_through()

    def _enable_native_click_through(self):
        """Make Windows pass native mouse input through this overlay too."""
        try:
            hwnd = int(self.winId())
            GWL_EXSTYLE = -20
            WS_EX_TRANSPARENT = 0x20
            WS_EX_LAYERED = 0x80000
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_TRANSPARENT | WS_EX_LAYERED)
        except (AttributeError, OSError):
            pass

    def clear(self):
        self._lines.clear()
        self._circles.clear()

    def set_opacity(self, opacity):
        self.setWindowOpacity(max(0.0, min(1.0, float(opacity))))

    def add_line(self, x1, y1, x2, y2, color, width):
        self._lines.append((float(x1), float(y1), float(x2), float(y2), tuple(color), float(width)))

    def add_circle(self, x, y, radius, color, width):
        self._circles.append((float(x), float(y), float(radius), tuple(color), float(width)))

    def present(self):
        self.raise_()
        self.update()
        self._app.processEvents()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        for x1, y1, x2, y2, color, width in self._lines:
            painter.setPen(QPen(QColor(*color), width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QLineF(x1, y1, x2, y2))
        for x, y, radius, color, width in self._circles:
            painter.setPen(QPen(QColor(*color), width))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(x - radius, y - radius, radius * 2, radius * 2))
        painter.end()
