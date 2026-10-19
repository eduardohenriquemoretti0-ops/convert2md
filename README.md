# Convert2MD

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Desktop: PyQt6](https://img.shields.io/badge/desktop-PyQt6-41CD52?logo=qt&logoColor=white)
![Android: Kivy APK](https://img.shields.io/badge/Android-Kivy%20APK-3DDC84?logo=android&logoColor=white)
![Web: Flask](https://img.shields.io/badge/web-Flask-000000?logo=flask&logoColor=white)
![Status: funcional](https://img.shields.io/badge/status-funcional-success)

**Conversor de documentos para Markdown que vive em três frentes — desktop, Android e web — a partir de um núcleo Python comum.** O mesmo motor de conversão (`convert2md.py`) é entregue por uma interface desktop (PyQt6), um app Android empacotado em APK (Kivy + buildozer) e dependências prontas para uma versão web (Flask). Um cartão de visita de versatilidade full-stack: levar o mesmo código do servidor ao dispositivo do usuário.

## O que converte

Documentos comuns de escritório e web para Markdown — PDF, planilhas (XLSX), HTML e texto — usando `pypdf`, `openpyxl`, `html2text` e `pillow`.

## Como rodar

**Desktop (PyQt6):**
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python gui.py
```

**Android (Kivy, APK):** empacotado com buildozer a partir de `main.py`.
```bash
buildozer -v android debug
```
Configuração em `buildozer.spec` (pacote `com.convert2md`).

**Núcleo / linha de comando:** a lógica de conversão fica em `convert2md.py`, reutilizada por todas as frentes.

## Estrutura

- `convert2md.py` — núcleo de conversão (reutilizado por todas as interfaces).
- `gui.py` — app desktop (PyQt6).
- `main.py` — entrada Android (Kivy).
- `buildozer.spec` — build do APK.
- `static/` — recursos de interface.
