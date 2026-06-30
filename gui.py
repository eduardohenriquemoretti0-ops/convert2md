#!/usr/bin/env python3
"""Convert2MD — Desktop GUI app, ilovepdf-style."""
import sys
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QFrame, QScrollArea,
    QProgressBar, QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap

# ── colours ────────────────────────────────────────────────────────────────
C_BG      = "#F0F4FF"
C_CARD    = "#FFFFFF"
C_PRIMARY = "#6366F1"
C_PRIM2   = "#818CF8"
C_SUCCESS = "#10B981"
C_ERROR   = "#EF4444"
C_TEXT    = "#1E293B"
C_MUTED   = "#64748B"
C_BORDER  = "#E2E8F0"
C_DROP_BG = "#EEF2FF"

EXT_COLOR = {
    ".pdf":  ("#EF4444", "PDF"),
    ".docx": ("#2563EB", "DOCX"),
    ".xlsx": ("#16A34A", "XLSX"),
    ".pptx": ("#EA580C", "PPTX"),
    ".html": ("#D97706", "HTML"),
    ".htm":  ("#D97706", "HTML"),
    ".csv":  ("#7C3AED", "CSV"),
}

STYLESHEET = f"""
QMainWindow, QWidget#root {{ background: {C_BG}; }}
QLabel {{ color: {C_TEXT}; background: transparent; }}
QPushButton#btnConvert {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {C_PRIMARY}, stop:1 {C_PRIM2});
    color: white; border: none; border-radius: 14px;
    font-size: 16px; font-weight: bold; padding: 16px 48px;
}}
QPushButton#btnConvert:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #4F46E5, stop:1 {C_PRIMARY});
}}
QPushButton#btnConvert:disabled {{ background: {C_BORDER}; color: {C_MUTED}; }}
QPushButton#btnMore {{
    background: transparent; color: {C_PRIMARY};
    border: 2px solid {C_PRIMARY}; border-radius: 10px;
    font-size: 14px; font-weight: bold; padding: 10px 32px;
}}
QPushButton#btnMore:hover {{ background: {C_DROP_BG}; }}
QPushButton#btnOpen {{
    background: {C_SUCCESS}; color: white; border: none;
    border-radius: 8px; font-size: 12px; font-weight: bold; padding: 6px 16px;
}}
QPushButton#btnOpen:hover {{ background: #059669; }}
QPushButton#btnCopy {{
    background: transparent; color: {C_PRIMARY};
    border: 1.5px solid {C_PRIMARY}; border-radius: 8px;
    font-size: 12px; padding: 6px 14px;
}}
QPushButton#btnCopy:hover {{ background: {C_DROP_BG}; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{
    background: {C_BG}; width: 6px; border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {C_BORDER}; border-radius: 3px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QProgressBar {{
    border: none; border-radius: 3px; background: {C_BORDER}; height: 6px;
}}
QProgressBar::chunk {{
    border-radius: 3px;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {C_PRIMARY}, stop:1 {C_PRIM2});
}}
"""


def _shadow(widget, blur=16, dy=3, color="#00000018"):
    eff = QGraphicsDropShadowEffect()
    eff.setBlurRadius(blur)
    eff.setOffset(0, dy)
    eff.setColor(QColor(color))
    widget.setGraphicsEffect(eff)


