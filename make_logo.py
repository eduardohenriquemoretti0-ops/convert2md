#!/usr/bin/env python3
"""Generate Convert2MD logo as SVG + PNG."""
from pathlib import Path
import subprocess, shutil

SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="shadow">
      <feDropShadow dx="3" dy="4" stdDeviation="5" flood-color="#00000040"/>
    </filter>
    <filter id="cshadow">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="#00000055"/>
    </filter>
    <linearGradient id="brainGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00FF88"/>
      <stop offset="50%" stop-color="#00CC66"/>
      <stop offset="100%" stop-color="#009944"/>
    </linearGradient>
  </defs>

  <!-- white background -->
  <rect width="512" height="512" fill="white"/>

  <!-- ─── DIGITAL BRAIN ──────────────────────────────────────── -->
  <g filter="url(#glow)" fill="url(#brainGrad)" stroke="#00AA55" stroke-width="2.5">
    <!-- Left lobe -->
    <path d="
      M 256 130
      C 230 115, 195 110, 170 125
      C 145 140, 128 165, 125 192
      C 118 205, 110 220, 112 240
      C 108 258, 112 278, 120 292
      C 128 315, 142 330, 160 340
      C 175 350, 195 355, 215 350
      C 228 346, 240 338, 248 328
      C 252 322, 254 315, 256 308
      L 256 130 Z
    "/>
    <!-- Right lobe -->
    <path d="
      M 256 130
      C 282 115, 317 110, 342 125
      C 367 140, 384 165, 387 192
      C 394 205, 402 220, 400 240
      C 404 258, 400 278, 392 292
      C 384 315, 370 330, 352 340
      C 337 350, 317 355, 297 350
      C 284 346, 272 338, 264 328
      C 260 322, 258 315, 256 308
      L 256 130 Z
    "/>
    <!-- Brain stem -->
    <path d="M 238 340 Q 256 360 274 340 L 274 370 Q 256 385 238 370 Z"/>
  </g>

  <!-- Brain folds -->
  <g stroke="#007733" stroke-width="2" fill="none" opacity="0.7">
    <path d="M 148 175 Q 165 165, 185 178 Q 198 188, 190 205"/>
    <path d="M 130 225 Q 148 215, 168 228 Q 182 240, 172 258"/>
    <path d="M 138 270 Q 158 262, 175 275 Q 188 285, 180 300"/>
    <path d="M 170 175 Q 190 160, 210 173 Q 225 185, 215 205"/>
    <path d="M 364 175 Q 347 165, 327 178 Q 314 188, 322 205"/>
    <path d="M 382 225 Q 364 215, 344 228 Q 330 240, 340 258"/>
    <path d="M 374 270 Q 354 262, 337 275 Q 324 285, 332 300"/>
    <path d="M 342 175 Q 322 160, 302 173 Q 287 185, 297 205"/>
  </g>

  <!-- Circuit lines -->
  <g stroke="#00FF88" stroke-width="1.5" fill="none" opacity="0.5">
    <line x1="125" y1="210" x2="150" y2="210"/>
    <line x1="113" y1="245" x2="140" y2="245"/>
    <line x1="122" y1="280" x2="148" y2="280"/>
    <line x1="150" y1="210" x2="150" y2="245"/>
    <line x1="140" y1="245" x2="140" y2="280"/>
    <line x1="387" y1="210" x2="362" y2="210"/>
    <line x1="399" y1="245" x2="372" y2="245"/>
    <line x1="390" y1="280" x2="364" y2="280"/>
    <line x1="362" y1="210" x2="362" y2="245"/>
    <line x1="372" y1="245" x2="372" y2="280"/>
    <line x1="200" y1="118" x2="256" y2="108"/>
    <line x1="256" y1="108" x2="312" y2="118"/>
  </g>

  <!-- Circuit nodes -->
  <g fill="#00FF88" opacity="0.9">
    <circle cx="125" cy="210" r="4"/>
    <circle cx="113" cy="245" r="4"/>
    <circle cx="122" cy="280" r="4"/>
    <circle cx="150" cy="210" r="3"/>
    <circle cx="140" cy="245" r="3"/>
    <circle cx="148" cy="280" r="3"/>
    <circle cx="387" cy="210" r="4"/>
    <circle cx="399" cy="245" r="4"/>
    <circle cx="390" cy="280" r="4"/>
    <circle cx="362" cy="210" r="3"/>
    <circle cx="372" cy="245" r="3"/>
    <circle cx="364" cy="280" r="3"/>
    <circle cx="200" cy="118" r="3"/>
    <circle cx="256" cy="108" r="4"/>
    <circle cx="312" cy="118" r="3"/>
  </g>

  <!-- ─── FILE ICON (rotated, dragged toward brain) ────────────── -->
  <g filter="url(#shadow)" transform="translate(186, 195) rotate(-8, 70, 85)">
    <!-- file body -->
    <rect x="10" y="0" width="118" height="148" rx="10" ry="10"
          fill="white" stroke="#CCCCCC" stroke-width="2"/>
    <!-- folded corner -->
    <path d="M 88 0 L 128 40 L 88 40 Z" fill="#E0E0E0" stroke="#CCCCCC" stroke-width="1.5"/>
    <!-- TXT badge -->
    <rect x="22" y="10" width="52" height="22" rx="5" fill="#6366F1"/>
    <text x="48" y="26" text-anchor="middle"
          font-family="monospace" font-size="13" font-weight="bold"
          fill="white">TXT</text>
    <!-- text lines -->
    <line x1="22" y1="52"  x2="106" y2="52"  stroke="#DDDDDD" stroke-width="3" stroke-linecap="round"/>
    <line x1="22" y1="66"  x2="98"  y2="66"  stroke="#DDDDDD" stroke-width="3" stroke-linecap="round"/>
    <line x1="22" y1="80"  x2="106" y2="80"  stroke="#DDDDDD" stroke-width="3" stroke-linecap="round"/>
    <line x1="22" y1="94"  x2="82"  y2="94"  stroke="#DDDDDD" stroke-width="3" stroke-linecap="round"/>
    <line x1="22" y1="108" x2="106" y2="108" stroke="#DDDDDD" stroke-width="3" stroke-linecap="round"/>
    <line x1="22" y1="122" x2="92"  y2="122" stroke="#DDDDDD" stroke-width="3" stroke-linecap="round"/>
  </g>

  <!-- ─── CURSOR (dragging the file) ─────────────────────────── -->
  <g filter="url(#cshadow)" transform="translate(240, 272)">
    <polygon points="0,0 0,36 10,28 16,42 22,40 16,26 28,26"
             fill="white" stroke="#333333" stroke-width="2.2"
             stroke-linejoin="round"/>
  </g>

  <!-- Motion trail -->
  <g opacity="0.3" stroke="#6366F1" stroke-width="2" fill="none">
    <path d="M 218 322 Q 232 316, 244 310" stroke-dasharray="4,4"/>
    <path d="M 214 332 Q 226 326, 238 320" stroke-dasharray="3,5"/>
    <path d="M 210 342 Q 220 337, 232 332" stroke-dasharray="2,6"/>
  </g>

  <!-- ─── APP NAME ────────────────────────────────────────────── -->
  <text x="212" y="418"
        font-family="\'Ubuntu\', \'Segoe UI\', sans-serif"
        font-size="40" font-weight="800" fill="#1E293B">Convert</text>
  <text x="360" y="418"
        font-family="\'Ubuntu\', \'Segoe UI\', sans-serif"
        font-size="40" font-weight="800" fill="#00CC66">2MD</text>

  <!-- tagline -->
  <text x="256" y="452" text-anchor="middle"
        font-family="\'Ubuntu\', \'Segoe UI\', sans-serif"
        font-size="15" fill="#64748B" letter-spacing="2">
    documents → markdown
  </text>
</svg>'''

out_svg = Path("/home/eduardo/convert2md/logo.svg")
out_svg.write_text(SVG)
print(f"SVG: {out_svg}")

# Try converters in order
if shutil.which("inkscape"):
    subprocess.run([
        "inkscape", str(out_svg),
        f"--export-filename=/home/eduardo/convert2md/logo.png",
        "--export-width=512"
    ], check=True)
    print("PNG via inkscape")
elif shutil.which("rsvg-convert"):
    subprocess.run([
        "rsvg-convert", "-w", "512", "-h", "512",
        str(out_svg), "-o", "/home/eduardo/convert2md/logo.png"
    ], check=True)
    print("PNG via rsvg-convert")
else:
    try:
        import cairosvg
        cairosvg.svg2png(url=str(out_svg),
                         write_to="/home/eduardo/convert2md/logo.png",
                         output_width=512, output_height=512)
        print("PNG via cairosvg")
    except ImportError:
        print("SVG saved. Install inkscape/rsvg-convert/cairosvg for PNG.")

if __name__ == "__main__":
    pass
