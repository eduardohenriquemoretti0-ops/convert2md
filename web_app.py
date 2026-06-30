#!/usr/bin/env python3
"""Convert2MD — Web App. Desktop + Android browser. Flask backend."""
import sys
import tempfile
from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

sys.path.insert(0, str(Path(__file__).parent))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

SUPPORTED = {".pdf", ".docx", ".xlsx", ".pptx", ".html", ".htm", ".csv"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ad")
def ad():
    return render_template("ad.html")


@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify(error="Nenhum arquivo enviado"), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify(error="Arquivo inválido"), 400

    p = Path(file.filename)
    ext = p.suffix.lower()

    if ext not in SUPPORTED:
        return jsonify(error=f"Formato não suportado: {ext}"), 400

    from convert2md import CONVERTERS, _clean

    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / p.name
        file.save(str(src))
        fn = CONVERTERS[ext]
        try:
            md = _clean(fn(src))
        except Exception as exc:
            return jsonify(error=str(exc)), 500

    return send_file(
        BytesIO(md.encode("utf-8")),
        as_attachment=True,
        download_name=p.stem + ".md",
        mimetype="text/markdown",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
