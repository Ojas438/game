// readFile.js
// Turns an uploaded or photographed file into plain text that the parser can
// read. Everything runs in the browser — the file never leaves the device.
//
//   - PDF with a real text layer  → read the text directly (fast, exact)
//   - Scanned PDF (image pages)   → render each page and OCR it
//   - Photo / image               → OCR it
//   - Plain .txt                  → read as-is
//
// The heavy libraries (pdf.js, Tesseract) are imported lazily so they only
// load when someone actually uploads a file, keeping the initial page light.
// This module produces text only; it does no parsing or interpretation.

import { groupIntoLines } from './layout.js';

// If a PDF's text layer yields fewer than this many characters, we assume it's
// a scan and fall back to OCR.
const MIN_PDF_TEXT = 40;

/**
 * @param {File} file
 * @param {(status: {stage: string, progress: number}) => void} onProgress
 * @returns {Promise<{ text: string, source: string }>}
 */
export async function readFile(file, onProgress = () => {}) {
  const name = (file.name || '').toLowerCase();
  const isPdf = file.type === 'application/pdf' || name.endsWith('.pdf');
  const isImage = file.type.startsWith('image/');

  if (isPdf) return readPdf(file, onProgress);
  if (isImage) {
    onProgress({ stage: 'Reading image', progress: 0 });
    const text = await ocrImage(file, onProgress);
    return { text, source: 'image-ocr' };
  }

  // Anything else: treat as plain text.
  const text = await file.text();
  return { text, source: 'text' };
}

async function readPdf(file, onProgress) {
  onProgress({ stage: 'Opening PDF', progress: 0 });
  const pdfjs = await import('pdfjs-dist');
  const workerUrl = (await import('pdfjs-dist/build/pdf.worker.min.mjs?url')).default;
  pdfjs.GlobalWorkerOptions.workerSrc = workerUrl;

  const data = new Uint8Array(await file.arrayBuffer());
  const pdf = await pdfjs.getDocument({ data }).promise;

  // First try the embedded text layer.
  let lines = [];
  for (let n = 1; n <= pdf.numPages; n++) {
    const page = await pdf.getPage(n);
    const content = await page.getTextContent();
    const pageWidth = page.getViewport({ scale: 1 }).width;
    // Normalize pdf.js's positioned items to { str, x, y, w } for the
    // column-aware line grouper.
    const items = content.items.map((it) => ({
      str: it.str,
      x: it.transform[4],
      y: it.transform[5],
      w: it.width || 0,
    }));
    lines.push(...groupIntoLines(items, pageWidth));
    onProgress({ stage: `Reading page ${n} of ${pdf.numPages}`, progress: n / pdf.numPages });
  }
  const text = lines.join('\n').trim();
  if (text.length >= MIN_PDF_TEXT) return { text, source: 'pdf-text' };

  // Looks like a scan — render each page and OCR it.
  const worker = await createOcrWorker(onProgress);
  try {
    const pages = [];
    for (let n = 1; n <= pdf.numPages; n++) {
      onProgress({ stage: `Scanning page ${n} of ${pdf.numPages}`, progress: n / pdf.numPages });
      const canvas = await renderPageToCanvas(await pdf.getPage(n), pdfjs);
      const { data: result } = await worker.recognize(canvas);
      pages.push(result.text);
    }
    return { text: pages.join('\n').trim(), source: 'pdf-ocr' };
  } finally {
    await worker.terminate();
  }
}

async function renderPageToCanvas(page, pdfjs) {
  const viewport = page.getViewport({ scale: 2 }); // upscale for better OCR
  const canvas = document.createElement('canvas');
  canvas.width = viewport.width;
  canvas.height = viewport.height;
  const context = canvas.getContext('2d');
  await page.render({ canvasContext: context, viewport }).promise;
  return canvas;
}

async function ocrImage(file, onProgress) {
  const worker = await createOcrWorker(onProgress);
  try {
    const { data } = await worker.recognize(file);
    return data.text.trim();
  } finally {
    await worker.terminate();
  }
}

async function createOcrWorker(onProgress) {
  const { createWorker } = await import('tesseract.js');
  return createWorker('eng', 1, {
    logger: (m) => {
      if (m.status === 'recognizing text') {
        onProgress({ stage: 'Reading text', progress: m.progress });
      }
    },
  });
}
