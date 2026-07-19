import math
import random
from collections import deque

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRectF, Property, QPointF
from PySide6.QtGui import (
    QPainter, QFont, QColor, QPen, QBrush, QPainterPath,
    QFontMetrics, QLinearGradient,
)

from src.utils.logger import get_logger

logger = get_logger(__name__)

def _build_bubble_path(w: float, h: float, tail_h: float) -> QPainterPath:
    """
    Build a smooth, compact elliptical/pill-shaped chat bubble.
    A simple pointed tail points down towards the pet.
    """
    body_h = h - tail_h
    path = QPainterPath()
    
    # ── Ellipse / Pill body ──
    # Maximum corner rounding makes a pill shape, which looks elliptical 
    # but tightly fits wrapped text without wasting space.
    radius = min(w, body_h) / 2.0
    path.addRoundedRect(0, 0, w, body_h, radius, radius)
    
    # ── Chat Tail ──
    # A simple triangle pointing down-left
    tail_w = 14.0
    tail_x = w * 0.4
    
    tail = QPainterPath()
    tail.moveTo(tail_x, body_h - 4)
    tail.lineTo(tail_x - 10, h)
    tail.lineTo(tail_x + tail_w, body_h - 4)
    tail.closeSubpath()
    
    path = path.united(tail)
    return path


# ─── SpeechBubble ─────────────────────────────────────────────────────────────

