import sys
import math
from PySide6.QtWidgets import QWidget, QApplication, QMenu
from PySide6.QtCore import Qt, QPoint, QPointF, QRect, QRectF
from PySide6.QtGui import (
    QPainter, QPixmap, QAction, QCursor, QColor, QBrush, QPen,
    QPainterPath, QPolygonF, QLinearGradient, QRadialGradient, QFont
)
import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # State for dragging
        self.dragging = False
        self.drag_offset = QPoint()

        # Current state info for procedural drawing
        self.current_state_id = "idle"
        self.mood_state = "neutral"
        self.tick = 0

        # Set a default position (center of primary screen)
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - config.PET_WIDTH) // 2
        y = (screen_geometry.height() - config.PET_HEIGHT) // 2
        self.move(x, y)

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(config.PET_WIDTH, config.PET_HEIGHT)

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _draw_panda_eye(self, painter: QPainter, cx, cy, look_x, rx=5.0, ry=6.0):
        """Draws a glossy panda eye: white sclera → black pupil → two catchlights."""
        # White sclera
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(QPointF(cx + look_x * 0.5, cy), rx, ry)
        # Black pupil (large, cute)
        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.drawEllipse(QPointF(cx + look_x, cy + 0.5), rx * 0.55, ry * 0.55)
        # Primary catchlight (top-left sparkle)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(QPointF(cx + look_x - rx * 0.22, cy - ry * 0.28), 1.8, 1.8)
        # Secondary sparkle (bottom-right, subtler)
        painter.setBrush(QBrush(QColor(255, 255, 255, 160)))
        painter.drawEllipse(QPointF(cx + look_x + rx * 0.25, cy + ry * 0.2), 0.9, 0.9)

    # ------------------------------------------------------------------
    # Main paint
    # ------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.tick += 1
        t = self.tick

        w = config.PET_WIDTH
        h = config.PET_HEIGHT
        cx, cy = w / 2, h / 2

        state = self.current_state_id

        # ── Base proportions (baby-schema: big round head, chubby body) ──
        head_x, head_y = cx, cy - 12
        head_rx, head_ry = 38, 32          # wide round head

        body_x, body_y = cx, cy + 16
        body_rx, body_ry = 26, 20          # chubby round tummy

        arm_l_x, arm_l_y = body_x - 22, body_y - 4
        arm_r_x, arm_r_y = body_x + 22, body_y - 4
        arm_rx, arm_ry = 10, 10

        leg_l_x, leg_l_y = body_x - 14, body_y + 16
        leg_r_x, leg_r_y = body_x + 14, body_y + 16
        leg_rx, leg_ry = 11, 9

        # Ears: center positions (round circles)
        ear_l_cx = head_x - 28
        ear_l_cy = head_y - head_ry + 4
        ear_r_cx = head_x + 28
        ear_r_cy = head_y - head_ry + 4
        ear_r_radius = 13

        tail_x, tail_y = body_x + 24, body_y + 10
        tail_angle = math.sin(t * 0.08) * 12

        look_dir = 0.0

        # ── Default face based on mood ──────────────────────────────────
        if self.mood_state == "very_happy":
            eye_type = "happy"
            mouth_type = "open"
        elif self.mood_state == "happy":
            eye_type = "happy"
            mouth_type = "w"
        elif self.mood_state == "sad":
            eye_type = "sad"
            mouth_type = "sad"
        elif self.mood_state == "angry":
            eye_type = "angry"
            mouth_type = "line"
        else: # neutral
            eye_type = "open"
            mouth_type = "w"

        # ── Animation offsets (can override face) ───────────────────────
        if state == "idle":
            breathe = math.sin(t * 0.055)
            head_y += breathe * 1.8
            body_ry += breathe * 1.2
            body_rx -= breathe * 0.6
            arm_l_y += breathe * 1.2
            arm_r_y += breathe * 1.2
            tail_angle = math.sin(t * 0.04) * 15

        elif state == "walk_left":
            head_x -= 3
            look_dir = -1
            bob = abs(math.sin(t * 0.25)) * 3.5
            head_y -= bob
            body_y -= bob
            arm_l_y -= bob
            arm_r_y -= bob
            leg_l_x += math.cos(t * 0.35) * 5
            leg_r_x += math.cos(t * 0.35 + math.pi) * 5
            leg_l_y -= max(0, math.sin(t * 0.35) * 3)
            leg_r_y -= max(0, math.sin(t * 0.35 + math.pi) * 3)
            tail_angle = 25 + math.sin(t * 0.35) * 18

        elif state == "walk_right":
            head_x += 3
            look_dir = 1
            bob = abs(math.sin(t * 0.25)) * 3.5
            head_y -= bob
            body_y -= bob
            arm_l_y -= bob
            arm_r_y -= bob
            leg_l_x += math.cos(t * 0.35) * 5
            leg_r_x += math.cos(t * 0.35 + math.pi) * 5
            leg_l_y -= max(0, math.sin(t * 0.35) * 3)
            leg_r_y -= max(0, math.sin(t * 0.35 + math.pi) * 3)
            tail_angle = -25 + math.sin(t * 0.35) * 18

        elif state == "sleep":
            # Lying-down pose: body squished flat, head resting to one side
            breathe = math.sin(t * 0.035)
            head_y += 18
            head_x += 10
            body_y += 14
            body_rx += 8          # wider = squished flat on the ground
            body_ry -= 6          # shorter = compressed vertically
            body_rx += breathe * 2.0
            body_ry -= breathe * 1.0
            head_y -= breathe * 1.0
            eye_type = "closed"
            mouth_type = "small"
            # Arms wrap forward (hugging bamboo)
            arm_l_x += 14
            arm_r_x += 8
            arm_l_y += 10
            arm_r_y += 12
            # Legs tuck back
            leg_l_y -= 2
            leg_l_x -= 8
            leg_r_y += 2
            tail_angle = 70 + breathe * 6

        elif state == "eat":
            bob = math.sin(t * 0.35) * 2.5
            head_y += bob
            eye_type = "happy"
            mouth_type = "open" if math.sin(t * 0.35) > 0 else "w"
            arm_l_x += 6
            arm_r_x -= 6
            arm_l_y -= 4
            arm_r_y -= 4

        elif state == "happy":
            eye_type = "happy"
            mouth_type = "open"
            bounce = abs(math.sin(t * 0.18)) * 4.5
            head_y -= bounce
            body_y -= bounce
            arm_l_y -= bounce + 5
            arm_r_y -= bounce + 5
            leg_l_y -= bounce
            leg_r_y -= bounce
            tail_angle = -15 + math.sin(t * 0.28) * 40

        elif state == "talk":
            mouth_type = "open" if math.sin(t * 0.28) > 0 else "line"
            head_y -= math.sin(t * 0.28) * 2

        elif state == "drag":
            body_ry += 8
            body_rx -= 3
            head_y -= 10
            arm_l_y -= 12
            arm_r_y -= 12
            leg_l_y += 10
            leg_r_y += 10
            eye_type = "wide"
            mouth_type = "open"
            tail_angle = 80

        elif state == "fall":
            body_ry += 5
            body_rx -= 2
            head_y -= 5
            arm_l_y -= 12
            arm_r_y -= 12
            eye_type = "wide"
            mouth_type = "open"
            tail_angle = 55
            leg_l_y -= 5
            leg_r_y -= 5

        elif state in ("roll_left", "roll_right"):
            look_dir = -1 if state == "roll_left" else 1
            # Squash into a tight ball
            head_y += 14
            body_ry -= 6
            body_rx += 6
            arm_l_y += 10
            arm_r_y += 10
            leg_l_y -= 12
            leg_r_y -= 12
            eye_type = "closed"
            mouth_type = "small"
            tail_angle = 90
            
        elif state == "stay_calm":
            # Just stand completely still and stare (override to sad mouth, wide/open eyes)
            eye_type = "wide"
            mouth_type = "sad"
            look_dir = 0.0
            # Remove breathing animations to make it eerie/calm
            pass

        # ── Panda colour palette ────────────────────────────────────────
        black     = QColor(35, 35, 40)
        white     = QColor(252, 252, 250)
        off_white = QColor(240, 238, 235)
        nose_col  = QColor(45, 42, 42)
        blush_col = QColor(255, 180, 190, 100)

        body_outline_pen = QPen(black, 2.5, Qt.PenStyle.SolidLine,
                                Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        limb_pen = QPen(QColor(25, 25, 28), 2.0, Qt.PenStyle.SolidLine,
                        Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

        # ── 0. Ground shadow ────────────────────────────────────────────
        painter.setPen(Qt.PenStyle.NoPen)
        sh_cy = body_y + body_ry + 8
        sh_grad = QRadialGradient(QPointF(cx, sh_cy), body_rx * 1.6)
        sh_grad.setColorAt(0.0, QColor(40, 35, 35, 55))
        sh_grad.setColorAt(1.0, QColor(40, 35, 35, 0))
        painter.setBrush(QBrush(sh_grad))
        painter.drawEllipse(QPointF(cx, sh_cy), body_rx * 1.3, body_ry * 0.35)

        # Apply whole-body rotation for rolling
        painter.save()
        if state in ("roll_left", "roll_right"):
            painter.translate(cx, cy)
            angle = (t * 12) % 360 if state == "roll_right" else (-t * 12) % 360
            painter.rotate(angle)
            painter.translate(-cx, -cy)

        # ── 1. Tiny stub tail ───────────────────────────────────────────
        painter.save()
        painter.translate(tail_x, tail_y)
        painter.rotate(tail_angle)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(white))
        painter.drawEllipse(QPointF(2, 4), 5, 4)
        painter.setPen(QPen(black, 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(2, 4), 5, 4)
        painter.restore()

        # ── 2. Back legs (behind body) ──────────────────────────────────
        painter.setPen(limb_pen)
        painter.setBrush(QBrush(black))
        painter.drawEllipse(QPointF(leg_l_x, leg_l_y), leg_rx, leg_ry)
        painter.drawEllipse(QPointF(leg_r_x, leg_r_y), leg_rx, leg_ry)
        # Paw pads
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(80, 75, 72)))
        painter.drawEllipse(QPointF(leg_l_x, leg_l_y + 2), 5, 3.5)
        painter.drawEllipse(QPointF(leg_r_x, leg_r_y + 2), 5, 3.5)

        # ── 3. Body (white torso) ───────────────────────────────────────
        body_grad = QLinearGradient(
            QPointF(body_x, body_y - body_ry),
            QPointF(body_x, body_y + body_ry),
        )
        body_grad.setColorAt(0.0, white)
        body_grad.setColorAt(1.0, off_white)
        painter.setPen(body_outline_pen)
        painter.setBrush(QBrush(body_grad))
        painter.drawEllipse(QPointF(body_x, body_y), body_rx, body_ry)

        # Belly patch (subtle lighter oval)
        painter.setPen(Qt.PenStyle.NoPen)
        belly_grad = QRadialGradient(QPointF(body_x, body_y + 2), body_rx * 0.7)
        belly_grad.setColorAt(0.0, QColor(255, 255, 255, 90))
        belly_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(belly_grad))
        painter.drawEllipse(QPointF(body_x, body_y + 2), body_rx * 0.65, body_ry * 0.7)

        # ── 4. Arms (black, in front of body) ──────────────────────────
        painter.setPen(limb_pen)
        painter.setBrush(QBrush(black))
        painter.drawEllipse(QPointF(arm_l_x, arm_l_y), arm_rx, arm_ry)
        painter.drawEllipse(QPointF(arm_r_x, arm_r_y), arm_rx, arm_ry)
        # Arm paw pads
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(80, 75, 72)))
        painter.drawEllipse(QPointF(arm_l_x, arm_l_y + 1), 4.5, 3)
        painter.drawEllipse(QPointF(arm_r_x, arm_r_y + 1), 4.5, 3)

        # ── 5. Head (white, drawn on top) ───────────────────────────────
        head_grad = QLinearGradient(
            QPointF(head_x, head_y - head_ry),
            QPointF(head_x, head_y + head_ry),
        )
        head_grad.setColorAt(0.0, white)
        head_grad.setColorAt(1.0, off_white)
        painter.setPen(body_outline_pen)
        painter.setBrush(QBrush(head_grad))
        painter.drawEllipse(QPointF(head_x, head_y), head_rx, head_ry)

        # ── 6. Ears (round black circles, drawn on top of head edge) ───
        painter.setPen(QPen(QColor(20, 20, 22), 2.0))
        painter.setBrush(QBrush(black))
        painter.drawEllipse(QPointF(ear_l_cx, ear_l_cy), ear_r_radius, ear_r_radius)
        painter.drawEllipse(QPointF(ear_r_cx, ear_r_cy), ear_r_radius, ear_r_radius)
        # Inner ear highlight
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(60, 58, 55)))
        painter.drawEllipse(QPointF(ear_l_cx, ear_l_cy), ear_r_radius * 0.55, ear_r_radius * 0.55)
        painter.drawEllipse(QPointF(ear_r_cx, ear_r_cy), ear_r_radius * 0.55, ear_r_radius * 0.55)

        # ── 7. Eye patches (smooth tilted ovals) ───────────────────────
        eye_y = head_y + 1
        eye_offset = 14
        patch_rx, patch_ry = 11, 9

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(black))
        # Left patch — rotated slightly outward
        painter.save()
        painter.translate(head_x - eye_offset, eye_y)
        painter.rotate(-12)
        painter.drawEllipse(QPointF(0, 0), patch_rx, patch_ry)
        painter.restore()
        # Right patch — mirrored rotation
        painter.save()
        painter.translate(head_x + eye_offset, eye_y)
        painter.rotate(12)
        painter.drawEllipse(QPointF(0, 0), patch_rx, patch_ry)
        painter.restore()

        # ── 8. Eyes ─────────────────────────────────────────────────────
        look_x = look_dir * 2.0

        if eye_type == "closed":
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(white, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(int(head_x - eye_offset - 5), int(eye_y), 10, 8, 0, -180 * 16)
            painter.drawArc(int(head_x + eye_offset - 5), int(eye_y), 10, 8, 0, -180 * 16)

        elif eye_type == "happy":
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(white, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(int(head_x - eye_offset - 5), int(eye_y - 2), 10, 8, 0, 180 * 16)
            painter.drawArc(int(head_x + eye_offset - 5), int(eye_y - 2), 10, 8, 0, 180 * 16)

        elif eye_type == "wide":
            self._draw_panda_eye(painter, head_x - eye_offset, eye_y, look_x, rx=6.0, ry=7.0)
            self._draw_panda_eye(painter, head_x + eye_offset, eye_y, look_x, rx=6.0, ry=7.0)
            
        elif eye_type == "sad":
            # Small droopy dots
            self._draw_panda_eye(painter, head_x - eye_offset, eye_y + 1, look_x, rx=3.0, ry=2.0)
            self._draw_panda_eye(painter, head_x + eye_offset, eye_y + 1, look_x, rx=3.0, ry=2.0)
            
        elif eye_type == "angry":
            # Angry slanted lines: \ /
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(white, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(head_x - eye_offset - 3), int(eye_y - 2), int(head_x - eye_offset + 3), int(eye_y + 2))
            painter.drawLine(int(head_x + eye_offset + 3), int(eye_y - 2), int(head_x + eye_offset - 3), int(eye_y + 2))

        else:  # open (default)
            self._draw_panda_eye(painter, head_x - eye_offset, eye_y, look_x)
            self._draw_panda_eye(painter, head_x + eye_offset, eye_y, look_x)

        # ── 9. Blush (subtle pink glow under each eye) ─────────────────
        painter.setPen(Qt.PenStyle.NoPen)
        for bx in (head_x - eye_offset, head_x + eye_offset):
            bg = QRadialGradient(QPointF(bx, eye_y + patch_ry - 1), 7)
            bg.setColorAt(0.0, blush_col)
            bg.setColorAt(1.0, QColor(255, 180, 190, 0))
            painter.setBrush(QBrush(bg))
            painter.drawEllipse(QPointF(bx, eye_y + patch_ry - 1), 7, 4)

        # ── 10. Nose (oval, not triangular) ─────────────────────────────
        nose_y = eye_y + 8
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(nose_col))
        painter.drawEllipse(QPointF(head_x, nose_y), 4, 2.8)
        # Tiny nose highlight
        painter.setBrush(QBrush(QColor(90, 85, 82)))
        painter.drawEllipse(QPointF(head_x - 1, nose_y - 0.8), 1.2, 0.7)

        # ── 11. Mouth ──────────────────────────────────────────────────
        mouth_y = nose_y + 3.5
        if mouth_type == "open":
            # Cute open mouth
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(200, 90, 100)))
            painter.drawEllipse(QPointF(head_x, mouth_y + 1), 4, 4.5)
            # Tongue
            painter.setBrush(QBrush(QColor(230, 130, 140)))
            painter.drawEllipse(QPointF(head_x, mouth_y + 3), 2.5, 2)
        elif mouth_type == "line":
            painter.setPen(QPen(nose_col, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawLine(int(head_x - 3), int(mouth_y), int(head_x + 3), int(mouth_y))
        elif mouth_type == "small":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(nose_col))
            painter.drawEllipse(QPointF(head_x, mouth_y), 1.5, 1.5)
        elif mouth_type == "sad":
            painter.setPen(QPen(nose_col, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawLine(int(head_x), int(nose_y + 2.8), int(head_x), int(mouth_y))
            # Upside down curve
            painter.drawArc(int(head_x - 3.5), int(mouth_y), 7, 4, 0, 180 * 16)
        else:  # "w" — default cute mouth
            painter.setPen(QPen(nose_col, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            # Nose-to-mouth line
            painter.drawLine(int(head_x), int(nose_y + 2.8), int(head_x), int(mouth_y))
            # Little "w"
            painter.drawArc(int(head_x - 5), int(mouth_y - 2), 5, 5, 0, -180 * 16)
            painter.drawArc(int(head_x), int(mouth_y - 2), 5, 5, 0, -180 * 16)

        # ── 12. Bamboo (eat = small leaf near mouth, sleep = full stick being hugged)
        if state == "eat":
            leaf_x = head_x
            leaf_y = mouth_y - 2
            painter.setPen(QPen(QColor(60, 120, 50), 1.5))
            painter.setBrush(QBrush(QColor(100, 180, 80)))
            leaf = QPainterPath()
            leaf.moveTo(leaf_x - 8, leaf_y)
            leaf.quadTo(leaf_x - 4, leaf_y - 6, leaf_x, leaf_y - 2)
            leaf.quadTo(leaf_x - 4, leaf_y + 2, leaf_x - 8, leaf_y)
            painter.drawPath(leaf)
            painter.setPen(QPen(QColor(80, 140, 60), 1.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(leaf_x - 8), int(leaf_y), int(leaf_x - 12), int(leaf_y + 4))

        if state == "sleep":
            # Bamboo stick the panda is hugging
            bamboo_col = QColor(90, 155, 70)
            bamboo_dark = QColor(65, 120, 50)
            bamboo_light = QColor(130, 190, 100)
            stick_cx = arm_l_x + 2
            stick_top = head_y - head_ry - 10
            stick_bot = leg_r_y + leg_ry + 4

            # Main stick (thick rounded line)
            painter.setPen(QPen(bamboo_dark, 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(stick_cx), int(stick_top), int(stick_cx), int(stick_bot))
            # Inner highlight stripe
            painter.setPen(QPen(bamboo_light, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(stick_cx - 1), int(stick_top + 2), int(stick_cx - 1), int(stick_bot - 2))

            # Bamboo nodes (little rings)
            painter.setPen(QPen(bamboo_dark, 1.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for ny in range(int(stick_top) + 12, int(stick_bot) - 5, 18):
                painter.drawLine(int(stick_cx - 3), ny, int(stick_cx + 3), ny)

            # Leaves sprouting from the top of the stick
            painter.setPen(QPen(QColor(55, 115, 45), 1.2))
            painter.setBrush(QBrush(QColor(95, 175, 75)))
            for angle, lx_off, ly_off in [(-35, -2, 4), (25, 3, 8), (-15, -4, 14)]:
                painter.save()
                painter.translate(stick_cx + lx_off, stick_top + ly_off)
                painter.rotate(angle)
                lf = QPainterPath()
                lf.moveTo(0, 0)
                lf.quadTo(4, -7, 10, -3)
                lf.quadTo(3, 2, 0, 0)
                painter.drawPath(lf)
                painter.restore()

        painter.restore() # End of whole-body rotation block

        # ── 13. Floating "zzz" during sleep ─────────────────────────────
        if state == "sleep":
            font = painter.font()
            font.setPointSize(9)
            font.setBold(True)
            painter.setFont(font)
            for i, ch in enumerate(("z", "z", "Z")):
                progress = ((t * 0.5) + i * 7) % 21
                alpha = max(0, 255 - int(progress * 11))
                painter.setPen(QColor(35, 35, 40, alpha))
                painter.drawText(
                    QPointF(head_x + 24 + progress * 1.2, head_y - 20 - progress * 1.2), ch
                )

    # ------------------------------------------------------------------
    # Mouse / interaction events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            if hasattr(self, "action_callback"):
                self.action_callback("drag_start")
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            if hasattr(self, "action_callback"):
                self.action_callback("drag_end")

    def show_context_menu(self, global_pos: QPoint):
        menu = QMenu(self)

        feed_action = menu.addAction("Feed 🎋")
        pet_action = menu.addAction("Pet 🐾")
        chat_action = menu.addAction("Chat 💬")
        stay_calm_action = menu.addAction("Stay calm 🛑")
        settings_action = menu.addAction("Settings ⚙")
        menu.addSeparator()
        quit_action = menu.addAction("Quit")

        action = menu.exec(global_pos)

        if action == quit_action:
            QApplication.quit()
        elif action == feed_action and hasattr(self, "action_callback"):
            self.action_callback("feed")
        elif action == pet_action and hasattr(self, "action_callback"):
            self.action_callback("pet")
        elif action == chat_action and hasattr(self, "action_callback"):
            self.action_callback("chat")
        elif action == stay_calm_action and hasattr(self, "action_callback"):
            self.action_callback("stay_calm")
        elif action == settings_action and hasattr(self, "action_callback"):
            self.action_callback("settings")

    def update_pet(self):
        self.repaint()

    def set_state(self, state_id: str):
        self.current_state_id = state_id