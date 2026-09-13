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
    lines.push(...groupIntoLines(content.items));
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

// pdf.js returns loose text fragments with positions. Group fragments that
// share (roughly) the same vertical position back into lines, so column
// layouts like "Pell Grant     $5,500" stay on one line.
function groupIntoLines(items) {
  const rows = new Map();
  for (const item of items) {
    if (!item.str) continue;
    const y = Math.round(item.transform[5]);
    if (!rows.has(y)) rows.set(y, []);
    rows.get(y).push(item);
  }
  return [...rows.entries()]
    .sort((a, b) => b[0] - a[0]) // top of page first
    .map(([, frags]) =>
      frags
        .sort((a, b) => a.transform[4] - b.transform[4]) // left to right
        .map((f) => f.str)
        .join(' ')
        .replace(/\s+/g, ' ')
        .trim()
    )
    .filter(Boolean);
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
