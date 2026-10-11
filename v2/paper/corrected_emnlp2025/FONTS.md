# Fonts

`main.tex` loads Noto Serif Ethiopic via `fontspec`, so it needs XeLaTeX or
LuaLaTeX and the font files in `fonts/`.

The font files are not tracked here, to avoid duplicating 616 KB that the
distribution archive already contains. Take them from
`corrected_emnlp2025.zip` at the repository root:

```bash
unzip -j ../../../corrected_emnlp2025.zip \
  'corrected_emnlp2025/fonts/*' -d fonts/
```

Noto Serif Ethiopic is distributed under the SIL Open Font License 1.1
(`fonts/OFL.txt` in the archive); upstream is github.com/notofonts/ethiopic.
