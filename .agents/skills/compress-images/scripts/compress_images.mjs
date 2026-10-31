#!/usr/bin/env node
/**
 * Normalize filenames (macOS NFD -> NFC), unify all images (.png, .heic, .webp, .jpeg, .JPG)
 * to .jpg, and compress them in-place using `sharp` (libvips + MozJPEG).
 * Also checks image references in _posts/*-struggle-<N>.markdown.
 *
 * Usage:
 *   node .agents/skills/compress-images/scripts/compress_images.mjs img/struggle/<N> [--max-dim 1920] [--quality 80]
 */
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ensure `sharp` is installed in the scripts directory
const sharpModulePath = path.join(__dirname, "node_modules", "sharp");
if (!fs.existsSync(sharpModulePath)) {
  console.log("Installing sharp in .agents/skills/compress-images/scripts/ ...");
  const npmBin = path.join(path.dirname(process.execPath), "npm");
  const npmCmd = fs.existsSync(npmBin) ? npmBin : "npm";
  execFileSync(npmCmd, ["install", "--no-audit", "--no-fund"], {
    cwd: __dirname,
    stdio: "inherit",
    env: {
      ...process.env,
      PATH: `${path.dirname(process.execPath)}:${process.env.PATH || ""}`,
    },
  });
}

const { default: sharp } = await import("sharp");

const SUPPORTED_EXTS = new Set([
  ".jpg",
  ".jpeg",
  ".png",
  ".webp",
  ".heic",
  ".tiff",
  ".tif",
]);

function formatBytes(size) {
  if (size < 1024) return `${size} B`;
  return `${(size / 1024).toFixed(1)} KB`;
}

function parseArgs(argv) {
  const args = argv.slice(2);
  let target = null;
  let maxDim = 1920;
  let quality = 80;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--max-dim" && args[i + 1]) {
      maxDim = Number.parseInt(args[++i], 10);
    } else if (args[i] === "--quality" && args[i + 1]) {
      quality = Number.parseInt(args[++i], 10);
    } else if (!args[i].startsWith("-") && !target) {
      target = args[i];
    }
  }

  if (!target) {
    // Auto-detect from git branch (e.g. feature/struggle-70) or latest post
    try {
      const branch = execFileSync("git", ["rev-parse", "--abbrev-ref", "HEAD"], {
        encoding: "utf8",
      }).trim();
      const m = branch.match(/struggle-(\d+)/);
      if (m) {
        target = `img/struggle/${m[1]}`;
      }
    } catch {
      // ignore
    }
  }

  if (!target) {
    console.error(
      "Usage: node compress_images.mjs [dir_path] [--max-dim 1920] [--quality 80]\nExample: node compress_images.mjs img/struggle/70"
    );
    process.exit(1);
  }

  return { target, maxDim, quality };
}

async function processAndCompressFile(targetDir, entryName, maxDim, quality) {
  const oldPath = path.join(targetDir, entryName);
  const nfcName = entryName.normalize("NFC");
  const parsed = path.parse(nfcName);
  const extLower = parsed.ext.toLowerCase();

  if (!SUPPORTED_EXTS.has(extLower)) return;

  const finalName = `${parsed.name}.jpg`;
  const finalPath = path.join(targetDir, finalName);
  const beforeSize = fs.statSync(oldPath).size;

  // Step 1: If HEIC, convert via macOS `sips` to a temporary JPEG first
  let sourcePath = oldPath;
  let tempHeicJpg = null;
  if (extLower === ".heic") {
    tempHeicJpg = path.join(targetDir, `.tmp_heic_${process.pid}_${finalName}`);
    execFileSync("sips", ["-s", "format", "jpeg", oldPath, "--out", tempHeicJpg], {
      stdio: "ignore",
    });
    sourcePath = tempHeicJpg;
  }

  try {
    const inputBuffer = fs.readFileSync(sourcePath);
    const meta = await sharp(inputBuffer).metadata();
    const needsResize =
      (meta.width && meta.width > maxDim) || (meta.height && meta.height > maxDim);
    const isConvertingFormat = extLower !== ".jpg";
    const isSlideOrTitle =
      parsed.name === "title" || parsed.name.endsWith("-발표자료");

    const outputBuffer = await sharp(inputBuffer)
      .rotate() // Auto-orient from EXIF and strip metadata
      .flatten({ background: "#ffffff" }) // Ensure transparent PNG backgrounds become white
      .resize(maxDim, maxDim, {
        fit: "inside",
        withoutEnlargement: true,
      })
      .jpeg({
        quality: isSlideOrTitle ? Math.max(quality, 85) : quality,
        mozjpeg: true,
        chromaSubsampling: isSlideOrTitle ? "4:4:4" : "4:2:0",
      })
      .toBuffer();

    const afterSize = outputBuffer.length;

    // Remove original file if its filename/extension or NFC encoding differed
    if (entryName !== finalName) {
      fs.unlinkSync(oldPath);
    }

    if (isConvertingFormat || needsResize || afterSize < beforeSize) {
      fs.writeFileSync(finalPath, outputBuffer);
      const ratio = ((1 - afterSize / beforeSize) * 100).toFixed(1);
      const tag = isConvertingFormat ? `Converted ${extLower}->.jpg` : "Compressed";
      console.log(
        `[${tag}] ${finalName}: ${formatBytes(beforeSize)} -> ${formatBytes(afterSize)} (${ratio >= 0 ? `-${ratio}%` : `+${Math.abs(ratio)}%`})`
      );
    } else {
      // Ensure NFC filename on APFS even when skipping re-write
      if (entryName !== finalName) {
        fs.writeFileSync(finalPath, inputBuffer);
      }
      console.log(
        `[Skipped]    ${finalName}: already optimal (${formatBytes(beforeSize)})`
      );
    }
  } finally {
    if (tempHeicJpg && fs.existsSync(tempHeicJpg)) {
      fs.unlinkSync(tempHeicJpg);
    }
  }
}

