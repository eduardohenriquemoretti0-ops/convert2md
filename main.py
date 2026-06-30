"""Convert2MD — Android entry point (Kivy + native file picker + AdSense WebView banner)."""
import os
import sys
import threading
from pathlib import Path

os.environ['KIVY_NO_ENV_CONFIG'] = '1'
sys.path.insert(0, str(Path(__file__).parent))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.utils import platform
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

AD_H = dp(60)


def _start_flask():
    from web_app import app as _app
    _app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)


def _request_android_permissions():
    if platform == 'android':
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])


def _downloads_dir():
    if platform == 'android':
        try:
            from android.storage import primary_external_storage_path
            return os.path.join(primary_external_storage_path(), 'Download')
        except Exception:
            pass
    return str(Path.home() / 'Downloads')


class Header(BoxLayout):
    def __init__(self, **kw):
        super().__init__(size_hint_y=None, height=dp(60), padding=[dp(20), 0], **kw)
        with self.canvas.before:
            Color(99/255, 102/255, 241/255, 1)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync)
        lbl = Label(text='Convert2MD', font_size=dp(20), bold=True,
                    color=(1, 1, 1, 1), halign='left', valign='middle')
        lbl.bind(size=lambda l, s: setattr(l, 'text_size', s))
        self.add_widget(lbl)

    def _sync(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size


class AdBanner(Widget):
    """Embeds Android native WebView showing /ad (AdSense banner)."""

    def __init__(self, **kw):
        super().__init__(size_hint_y=None, height=AD_H, **kw)
        self._wv = None
        if platform == 'android':
            Clock.schedule_once(self._setup, 3)
        self.bind(pos=self._move, size=self._move)

    def _setup(self, _dt):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            WebView        = autoclass('android.webkit.WebView')
            WebViewClient  = autoclass('android.webkit.WebViewClient')
            LP             = autoclass('android.view.ViewGroup$LayoutParams')
            activity = PythonActivity.mActivity
            wv = WebView(activity)
            wv.getSettings().setJavaScriptEnabled(True)
            wv.getSettings().setDomStorageEnabled(True)
            wv.getSettings().setMediaPlaybackRequiresUserGesture(False)
            wv.setWebViewClient(WebViewClient())
            wv.loadUrl('http://127.0.0.1:5000/ad')
            activity.addContentView(wv, LP(-1, int(AD_H)))
            self._wv = wv
            self._move()
        except Exception:
            pass

    def _move(self, *_):
        if not self._wv:
            return
        try:
            from android.runnable import run_on_ui_thread
            wv = self._wv
            y_pos = int(Window.height - self.y - self.height)

            @run_on_ui_thread
            def _ui():
                wv.setX(int(self.x))
                wv.setY(y_pos)
        except Exception:
            pass


class Convert2MDApp(App):
    def build(self):
        Window.clearcolor = (240/255, 244/255, 255/255, 1)
        _request_android_permissions()
        threading.Thread(target=_start_flask, daemon=True).start()

        root = BoxLayout(orientation='vertical')
        root.add_widget(Header())

        self._sbox = BoxLayout(orientation='vertical', size_hint_y=None,
                               spacing=dp(8), padding=[dp(16), dp(12)])
        self._sbox.bind(minimum_height=self._sbox.setter('height'))
        sv = ScrollView()
        sv.add_widget(self._sbox)
        root.add_widget(sv)

        self._msg('Toque em "Selecionar" para converter um arquivo.',
                  (100/255, 116/255, 139/255, 1))

        btn_row = BoxLayout(size_hint_y=None, height=dp(72),
                            padding=[dp(16), dp(10)], spacing=dp(10))
        btn = Button(text='Selecionar arquivo',
                     background_color=(99/255, 102/255, 241/255, 1),
                     color=(1, 1, 1, 1), font_size=dp(15))
        btn.bind(on_press=self._pick)
        btn_row.add_widget(btn)
        root.add_widget(btn_row)

        root.add_widget(AdBanner())
        return root

    def _msg(self, text, color=None):
        lbl = Label(text=text,
                    color=color or (30/255, 41/255, 59/255, 1),
                    size_hint_y=None, height=dp(36),
                    halign='left', valign='middle')
        lbl.bind(size=lambda l, s: setattr(l, 'text_size', (s[0], None)))
        self._sbox.add_widget(lbl)
        return lbl

    def _pick(self, _btn):
        root_path = '/storage/emulated/0' if platform == 'android' else str(Path.home())
        fc = FileChooserListView(
            path=root_path,
            filters=['*.pdf', '*.docx', '*.xlsx', '*.html', '*.htm', '*.csv'],
        )
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(fc)
        ok = Button(text='Converter', size_hint_y=None, height=dp(56),
                    background_color=(99/255, 102/255, 241/255, 1), color=(1, 1, 1, 1))
        layout.add_widget(ok)
        popup = Popup(title='Selecionar arquivo', content=layout, size_hint=(0.95, 0.9))

        def _go(_):
            if fc.selection:
                popup.dismiss()
                self._convert(fc.selection[0])
        ok.bind(on_press=_go)
        popup.open()

    def _convert(self, src):
        lbl = self._msg(f'Convertendo {Path(src).name}…', (100/255, 116/255, 139/255, 1))

        def _worker():
            from convert2md import CONVERTERS, _clean
            p = Path(src)
            ext = p.suffix.lower()
            fn = CONVERTERS.get(ext)
            if not fn:
                Clock.schedule_once(lambda _: self._done(lbl, f'✗ Formato não suportado: {ext}', False))
                return
            try:
                md = _clean(fn(p))
            except Exception as e:
                Clock.schedule_once(lambda _: self._done(lbl, f'✗ {e}', False))
                return
            dl = Path(_downloads_dir())
            dl.mkdir(parents=True, exist_ok=True)
            dest = dl / (p.stem + '.md')
            dest.write_text(md, encoding='utf-8')
            Clock.schedule_once(lambda _: self._done(lbl, f'✓ Salvo: Downloads/{dest.name}', True))

        threading.Thread(target=_worker, daemon=True).start()

    def _done(self, lbl, text, ok):
        lbl.text = text
        lbl.color = (16/255, 185/255, 129/255, 1) if ok else (239/255, 68/255, 68/255, 1)


if __name__ == '__main__':
    Convert2MDApp().run()
