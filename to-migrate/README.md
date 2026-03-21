# to-migrate

Legacy standalone tools awaiting migration to the plugin format.

## Status

| Folder | Status | Notes |
|--------|--------|-------|
| 01 - codescanner | Migrated | Now `plugins/dev/skills/code-scanner/`. Deleted. |
| 02 - RAG | Killed | Archon V1 clone, too project-specific. Deleted. |
| 03 - website to markdown | Parked | Website crawler + markdown converter. Overlaps with `obsidian:defuddle` for single pages. The multi-page crawling/spidering is the differentiator but has heavy deps (OpenAI, LanceDB). Needs rethinking as a lighter skill. |
| 05 - pdf-scanner | Parked | PDF text + image extraction with OCR and FAISS. Heavy native deps (tesseract, cv2, PyMuPDF). Core concept is useful but needs reimagining without the local ML stack. |