function checkMarkdownReferences(struggleNum, targetDir) {
  const postsDir = path.resolve("_posts");
  if (!fs.existsSync(postsDir)) return;

  const suffix = `-struggle-${struggleNum}.markdown`;
  const matchingPosts = fs
    .readdirSync(postsDir)
    .filter((f) => f.endsWith(suffix))
    .sort();

  if (matchingPosts.length === 0) return;

  const postPath = path.join("_posts", matchingPosts[matchingPosts.length - 1]);
  const content = fs.readFileSync(postPath, "utf8");
  const regex = new RegExp(`/img/struggle/${struggleNum}/([^)\\s]+)`, "g");
  const referenced = [];
  let match;
  while ((match = regex.exec(content)) !== null) {
    referenced.push(match[1].normalize("NFC"));
  }

  const existing = new Set(
    fs
      .readdirSync(targetDir, { withFileTypes: true })
      .filter((e) => e.isFile() && !e.name.startsWith("."))
      .map((e) => e.name.normalize("NFC"))
  );

  console.log(`\n=== Image Check against ${postPath} ===`);
  for (const ref of referenced) {
    const status = existing.has(ref) ? "OK     " : "MISSING";
    console.log(`  [${status}] ${ref}`);
  }

  const refSet = new Set(referenced);
  for (const file of [...existing].sort()) {
    if (!refSet.has(file)) {
      console.log(
        `  [UNLINKED] ${file} (exists in folder but not referenced in markdown)`
      );
    }
  }
}

async function main() {
  const { target, maxDim, quality } = parseArgs(process.argv);
  const repoRoot = path.resolve(__dirname, "../../../..");

  let targetDir;
  if (/^\d+$/.test(target)) {
    targetDir = path.join(repoRoot, "img", "struggle", target);
  } else if (fs.existsSync(target)) {
    targetDir = path.resolve(target);
  } else if (
    target.startsWith("/") &&
    fs.existsSync(path.join(repoRoot, target.slice(1)))
  ) {
    targetDir = path.join(repoRoot, target.slice(1));
  } else {
    targetDir = path.resolve(repoRoot, target);
  }

  if (!fs.existsSync(targetDir)) {
    console.error(`Directory does not exist: ${targetDir}`);
    process.exit(1);
  }

  const dsStore = path.join(targetDir, ".DS_Store");
  if (fs.existsSync(dsStore)) {
    fs.unlinkSync(dsStore);
    console.log("Removed .DS_Store");
  }

  const entries = fs
    .readdirSync(targetDir, { withFileTypes: true })
    .filter((e) => e.isFile() && !e.name.startsWith("."))
    .map((e) => e.name)
    .sort();

  if (entries.length === 0) {
    console.log(
      `No image files currently in ${path.relative(repoRoot, targetDir)}/.`
    );
  } else {
    for (const entryName of entries) {
      await processAndCompressFile(targetDir, entryName, maxDim, quality);
    }
  }

  const struggleMatch = targetDir.match(/[/\\]img[/\\]struggle[/\\](\d+)$/);
  if (struggleMatch) {
    checkMarkdownReferences(struggleMatch[1], targetDir);
  }
}

await main();
