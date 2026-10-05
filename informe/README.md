# Informe universitario: `persona.csv`

Informe académico en LaTeX sobre preparación, validación y análisis descriptivo del dataset local `data/persona.csv`. La carátula institucional y las páginas preliminares siguen como referencia el informe anterior de `../main.tex`; el contenido se redactó desde la documentación vigente del proyecto.

## Archivos

- `main.tex`: portada, resumen, índice, listas y formato general del informe.
- `secciones/`: contenido del informe por capítulos.
- `referencias.bib`: fuentes bibliográficas citadas en el informe.
- `../Logo_Umsa.png`: recurso gráfico de la carátula.

## Compilación

Desde esta carpeta, con una distribución TeX que incluya `pdflatex`, `biber` y `biblatex`:

```powershell
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

La compilación final depende de que el entorno tenga instalada una distribución TeX con `biblatex`. Las cifras del informe se deben volver a cotejar con `docs/` cuando cambie el estado publicado del proyecto.

El informe se compilo con MiKTeX mediante `latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex`; latexmk ejecuto Biber y las pasadas de pdfLaTeX. El PDF generado es `main.pdf` (20 paginas). Las cifras deben cotejarse con `docs/` si cambia la version publicada. El informe anterior `informe/main.pdf` se conserva intacto y no corresponde a este contenido.

La caratula conserva la alineacion centrada de la referencia institucional. Los encabezados del cuerpo y de las paginas preliminares estan alineados a la izquierda. Las citas y la bibliografia usan el estilo autor-año configurado en `biblatex`; el diseño general mantiene los márgenes, interlineado y jerarquia tipografica definidos en este documento.