class SpeechBubble(QWidget):
    """
    A thought-cloud speech bubble with:
      • proper cloud silhouette (overlapping circles unified into one path)
      • pop-in / pop-out scale animation (OutBack / InBack easing)
      • gentle idle float animation while visible
      • typewriter text reveal
      • message queue — queue_messages([msg1, msg2, ...]) shows them sequentially
        with an 11-second gap between each bubble
      • screen-edge clamping (size is pre-calculated before .show())
    """

    # ── Layout constants ──────────────────────────────────────────────────────
    _TAIL_H     = 18    # px at bottom reserved for the triangular tail
    _MAX_TEXT_W = 180   # max width for wrapping (smaller = more compact/squarish)
    _MAX_CHARS  = 120   
    # Tighter insets for a small bubble
    _INSET_L    = 22
    _INSET_R    = 22
    _INSET_T    = 16
    _INSET_B    = 14

    # Delay between consecutive queued bubbles (ms)
    _INTER_BUBBLE_DELAY_MS = 11_000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.bubble_font = QFont("Segoe UI", 10, QFont.Weight.Bold)

        # ── Internal state ─────────────────────────────────────────────────
        self._pop_scale  = 0.0
        self._float_tick = 0.0
        self._bubble_path = QPainterPath()

        self.full_text    = ""
        self.current_text = ""
        self.char_index   = 0

        # Callback to invoke when the pop animation finishes.
        # We connect pop_anim.finished ONCE to a dispatcher, avoiding
        # repeated connect/disconnect calls that cause RuntimeWarnings.
        self._finish_callback = None

        # ── Message queue ──────────────────────────────────────────────────
        self._queue: deque[str] = deque()

        # ── Animations & timers ────────────────────────────────────────────
        self.pop_anim = QPropertyAnimation(self, b"pop_scale")
        self.pop_anim.setDuration(420)
        # Single persistent connection — routes to _finish_callback when set
        self.pop_anim.finished.connect(self._on_anim_finished)

        self.type_timer = QTimer(self)
        self.type_timer.timeout.connect(self._type_next_char)

        # Auto-hide: fires when the current bubble has been fully read
        self.hide_timer = QTimer(self)
        self.hide_timer.timeout.connect(self._finish_current_bubble)
        self.hide_timer.setSingleShot(True)

        # Inter-bubble delay: fires to show the next queued bubble
        self.next_timer = QTimer(self)
        self.next_timer.timeout.connect(self._show_next_from_queue)
        self.next_timer.setSingleShot(True)

        # Float repaint ticker
        self.float_timer = QTimer(self)
        self.float_timer.setInterval(16)
        self.float_timer.timeout.connect(self._tick_float)

    # ── Qt Property ───────────────────────────────────────────────────────────

    @Property(float)
    def pop_scale(self):
        return self._pop_scale

    @pop_scale.setter
    def pop_scale(self, value: float):
        self._pop_scale = value
        self.update()

    # ── Bubble geometry ─────────────────────────────────────────────────────────

    def _rebuild_bubble(self, w: int, h: int):
        self._bubble_path = _build_bubble_path(float(w), float(h), self._TAIL_H)

    # ── Public API ─────────────────────────────────────────────────────────────

    def show_message(self, text: str, duration_ms: int = 4000):
        """Show a single message immediately, interrupting any current bubble."""
        self._queue.clear()
        self.next_timer.stop()
        self._display(text, duration_ms)

    def queue_messages(self, messages: list[str], duration_ms: int = 4000):
        """
        Queue multiple messages. The first appears immediately; each subsequent
        one pops up _INTER_BUBBLE_DELAY_MS after the previous one disappears.
        """
        if not messages:
            return

        # Stop anything currently running
        self._stop_all()
        self._queue.clear()

        # Load all messages into the queue (in order)
        for msg in messages:
            self._queue.append((msg, duration_ms))

        # Show the first one right away
        self._show_next_from_queue()

    # ── Queue internals ────────────────────────────────────────────────────────

    def _show_next_from_queue(self):
        if not self._queue:
            return
        text, duration_ms = self._queue.popleft()
        self._display(text, duration_ms)

    def _finish_current_bubble(self):
        """Fade out the current bubble, then schedule the next one if any."""
        self._pop_out(callback=self._on_bubble_hidden)

    def _on_bubble_hidden(self):
        self.hide()
        self.float_timer.stop()
        if self._queue:
            self.next_timer.start(self._INTER_BUBBLE_DELAY_MS)

    # ── Core display logic ─────────────────────────────────────────────────────

    def _display(self, text: str, duration_ms: int):
        """Pre-size, show, and animate one bubble for the given text."""
        self._stop_all()

        # Clamp length
        if len(text) > self._MAX_CHARS:
            text = text[:self._MAX_CHARS].rstrip() + "…"

        self.full_text    = text
        self.current_text = ""
        self.char_index   = 0

        # Measure the natural size the text needs at our max wrap width.
        # We pass a large height so boundingRect never clips vertically.
        fm    = QFontMetrics(self.bubble_font)
        flags = int(Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignCenter)
        rect  = fm.boundingRect(0, 0, self._MAX_TEXT_W, 4000, flags, text)

        # rect.width/height = actual text area needed (≤ _MAX_TEXT_W wide)
        # Add insets around that measured area to get the widget (cloud) size.
        w = max(100, rect.width()  + self._INSET_L + self._INSET_R)
        h = max(60,  rect.height() + self._INSET_T + self._INSET_B + self._TAIL_H)
        self.resize(w, h)
        self._rebuild_bubble(w, h)

        self.show()
        self.float_timer.start()

        # Pop-in animation
        self.pop_anim.stop()
        self.pop_anim.setStartValue(0.0)
        self.pop_anim.setEndValue(1.0)
        self.pop_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.pop_anim.start()

        # Typewriter
        self.type_timer.start(28)

        # Schedule hide after reading time
        total_type_ms = len(text) * 28
        self.hide_timer.start(duration_ms + total_type_ms)

    def _pop_out(self, callback=None):
        """Animate scale to 0, then invoke callback (if any) via the dispatcher."""
        self._finish_callback = callback
        self.pop_anim.stop()
        self.pop_anim.setStartValue(self._pop_scale)
        self.pop_anim.setEndValue(0.0)
        self.pop_anim.setEasingCurve(QEasingCurve.Type.InBack)
        self.pop_anim.start()

    def _stop_all(self):
        """Halt all timers and the pop animation without triggering any callback."""
        self._finish_callback = None   # clear before stopping so dispatcher is a no-op
        self.pop_anim.stop()
        self.type_timer.stop()
        self.hide_timer.stop()
        self.next_timer.stop()

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_anim_finished(self):
        """Single dispatcher connected to pop_anim.finished exactly once."""
        cb = self._finish_callback
        self._finish_callback = None
        if cb is not None:
            cb()

    def _type_next_char(self):
        if self.char_index < len(self.full_text):
            self.current_text += self.full_text[self.char_index]
            self.char_index   += 1
            self.update()
        else:
            self.type_timer.stop()

    def _tick_float(self):
        self._float_tick += 0.04
        self.update()

    def hide_bubble(self):
        """External call to immediately dismiss the current bubble."""
        self._stop_all()
        self._pop_out(callback=lambda: (self.hide(), self.float_timer.stop()))

    # ── Painting ───────────────────────────────────────────────────────────────

    def paintEvent(self, _event):
        if self._pop_scale <= 0.005:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w  = float(self.width())
        h  = float(self.height())
        cx = w / 2.0
        cy = h / 2.0

        float_dy = math.sin(self._float_tick) * 3.0

        painter.translate(cx, cy + float_dy)
        painter.scale(self._pop_scale, self._pop_scale)
        painter.translate(-cx, -cy)

        # Drop shadow
        shadow = self._bubble_path.translated(3, 5)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 35)))
        painter.drawPath(shadow)

        # Bubble fill gradient
        grad = QLinearGradient(QPointF(cx, 0), QPointF(cx, h - self._TAIL_H))
        grad.setColorAt(0.0, QColor(255, 255, 255))
        grad.setColorAt(1.0, QColor(245, 248, 255))

        painter.setPen(
            QPen(QColor(80, 90, 110, 200), 2.2,
                 Qt.PenStyle.SolidLine,
                 Qt.PenCapStyle.RoundCap,
                 Qt.PenJoinStyle.RoundJoin)
        )
        painter.setBrush(QBrush(grad))
        painter.drawPath(self._bubble_path)

        # Gloss highlight
        gloss = QLinearGradient(QPointF(cx * 0.5, 6), QPointF(cx * 0.5, (h - self._TAIL_H) * 0.5))
        gloss.setColorAt(0.0, QColor(255, 255, 255, 160))
        gloss.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gloss))
        painter.save()
        painter.setClipPath(self._bubble_path)
        painter.drawEllipse(QRectF(w * 0.08, 2, w * 0.6, (h - self._TAIL_H) * 0.45))
        painter.restore()

        # Text
        painter.setFont(self.bubble_font)
        painter.setPen(QColor(28, 32, 48))
        text_rect = QRectF(
            self._INSET_L,
            self._INSET_T,
            w - self._INSET_L - self._INSET_R,
            h - self._TAIL_H - self._INSET_T - self._INSET_B,
        )
        flags = int(Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignCenter)
        painter.drawText(text_rect, flags, self.current_text)
