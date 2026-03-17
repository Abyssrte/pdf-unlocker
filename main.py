"""
PDF UNLOCKER - Kivy Android App
UI: Exact match to Expo preview screenshots
- Splash: dark bg, blue circle lock icon, PDF UNLOCKER title, tagline
- Main: hamburger + blue icon + title, doc icon center, Select PDF blue btn
- Menu: slide-down panel, icon+title, sun/moon slider, tap outside close
- Password: back arrow + blue icon + title, password field + eye, Unlock PDF btn
- Popups: slide-up from bottom, app icon in header
- Output: DDMMYYYY_HHMMSS.pdf in Downloads
- 100% original PDF quality
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.image import Image as KivyImage
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.graphics import (Color, RoundedRectangle, Rectangle, Ellipse, Line)
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from datetime import datetime
import threading
import os

try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    ANDROID = True
except ImportError:
    ANDROID = False

try:
    from pypdf import PdfReader, PdfWriter
    PDF_OK = True
    PDF_ERR = ""
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        PDF_OK = True
        PDF_ERR = ""
    except ImportError:
        PDF_OK = False
        PDF_ERR = "pypdf not installed!\nRun: pip install pypdf"

# ─── THEMES ──────────────────────────────────────────────────────────────────
DARK = {
    "bg":       "#0a0a0a",
    "card":     "#141414",
    "surface":  "#1e1e1e",
    "field":    "#1e1e1e",
    "text":     "#ffffff",
    "subtext":  "#888888",
    "hint":     "#555555",
    "accent":   "#1877F2",
    "success":  "#22c55e",
    "error":    "#ef4444",
    "warn":     "#f59e0b",
    "popup":    "#141414",
    "divider":  "#2a2a2a",
    "menu_bg":  "#1e1e1e",
    "icon_bg":  "#1877F2",
    "doc_icon": "#555555",
}
LIGHT = {
    "bg":       "#f8f8f8",
    "card":     "#ffffff",
    "surface":  "#f0f0f0",
    "field":    "#ebebeb",
    "text":     "#111111",
    "subtext":  "#666666",
    "hint":     "#aaaaaa",
    "accent":   "#1877F2",
    "success":  "#16a34a",
    "error":    "#dc2626",
    "warn":     "#d97706",
    "popup":    "#1a1a1a",
    "divider":  "#e0e0e0",
    "menu_bg":  "#ffffff",
    "icon_bg":  "#1877F2",
    "doc_icon": "#cccccc",
}

_th = {"v": DARK}
def T(k):  return get_color_from_hex(_th["v"][k])
def TH(k): return _th["v"][k]
def is_dark(): return _th["v"] is DARK

def get_output_dir():
    if ANDROID:
        p = os.path.join(primary_external_storage_path(), "Download")
    else:
        p = os.path.join(os.path.expanduser("~"), "Downloads")
    os.makedirs(p, exist_ok=True)
    return p

def make_out_name():
    return datetime.now().strftime("%d%m%Y_%H%M%S") + ".pdf"


# ─── BLUE CIRCLE LOCK ICON ───────────────────────────────────────────────────
class LockIcon(Widget):
    """Blue circle with white lock icon — exact match to screenshots."""
    def __init__(self, size_px=48, **kw):
        super().__init__(
            size_hint=(None, None),
            width=dp(size_px), height=dp(size_px), **kw
        )
        self._px = size_px
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        cx = x + w / 2
        cy = y + h / 2
        s  = min(w, h)

        with self.canvas:
            # Blue circle background
            Color(*get_color_from_hex("#1877F2"))
            Ellipse(pos=(x, y), size=(w, h))

            # White lock body (rounded rect)
            Color(1, 1, 1, 1)
            body_w = s * 0.44
            body_h = s * 0.36
            body_r = s * 0.07
            bx = cx - body_w / 2
            by = cy - s * 0.28
            RoundedRectangle(
                pos=(bx, by),
                size=(body_w, body_h),
                radius=[dp(body_r)]
            )

            # White shackle arc (open lock — shackle lifted on right)
            Color(1, 1, 1, 1)
            shackle_w = body_w * 0.62
            shackle_t = s * 0.075
            sx = cx - shackle_w / 2
            # Left vertical bar
            Rectangle(
                pos=(sx, by + body_h * 0.3),
                size=(shackle_t, s * 0.22)
            )
            # Top arc
            Line(
                ellipse=(
                    sx, by + body_h * 0.3,
                    shackle_w, shackle_w * 0.9,
                    180, 0
                ),
                width=shackle_t
            )
            # Right vertical bar — shorter (open lock)
            Rectangle(
                pos=(sx + shackle_w - shackle_t, by + body_h * 0.5),
                size=(shackle_t, s * 0.08)
            )

            # Keyhole dot on lock body
            Color(*get_color_from_hex("#1877F2"))
            kh_r = s * 0.07
            Ellipse(
                pos=(cx - kh_r, by + body_h * 0.38),
                size=(kh_r * 2, kh_r * 2)
            )


# ─── DOCUMENT ICON (center of main screen) ───────────────────────────────────
class DocIcon(Widget):
    """Grey document icon — matches 'No file selected' state in screenshot."""
    def __init__(self, size_px=80, selected=False, **kw):
        super().__init__(
            size_hint=(None, None),
            width=dp(size_px), height=dp(size_px), **kw
        )
        self._selected = selected
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        col = TH("accent") if self._selected else TH("doc_icon")

        with self.canvas:
            Color(*get_color_from_hex(col))
            fold = w * 0.28
            r    = dp(6)
            # Main body
            RoundedRectangle(
                pos=(x + w*0.12, y),
                size=(w * 0.76, h * 0.88),
                radius=[r]
            )
            # Fold triangle (white cut)
            Color(*T("bg"))
            # top-right fold
            fold_s = w * 0.26
            RoundedRectangle(
                pos=(x + w * 0.88 - fold_s, y + h * 0.88 - fold_s),
                size=(fold_s, fold_s),
                radius=[0, r, 0, 0]
            )


# ─── ROUNDED BUTTON ──────────────────────────────────────────────────────────
class RBtn(Button):
    def __init__(self, bg="#1877F2", fg="#ffffff", r=28, **kw):
        super().__init__(**kw)
        self._bg = bg; self._r = r
        self.background_color  = (0,0,0,0)
        self.background_normal = ""
        self.color     = get_color_from_hex(fg)
        self.bold      = True
        self.font_size = dp(16)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self._bg))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(self._r)])

    def recolor(self, h):
        self._bg = h; self._draw()


# ─── SUN/MOON PILL TOGGLE ────────────────────────────────────────────────────
class ThemeToggle(Widget):
    """
    Pill toggle: ☀️ left side, 🌙 right side.
    Knob slides. Exact match to screenshots.
    """
    TW = 72; TH_PX = 36

    def __init__(self, on_toggle=None, **kw):
        super().__init__(
            size_hint=(None, None),
            width=dp(self.TW), height=dp(self.TH_PX), **kw
        )
        self._on_toggle = on_toggle
        self._is_dark   = is_dark()
        self.bind(pos=self._draw, size=self._draw)

        # Invisible button over widget for tap
        self._btn = Button(
            size_hint=(None, None),
            width=dp(self.TW), height=dp(self.TH_PX),
            background_color=(0,0,0,0),
            background_normal=""
        )
        self._btn.bind(on_press=self._tapped)
        self._btn.bind(pos=lambda w,s: setattr(self._btn,"pos",self.pos))
        self.bind(pos=lambda w,s: setattr(self._btn,"pos",s))
        self.add_widget(self._btn)

    def _draw(self, *a):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        r    = h / 2

        track = "#333333" if self._is_dark else "#e0e0e0"
        knob  = "#2a2a2a" if self._is_dark else "#ffffff"

        with self.canvas:
            # Track
            Color(*get_color_from_hex(track))
            RoundedRectangle(pos=(x,y), size=(w,h), radius=[dp(r)])

            # Knob
            pad   = dp(3)
            kd    = h - pad * 2
            kx    = (x + w - pad - kd) if self._is_dark else (x + pad)
            ky    = y + pad

            # Shadow
            Color(0, 0, 0, 0.2)
            Ellipse(pos=(kx+dp(1), ky-dp(1)), size=(kd, kd))

            Color(*get_color_from_hex(knob))
            Ellipse(pos=(kx, ky), size=(kd, kd))

    def _tapped(self, *a):
        self._is_dark = not self._is_dark
        self._draw()
        if self._on_toggle:
            Clock.schedule_once(lambda dt: self._on_toggle(), 0.15)

    def sync(self):
        self._is_dark = is_dark()
        self._draw()


# ─── PASSWORD FIELD + EYE ────────────────────────────────────────────────────
class PasswordField(BoxLayout):
    def __init__(self, **kw):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None, height=dp(54), **kw
        )
        self._hidden = True

        with self.canvas.before:
            Color(*T("field"))
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(27)]
            )
        self.bind(pos=self._upd, size=self._upd)

        self._inp = TextInput(
            hint_text="Enter PDF Password",
            password=True, multiline=False,
            background_color=(0,0,0,0), background_normal="",
            foreground_color=T("text"),
            hint_text_color=T("hint"),
            cursor_color=T("accent"),
            font_size=sp(15),
            padding=[dp(22), dp(16)],
        )
        self.add_widget(self._inp)

        self._eye = Button(
            text="👁" + "\u0338" if True else "👁",
            font_size=sp(18),
            background_color=(0,0,0,0), background_normal="",
            color=T("subtext"),
            size_hint=(None,None), width=dp(52), height=dp(54)
        )
        # Use text symbols that match screenshot eye-slash icon
        self._eye.text = "◌"   # placeholder, updated below
        self._update_eye_icon()
        self._eye.bind(on_press=self._toggle)
        self.add_widget(self._eye)

    def _update_eye_icon(self):
        # Use simple text that looks like eye/eye-slash
        self._eye.text = "🙈" if self._hidden else "👁"
        self._eye.font_size = sp(16)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _toggle(self, *a):
        self._hidden = not self._hidden
        self._inp.password = self._hidden
        self._update_eye_icon()

    @property
    def text(self): return self._inp.text


# ─── HAMBURGER MENU (slides down from top) ───────────────────────────────────
class HamburgerMenu(FloatLayout):
    def __init__(self, layer, rebuild_fn, **kw):
        super().__init__(**kw)
        self._layer    = layer
        self._rebuild  = rebuild_fn
        self._panel    = None

    def open(self):
        panel = BoxLayout(
            orientation="vertical",
            padding=[dp(22), dp(20), dp(22), dp(20)],
            spacing=dp(16),
            size_hint=(1, None), height=dp(190),
            pos_hint={"x": 0, "top": 2}
        )

        with panel.canvas.before:
            Color(*T("menu_bg"))
            self._prect = RoundedRectangle(
                pos=panel.pos, size=panel.size,
                radius=[0, 0, dp(24), dp(24)]
            )
        panel.bind(
            pos=lambda w,s: setattr(self._prect,"pos",s),
            size=lambda w,s: setattr(self._prect,"size",s)
        )

        # Dim overlay
        with self.canvas.before:
            Color(0, 0, 0, 0.45)
            self._orect = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda w,s: setattr(self._orect,"pos",s),
            size=lambda w,s: setattr(self._orect,"size",s)
        )

        # ── Icon + App name row ──
        row1 = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(16))
        row1.add_widget(LockIcon(size_px=44))
        name_box = BoxLayout(orientation="vertical")
        nl = Label(
            text="[b]PDF Unlocker[/b]", markup=True,
            font_size=sp(16), color=T("text"),
            halign="left", valign="bottom"
        )
        nl.bind(size=lambda w,s: setattr(w,"text_size",s))
        sl = Label(
            text="Settings", font_size=sp(12),
            color=T("subtext"), halign="left", valign="top"
        )
        sl.bind(size=lambda w,s: setattr(w,"text_size",s))
        name_box.add_widget(nl)
        name_box.add_widget(sl)
        row1.add_widget(name_box)
        panel.add_widget(row1)

        # Divider
        div = Widget(size_hint_y=None, height=dp(1))
        with div.canvas:
            Color(*T("divider"))
            Rectangle(pos=div.pos, size=div.size)
        div.bind(pos=lambda w,s: (w.canvas.clear(),
                 w.canvas.add(Color(*T("divider"))),
                 w.canvas.add(Rectangle(pos=s, size=w.size))))
        panel.add_widget(div)

        # ── Theme toggle row ──
        row2 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))

        sun_lbl = Label(
            text="☀️  Light", font_size=sp(13), color=T("text"),
            size_hint_x=None, width=dp(80), halign="left"
        )
        sun_lbl.bind(size=lambda w,s: setattr(w,"text_size",s))
        row2.add_widget(sun_lbl)

        self._toggle_widget = ThemeToggle(on_toggle=self._do_toggle)
        row2.add_widget(self._toggle_widget)

        moon_lbl = Label(
            text="Dark  🌙", font_size=sp(13), color=T("text"),
            size_hint_x=None, width=dp(80), halign="right"
        )
        moon_lbl.bind(size=lambda w,s: setattr(w,"text_size",s))
        row2.add_widget(moon_lbl)

        panel.add_widget(row2)

        # Close hint
        cl = Label(
            text="Tap outside to close",
            font_size=sp(11), color=T("subtext"),
            size_hint_y=None, height=dp(20)
        )
        panel.add_widget(cl)

        # Tap outside to close
        overlay_btn = Button(
            size_hint=(1, 1),
            background_color=(0,0,0,0), background_normal=""
        )
        overlay_btn.bind(on_press=self.close)
        self.add_widget(overlay_btn)

        self._panel = panel
        self.add_widget(panel)
        Animation(pos_hint={"x":0,"top":1}, duration=0.3, t="out_cubic").start(panel)

    def _do_toggle(self):
        _th["v"] = LIGHT if is_dark() else DARK
        self._toggle_widget.sync()
        Clock.schedule_once(lambda dt: (self.close(), self._rebuild()), 0.2)

    def close(self, *a):
        if not self._panel: return
        p = self._panel
        def _rm(*_):
            if p in self.children:            self.remove_widget(p)
            if self in self._layer.children:  self._layer.remove_widget(self)
        Animation(pos_hint={"x":0,"top":2}, duration=0.22, t="in_cubic"
                  ).bind(on_complete=_rm).start(p)
        self._panel = None


def open_menu(layer, rebuild_fn):
    hm = HamburgerMenu(layer, rebuild_fn,
                       size_hint=(1,1), pos_hint={"x":0,"y":0})
    layer.add_widget(hm)
    hm.open()


# ─── GAME POPUP (bottom slide-up) ────────────────────────────────────────────
class GamePopup(FloatLayout):
    def __init__(self, layer, **kw):
        super().__init__(**kw)
        self._layer = layer
        self._panel = None

    def show(self, title, msg, kind="info", on_ok=None):
        self._on_ok    = on_ok
        self._pass_fld = None

        COLORS = {
            "success": "#22c55e", "error": "#ef4444",
            "warn": "#f59e0b",    "info":  "#1877F2", "input": "#1877F2"
        }
        ICONS  = {
            "success": "✅", "error": "❌",
            "warn": "⚠️",   "info":  "ℹ️", "input": "🔐"
        }
        acc      = COLORS.get(kind, "#1877F2")
        kind_ico = ICONS.get(kind, "ℹ️")

        ph = dp(290) if kind == "input" else dp(210)

        panel = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(20), dp(24), dp(22)],
            spacing=dp(14),
            size_hint=(1, None), height=ph,
            pos_hint={"x":0, "y":-1}
        )

        # Overlay
        with self.canvas.before:
            Color(0, 0, 0, 0.55)
            self._orect = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda w,s: setattr(self._orect,"pos",s),
            size=lambda w,s: setattr(self._orect,"size",s)
        )

        # Panel bg
        with panel.canvas.before:
            Color(*get_color_from_hex(TH("popup")))
            self._prect = RoundedRectangle(
                pos=panel.pos, size=panel.size,
                radius=[dp(28), dp(28), 0, 0]
            )
        panel.bind(
            pos=lambda w,s: setattr(self._prect,"pos",s),
            size=lambda w,s: setattr(self._prect,"size",s)
        )

        # ── Header: lock icon + title + "PDF Unlocker" ──
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(14))
        header.add_widget(LockIcon(size_px=40))

        title_col = BoxLayout(orientation="vertical")
        tl = Label(
            text=f"[b]{kind_ico}  {title}[/b]", markup=True,
            font_size=sp(15), color=get_color_from_hex(acc),
            halign="left", valign="bottom"
        )
        tl.bind(size=lambda w,s: setattr(w,"text_size",s))
        app_lbl = Label(
            text="PDF Unlocker", font_size=sp(10),
            color=get_color_from_hex("#666666"),
            halign="left", valign="top"
        )
        app_lbl.bind(size=lambda w,s: setattr(w,"text_size",s))
        title_col.add_widget(tl)
        title_col.add_widget(app_lbl)
        header.add_widget(title_col)
        panel.add_widget(header)

        # Message
        ml = Label(
            text=msg, font_size=sp(13), color=T("text"),
            size_hint_y=None, height=dp(44),
            halign="left", valign="top"
        )
        ml.bind(size=lambda w,s: setattr(w,"text_size",s))
        panel.add_widget(ml)

        # Password input (only for 'input' kind)
        if kind == "input":
            self._pass_fld = PasswordField()
            panel.add_widget(self._pass_fld)

        # Button
        btn_txt = "Unlock PDF" if kind == "input" else "OK"
        ok_btn = RBtn(
            text=btn_txt, bg=acc, fg="#ffffff", r=28,
            size_hint_y=None, height=dp(52)
        )
        ok_btn.bind(on_press=self._ok)
        panel.add_widget(ok_btn)

        self._panel = panel
        self.add_widget(panel)
        Animation(pos_hint={"x":0,"y":0}, duration=0.3, t="out_cubic").start(panel)

    def _ok(self, *a):
        pwd = self._pass_fld.text if self._pass_fld else ""
        cb  = self._on_ok
        self.dismiss()
        if cb: cb(pwd)

    def dismiss(self, *a):
        if not self._panel: return
        p = self._panel
        def _rm(*_):
            if p in self.children:           self.remove_widget(p)
            if self in self._layer.children: self._layer.remove_widget(self)
        anim = Animation(pos_hint={"x":0,"y":-1}, duration=0.22, t="in_cubic")
        anim.bind(on_complete=_rm)
        anim.start(p)
        self._panel = None


def show_popup(layer, title, msg, kind="info", on_ok=None):
    gp = GamePopup(layer, size_hint=(1,1), pos_hint={"x":0,"y":0})
    layer.add_widget(gp)
    gp.show(title, msg, kind, on_ok)


# ─── TOPBAR BUILDER ──────────────────────────────────────────────────────────
def build_topbar(pop_layer, rebuild_fn, show_back=False, back_fn=None):
    top = BoxLayout(
        size_hint=(1, None), height=dp(58),
        pos_hint={"x":0, "top":1},
        padding=[dp(6), dp(8), dp(16), dp(8)],
        spacing=dp(10)
    )
    with top.canvas.before:
        Color(*T("card"))
        r = Rectangle(pos=top.pos, size=top.size)
    top.bind(
        pos=lambda w,s: setattr(r,"pos",s),
        size=lambda w,s: setattr(r,"size",s)
    )

    if show_back:
        left = Button(
            text="←", font_size=sp(24), bold=True,
            color=T("text"), background_color=(0,0,0,0),
            background_normal="",
            size_hint=(None,None), width=dp(44), height=dp(44)
        )
        if back_fn: left.bind(on_press=back_fn)
    else:
        left = Button(
            text="≡", font_size=sp(28), bold=False,
            color=T("text"), background_color=(0,0,0,0),
            background_normal="",
            size_hint=(None,None), width=dp(44), height=dp(44)
        )
        left.bind(on_press=lambda *a: open_menu(pop_layer, rebuild_fn))

    top.add_widget(left)
    top.add_widget(LockIcon(size_px=34))

    title_lbl = Label(
        text="[b]Unlock PDF[/b]", markup=True,
        font_size=sp(18), color=T("text"),
        halign="left", valign="middle",
        padding_x=dp(6)
    )
    title_lbl.bind(size=lambda w,s: setattr(w,"text_size",s))
    top.add_widget(title_lbl)

    return top


# ─── SPLASH SCREEN ───────────────────────────────────────────────────────────
class SplashScreen(Screen):
    def on_enter(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*T("bg"))
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda w,s: setattr(self._bg,"pos",s),
            size=lambda w,s: setattr(self._bg,"size",s)
        )

        lay = FloatLayout()

        # Center box
        box = BoxLayout(
            orientation="vertical", spacing=dp(18),
            size_hint=(None,None), width=dp(200), height=dp(180),
            pos_hint={"center_x":0.5, "center_y":0.52}
        )

        # Lock icon centered
        icon_row = BoxLayout(size_hint_y=None, height=dp(96))
        icon_row.add_widget(Widget())
        self._ico = LockIcon(size_px=84, opacity=0)
        icon_row.add_widget(self._ico)
        icon_row.add_widget(Widget())
        box.add_widget(icon_row)

        self._ttl = Label(
            text="[b]PDF UNLOCKER[/b]", markup=True,
            font_size=sp(26), color=T("accent"),
            size_hint_y=None, height=dp(38),
            opacity=0
        )
        box.add_widget(self._ttl)

        lay.add_widget(box)

        # Tagline at bottom
        self._tag = Label(
            text="Remove password · Keep original quality",
            font_size=sp(12), color=T("subtext"),
            size_hint=(1, None), height=dp(22),
            pos_hint={"center_x":0.5, "y":0.1},
            opacity=0
        )
        lay.add_widget(self._tag)
        self.add_widget(lay)

        Clock.schedule_once(self._anim, 0.1)

    def _anim(self, dt):
        Animation(opacity=1, duration=0.5).start(self._ico)
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.5).start(self._ttl), 0.3)
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.5).start(self._tag), 0.55)
        Clock.schedule_once(self._go, 2.5)

    def _go(self, dt):
        self.manager.current = "main"


# ─── MAIN SCREEN ─────────────────────────────────────────────────────────────
class MainScreen(Screen):
    def on_enter(self):
        self._pdf = getattr(self, "_pdf", "")
        self._build()

    def _build(self):
        self.clear_widgets()
        root = FloatLayout()

        with root.canvas.before:
            Color(*T("bg"))
            self._bgrect = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda w,s: setattr(self._bgrect,"pos",s),
            size=lambda w,s: setattr(self._bgrect,"size",s)
        )

        self._pop_layer = FloatLayout(size_hint=(1,1), pos_hint={"x":0,"y":0})

        # Topbar
        root.add_widget(build_topbar(self._pop_layer, self._build))

        # ── Center content ────────────────────────────────────────────────────
        center = FloatLayout(
            size_hint=(1,1)
        )

        # Document icon
        self._doc_row = BoxLayout(
            orientation="vertical", spacing=dp(14),
            size_hint=(None,None), width=dp(200), height=dp(130),
            pos_hint={"center_x":0.5, "center_y":0.55}
        )

        icon_row2 = BoxLayout(size_hint_y=None, height=dp(80))
        icon_row2.add_widget(Widget())
        self._doc_icon = DocIcon(size_px=70, selected=bool(self._pdf))
        icon_row2.add_widget(self._doc_icon)
        icon_row2.add_widget(Widget())
        self._doc_row.add_widget(icon_row2)

        self._st_lbl = Label(
            text=os.path.basename(self._pdf) if self._pdf else "No file selected",
            font_size=sp(14),
            color=T("text") if self._pdf else T("subtext"),
            size_hint_y=None, height=dp(28),
            halign="center"
        )
        self._st_lbl.bind(size=lambda w,s: setattr(w,"text_size",(s[0],None)))
        self._doc_row.add_widget(self._st_lbl)

        center.add_widget(self._doc_row)

        # File size label
        self._fl_lbl = Label(
            text=f"{os.path.getsize(self._pdf)/1024:.0f} KB  ·  PDF Document" if self._pdf else "",
            font_size=sp(11), color=T("subtext"),
            size_hint=(1,None), height=dp(20),
            pos_hint={"x":0, "center_y":0.36},
            halign="center"
        )
        self._fl_lbl.bind(size=lambda w,s: setattr(w,"text_size",(s[0],None)))
        center.add_widget(self._fl_lbl)

        # Output label
        self._out_lbl = Label(
            text=getattr(self,"_out_name",""),
            font_size=sp(11), color=T("success"),
            size_hint=(1,None), height=dp(20),
            pos_hint={"x":0, "center_y":0.3},
            halign="center"
        )
        self._out_lbl.bind(size=lambda w,s: setattr(w,"text_size",(s[0],None)))
        center.add_widget(self._out_lbl)

        root.add_widget(center)

        # ── Bottom buttons ─────────────────────────────────────────────────────
        bot = BoxLayout(
            orientation="vertical", spacing=dp(12),
            padding=[dp(22), 0, dp(22), dp(36)],
            size_hint=(1,None), height=dp(self._pdf and 142 or 90),
            pos_hint={"x":0,"y":0}
        )

        if self._pdf:
            self._unlock_btn = RBtn(
                text="Unlock PDF",
                bg=TH("accent"), fg="#ffffff", r=28,
                size_hint=(1,None), height=dp(54)
            )
            self._unlock_btn.bind(on_press=self._go_pass)
            bot.add_widget(self._unlock_btn)

        self._sel_btn = RBtn(
            text="Select PDF",
            bg=TH("accent"), fg="#ffffff", r=28,
            size_hint=(1,None), height=dp(54)
        )
        self._sel_btn.bind(on_press=self._open_fc)
        bot.add_widget(self._sel_btn)

        root.add_widget(bot)
        root.add_widget(self._pop_layer)
        self.add_widget(root)

        if ANDROID:
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

    def _open_fc(self, *a):
        start = primary_external_storage_path() if ANDROID else os.path.expanduser("~")

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        with content.canvas.before:
            Color(*T("bg"))
            br = Rectangle(pos=content.pos, size=content.size)
        content.bind(
            pos=lambda w,s: setattr(br,"pos",s),
            size=lambda w,s: setattr(br,"size",s)
        )

        fc = FileChooserListView(
            path=start, filters=["*.pdf","*.PDF"],
            background_color=T("surface"), foreground_color=T("text")
        )
        content.add_widget(fc)

        row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        cbtn = RBtn(text="Cancel",     bg=TH("surface"), fg=TH("text"),  r=24, size_hint_x=0.38)
        sbtn = RBtn(text="✅  Select",  bg=TH("accent"),  fg="#ffffff",   r=24, size_hint_x=0.62)
        row.add_widget(cbtn); row.add_widget(sbtn)
        content.add_widget(row)

        pop = Popup(
            title="Select PDF File", content=content,
            size_hint=(0.96, 0.88),
            background_color=T("card"),
            title_color=T("text"),
            separator_color=T("accent")
        )
        def on_sel(*_):
            if fc.selection:
                self._pdf = fc.selection[0]
                self._out_name = ""
                self._build()
            pop.dismiss()

        sbtn.bind(on_press=on_sel)
        cbtn.bind(on_press=pop.dismiss)
        pop.open()

    def _go_pass(self, *a):
        if not PDF_OK:
            show_popup(self._pop_layer, "Library Missing", PDF_ERR, "error"); return
        ps = self.manager.get_screen("password")
        ps.set_file(self._pdf, self)
        self.manager.current = "password"

    def set_result(self, name):
        self._out_name = f"✅ Saved: {name}"
        self._build()


# ─── PASSWORD SCREEN ─────────────────────────────────────────────────────────
class PasswordScreen(Screen):
    def set_file(self, path, main_ref):
        self._pdf  = path
        self._main = main_ref

    def on_enter(self):
        self._build()

    def _build(self):
        self.clear_widgets()
        root = FloatLayout()

        with root.canvas.before:
            Color(*T("bg"))
            self._bgrect = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda w,s: setattr(self._bgrect,"pos",s),
            size=lambda w,s: setattr(self._bgrect,"size",s)
        )

        self._pop_layer = FloatLayout(size_hint=(1,1), pos_hint={"x":0,"y":0})

        # Topbar with back
        root.add_widget(build_topbar(
            self._pop_layer, self._build,
            show_back=True, back_fn=self._go_back
        ))

        # ── Center: password + button ─────────────────────────────────────────
        mid = BoxLayout(
            orientation="vertical", spacing=dp(16),
            padding=[dp(22), 0],
            size_hint=(1,None), height=dp(132),
            pos_hint={"x":0, "center_y":0.46}
        )

        self._pass_fld = PasswordField()
        mid.add_widget(self._pass_fld)

        self._unlock_btn = RBtn(
            text="Unlock PDF",
            bg=TH("accent"), fg="#ffffff", r=28,
            size_hint=(1,None), height=dp(56)
        )
        self._unlock_btn.bind(on_press=self._do_unlock)
        mid.add_widget(self._unlock_btn)

        root.add_widget(mid)

        # Status
        self._st = Label(
            text="", font_size=sp(12), color=T("subtext"),
            size_hint=(1,None), height=dp(24),
            pos_hint={"x":0,"y":0.05}, halign="center"
        )
        self._st.bind(size=lambda w,s: setattr(w,"text_size",(s[0],None)))
        root.add_widget(self._st)

        root.add_widget(self._pop_layer)
        self.add_widget(root)

    def _go_back(self, *a):
        self.manager.current = "main"

    def _do_unlock(self, *a):
        pwd = self._pass_fld.text
        self._unlock_btn.disabled = True
        self._unlock_btn.text = "Processing..."
        self._st.text  = "⏳ Unlocking PDF, please wait..."
        self._st.color = T("warn")
        threading.Thread(target=self._process, args=(self._pdf, pwd), daemon=True).start()

    def _process(self, inp, pwd):
        try:
            reader = PdfReader(inp)
            if reader.is_encrypted:
                res = reader.decrypt(pwd if pwd else "")
                if res == 0:
                    Clock.schedule_once(lambda dt: self._fail(
                        "Wrong Password",
                        "The password you entered is incorrect.\nPlease try again."
                    ), 0)
                    return

            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            try:
                if reader.metadata: writer.add_metadata(reader.metadata)
            except Exception: pass

            out = os.path.join(get_output_dir(), make_out_name())
            with open(out, "wb") as f:
                writer.write(f)

            Clock.schedule_once(lambda dt: self._success(out), 0)

        except Exception as e:
            err = str(e)
            Clock.schedule_once(lambda dt: self._fail("Error", err), 0)

    def _success(self, out):
        self._unlock_btn.disabled = False
        self._unlock_btn.text = "Unlock PDF"
        self._st.text  = f"✅ Saved: {os.path.basename(out)}"
        self._st.color = T("success")
        if hasattr(self, "_main") and self._main:
            self._main.set_result(os.path.basename(out))
        show_popup(
            self._pop_layer,
            "PDF Unlocked! 🎉",
            f"Saved to Downloads:\n{os.path.basename(out)}",
            "success",
            on_ok=lambda *_: setattr(self.manager, "current", "main")
        )

    def _fail(self, title, msg):
        self._unlock_btn.disabled = False
        self._unlock_btn.text = "Unlock PDF"
        self._st.text  = "❌ Failed!"
        self._st.color = T("error")
        show_popup(self._pop_layer, title, msg, "error")


# ─── APP ─────────────────────────────────────────────────────────────────────
class PDFUnlockerApp(App):
    def build(self):
        self.title = "PDF Unlocker"
        sm = ScreenManager(transition=FadeTransition(duration=0.25))
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(PasswordScreen(name="password"))
        return sm


if __name__ == "__main__":
    PDFUnlockerApp().run()