class ExtBadge(QLabel):
    def __init__(self, ext: str, parent=None):
        super().__init__(parent)
        color, label = EXT_COLOR.get(ext, (C_MUTED, ext.upper().lstrip(".")))
        self.setText(label)
        self.setFixedSize(52, 24)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            background: {color}22; color: {color};
            border: 1.5px solid {color}55;
            border-radius: 6px; font-size: 11px; font-weight: bold;
        """)


class DropZone(QFrame):
    files_dropped = pyqtSignal(list)
    clicked_pick  = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dz")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._style(False)

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(10)

        ico = QLabel("📄")
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setStyleSheet("font-size: 64px;")

        title = QLabel("Arraste arquivos aqui")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {C_TEXT};")

        sub = QLabel("ou clique para selecionar")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"font-size: 14px; color: {C_MUTED};")

        badges = QWidget()
        badges.setStyleSheet("background: transparent;")
        blay = QHBoxLayout(badges)
        blay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        blay.setSpacing(6)
        for ext in [".pdf", ".docx", ".xlsx", ".pptx", ".html", ".csv"]:
            blay.addWidget(ExtBadge(ext))

        lay.addWidget(ico)
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addSpacing(8)
        lay.addWidget(badges)

    def _style(self, hover: bool):
        bg = "#DDE8FF" if hover else C_DROP_BG
        self.setStyleSheet(f"""
            QFrame#dz {{
                background: {bg};
                border: 2.5px dashed {C_PRIMARY};
                border-radius: 20px;
            }}
        """)

    def mousePressEvent(self, _e): self.clicked_pick.emit()
    def enterEvent(self, _e):       self._style(True)
    def leaveEvent(self, _e):       self._style(False)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._style(True)

    def dragLeaveEvent(self, _e): self._style(False)

    def dropEvent(self, e):
        self._style(False)
        paths = [u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
        if paths:
            self.files_dropped.emit(paths)


class ConvertWorker(QThread):
    progress = pyqtSignal(str, int)
    done     = pyqtSignal(str, str)
    error    = pyqtSignal(str, str)

    def __init__(self, paths: list[str]):
        super().__init__()
        self.paths = paths

    def run(self):
        sys.path.insert(0, str(Path(__file__).parent))
        from convert2md import CONVERTERS, _clean  # type: ignore

        for src in self.paths:
            p   = Path(src)
            ext = p.suffix.lower()
            fn  = CONVERTERS.get(ext)
            if fn is None:
                self.error.emit(src, f"Formato não suportado: {ext}")
                continue
            self.progress.emit(src, 30)
            try:
                md = _clean(fn(p))
            except Exception as exc:
                self.error.emit(src, str(exc))
                continue
            self.progress.emit(src, 80)
            dest = p.parent / (p.stem + ".md")
            dest.write_text(md, encoding="utf-8")
            self.progress.emit(src, 100)
            self.done.emit(src, str(dest))


class FileCard(QFrame):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.src_path  = path
        self.dest_path = ""
        p   = Path(path)
        ext = p.suffix.lower()

        self.setStyleSheet(f"""
            QFrame {{
                background: {C_CARD};
                border-radius: 14px;
                border: 1.5px solid {C_BORDER};
            }}
        """)
        self.setFixedHeight(88)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        _shadow(self, 12, 2)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(14)

        badge = ExtBadge(ext)
        badge.setFixedSize(52, 32)
        lay.addWidget(badge)

        col = QVBoxLayout()
        col.setSpacing(4)
        self._name = QLabel(p.name)
        self._name.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {C_TEXT};")
        self._status = QLabel("Aguardando…")
        self._status.setStyleSheet(f"font-size: 11px; color: {C_MUTED};")
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedHeight(6)
        self._bar.setTextVisible(False)
        col.addWidget(self._name)
        col.addWidget(self._status)
        col.addWidget(self._bar)
        lay.addLayout(col, stretch=1)

        self._btn_open = QPushButton("Abrir")
        self._btn_open.setObjectName("btnOpen")
        self._btn_open.setFixedWidth(72)
        self._btn_open.hide()
        self._btn_open.clicked.connect(self._open)

        self._btn_copy = QPushButton("Copiar MD")
        self._btn_copy.setObjectName("btnCopy")
        self._btn_copy.setFixedWidth(90)
        self._btn_copy.hide()
        self._btn_copy.clicked.connect(self._copy)

        lay.addWidget(self._btn_open)
        lay.addWidget(self._btn_copy)

    def set_progress(self, v: int):
        self._bar.setValue(v)
        self._status.setText(f"Convertendo… {v}%")

    def set_done(self, dest: str):
        self.dest_path = dest
        self._bar.setValue(100)
        self._bar.setStyleSheet(f"QProgressBar::chunk {{ background: {C_SUCCESS}; border-radius: 3px; }}")
        self._status.setText(f"✓  {Path(dest).name}")
        self._status.setStyleSheet(f"font-size: 11px; color: {C_SUCCESS};")
        self._btn_open.show()
        self._btn_copy.show()

    def set_error(self, msg: str):
        self._bar.setValue(100)
        self._bar.setStyleSheet(f"QProgressBar::chunk {{ background: {C_ERROR}; border-radius: 3px; }}")
        self._status.setText(f"✗  {msg}")
        self._status.setStyleSheet(f"font-size: 11px; color: {C_ERROR};")

    def _open(self):
        if self.dest_path:
            subprocess.Popen(["xdg-open", self.dest_path])

    def _copy(self):
        if self.dest_path:
            QApplication.clipboard().setText(Path(self.dest_path).read_text(encoding="utf-8"))
            self._btn_copy.setText("Copiado!")
            QTimer.singleShot(2000, lambda: self._btn_copy.setText("Copiar MD"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Convert2MD")
        self.setMinimumSize(720, 600)
        self.resize(860, 720)
        logo_path = Path(__file__).parent / "logo.png"
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))
        self._cards: dict[str, FileCard] = {}
        self._worker: ConvertWorker | None = None
        self._build()

    def _build(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # header
        hdr = QFrame()
        hdr.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C_PRIMARY}, stop:1 {C_PRIM2});
            }}
        """)
        hdr.setFixedHeight(68)
        hlay = QHBoxLayout(hdr)
        hlay.setContentsMargins(20, 0, 32, 0)

        logo_img = QLabel()
        logo_path = Path(__file__).parent / "logo.png"
        if logo_path.exists():
            pix = QPixmap(str(logo_path)).scaled(
                44, 44,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_img.setPixmap(pix)
        logo_img.setFixedSize(48, 48)

        logo_txt = QLabel("Convert2MD")
        logo_txt.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")

        tag = QLabel("PDF · DOCX · XLSX · PPTX · HTML · CSV  →  Markdown")
        tag.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 13px;")

        hlay.addWidget(logo_img)
        hlay.addSpacing(8)
        hlay.addWidget(logo_txt)
        hlay.addStretch()
        hlay.addWidget(tag)
        main.addWidget(hdr)

        # scroll body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body_w = QWidget()
        body_w.setStyleSheet(f"background: {C_BG};")
        body   = QVBoxLayout(body_w)
        body.setContentsMargins(40, 36, 40, 36)
        body.setSpacing(24)

        self._drop = DropZone()
        self._drop.files_dropped.connect(self._on_files)
        self._drop.clicked_pick.connect(self._pick)
        _shadow(self._drop, 20, 6, "#6366F130")
        body.addWidget(self._drop)

        self._list_w = QWidget()
        self._list_w.setStyleSheet("background: transparent;")
        self._list_lay = QVBoxLayout(self._list_w)
        self._list_lay.setContentsMargins(0, 0, 0, 0)
        self._list_lay.setSpacing(10)
        body.addWidget(self._list_w)

        btn_row = QWidget()
        btn_row.setStyleSheet("background: transparent;")
        blay = QHBoxLayout(btn_row)
        blay.setContentsMargins(0, 8, 0, 0)
        self._btn_more = QPushButton("+ Adicionar mais arquivos")
        self._btn_more.setObjectName("btnMore")
        self._btn_more.clicked.connect(self._pick)
        self._btn_more.hide()
        self._btn_conv = QPushButton("Converter para Markdown")
        self._btn_conv.setObjectName("btnConvert")
        self._btn_conv.clicked.connect(self._convert)
        self._btn_conv.setEnabled(False)
        self._btn_conv.hide()
        blay.addWidget(self._btn_more)
        blay.addStretch()
        blay.addWidget(self._btn_conv)
        body.addWidget(btn_row)
        body.addStretch()

        scroll.setWidget(body_w)
        main.addWidget(scroll)

        # footer
        foot = QLabel("Convert2MD  •  Offline  •  Código aberto")
        foot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        foot.setFixedHeight(36)
        foot.setStyleSheet(f"color: {C_MUTED}; font-size: 11px; background: {C_BG};")
        main.addWidget(foot)

    def _pick(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Selecionar arquivos", str(Path.home()),
            "Documentos (*.pdf *.docx *.xlsx *.pptx *.html *.htm *.csv)"
        )
        if paths:
            self._on_files(paths)

    def _on_files(self, paths: list[str]):
        added = False
        supported = {".pdf", ".docx", ".xlsx", ".pptx", ".html", ".htm", ".csv"}
        for p in paths:
            if Path(p).suffix.lower() not in supported or p in self._cards:
                continue
            card = FileCard(p)
            self._list_lay.addWidget(card)
            self._cards[p] = card
            added = True
        if added:
            self._drop.hide()
            self._btn_conv.show()
            self._btn_conv.setEnabled(True)
            self._btn_more.show()

    def _convert(self):
        pending = [p for p, c in self._cards.items() if not c.dest_path]
        if not pending:
            return
        self._btn_conv.setEnabled(False)
        self._btn_conv.setText("Convertendo…")
        self._worker = ConvertWorker(pending)
        self._worker.progress.connect(lambda p, v: self._cards[p].set_progress(v) if p in self._cards else None)
        self._worker.done.connect(lambda p, d: self._cards[p].set_done(d) if p in self._cards else None)
        self._worker.error.connect(lambda p, m: self._cards[p].set_error(m) if p in self._cards else None)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_finished(self):
        if all(c.dest_path for c in self._cards.values()):
            self._btn_conv.setText("✓  Tudo convertido!")
        else:
            self._btn_conv.setText("Converter para Markdown")
            self._btn_conv.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Convert2MD")
    app.setDesktopFileName("convert2md")  # links to convert2md.desktop → GNOME taskbar icon
    app.setStyleSheet(STYLESHEET)
    font = QFont("Ubuntu", 10)
    app.setFont(font)
    logo_path = Path(__file__).parent / "logo.png"
    if logo_path.exists():
        icon = QIcon(str(logo_path))
        app.setWindowIcon(icon)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
