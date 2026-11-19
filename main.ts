// news-image-20261119: ship the finished front page for 19 November 2026.
// The picture itself is drawn by build_image.py (Pillow) and stored next to
// this file as entry.png. This program does nothing else: it puts that file
// where the grader reads it, /output/entry.png (or $MAKEFUN_OUTPUT_DIR
// when set, for a local run).
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = dirname(fileURLToPath(import.meta.url));
const destination = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(destination, { recursive: true });
copyFileSync(join(repoRoot, "entry.png"), join(destination, "entry.png"));
