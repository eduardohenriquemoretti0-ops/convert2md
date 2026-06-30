[app]
title = Convert2MD
package.name = convert2md
package.domain = com.convert2md
source.dir = .
source.include_exts = py,png,jpg,svg,kv,atlas,json,html,css,js
source.exclude_dirs = tests,bin,.buildozer,.git,__pycache__,convert2md.egg-info,node_modules,graph-ui
source.exclude_patterns = gui.py,make_logo.py,buildozer.spec
version = 1.0.0

requirements = python3,kivy,flask,jinja2,werkzeug,click,itsdangerous,markupsafe,html2text,openpyxl,pymupdf,pymupdf4llm,pillow

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.arch = arm64-v8a
android.allow_backup = False

[buildozer]
log_level = 2
warn_on_root = 1
