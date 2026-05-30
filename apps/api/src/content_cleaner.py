"""
Content cleaner for Hukumonline scraped articles.

Handles 5 structural variants found across 1342 articles:
  1. INTISARI_FIRST (56.4%): "INTISARI JAWABAN" -> content -> noise
  2. TERIMA_KASIH_FIRST (25.3%): "ULASAN LENGKAP" + embedded KLINIK TERKAIT block ->
     "Terima kasih..." -> actual content -> noise
  3. ULASAN_LENGKAP_->_KT_EMBEDDED (15.7%): "ULASAN LENGKAP" -> KLINIK TERKAIT block
     -> content -> noise
  4. ULASAN_LENGKAP_FIRST (1.6%): "ULASAN LENGKAP" -> content -> noise (no KT block)
  5. NO_MARKER_FOUND (1.0%): No known start marker, keep as-is

Noise patterns stripped:
  - KLINIK TERKAIT (embedded related-article blocks)
  - TAGS + Temukan pengacara advertising
  - TIPS HUKUM / KLINIK TERBARU sidebars
  - Artikel Selanjutnya / Butuh Lebih Banyak Artikel footers
  - Berbagai info akurat / Kunjungi newsletter promos
  - Belajar Hukum Secara Online / Lihat Semua Kelas ads
  - Web External Justika CTAs
  - Daftar Isi inline
  - Navigation headers (Katalog Produk, Berlangganan, Halo Anda, dll.)
  - Chat/pricing CTAs
  - Disclaimer compression
"""
import json
import os
import re
import shutil
from typing import Optional


# ── Start markers (in priority order) ──────────────────────────────────────

CONTENT_START_MARKERS = [
    "INTISARI JAWABAN",
    "ULASAN LENGKAP",
    "Terima kasih atas pertanyaan Anda.",
    "Terima kasih atas pertanyaan Anda",
]

# ── End / cut-point markers (position-agnostic, no \\n dependency) ─────────

# These are searched as plain substrings — earliest match wins.
CONTENT_END_MARKERS = [
    "TAGS",
    "KLINIK TERBARU",
    "TIPS HUKUM",
    "Artikel Selanjutnya",
    "Butuh Lebih Banyak Artikel",
]

# ── Error detection ────────────────────────────────────────────────────────

MIN_CONTENT_LENGTH = 200
ERROR_SIGNATURES = [
    "bad gateway",
    "502 bad gateway",
    "cloudflare",
    "ray id:",
    "error reference number: 502",
]


# ── Inline noise patterns (applied after start/end extraction) ─────────────

INLINE_NOISE_PATTERNS = [
    # --- Daftar Isi block (before INTISARI / ULASAN LENGKAP) ---------------
    re.compile(r"Daftar Isi\s+pertanyaan\s+daftar isi.*?(?=INTISARI JAWABAN|ULASAN LENGKAP)", re.DOTALL),
    re.compile(r"Daftar Isi\s+pertanyaan\s+daftar isi.*?(?=\n)", re.DOTALL),

    # --- KLINIK TERKAIT block (embedded related articles with date pattern) --
    # Matches: "KLINIK TERKAIT Title1 DD Mmm YYYY Title2 DD Mmm YYYY ..."
    re.compile(
        r"KLINIK TERKAIT\s+"
        r"(?:.*?\d{1,2}\s+(?:Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agu|Sep|Okt|Nov|Des)[a-z]*[,.]?\s+\d{4}\s*)+",
        re.DOTALL,
    ),

    # --- TAGS + Temukan pengacara advertising block -------------------------
    re.compile(
        r"TAGS\s+Temukan pengacara dan kantor hukum sesuai kebutuhan Anda!"
        r".*?(?=KLINIK TERBARU|TIPS HUKUM|Butuh Lebih Banyak Artikel|Artikel Selanjutnya|Berbagai info|$)",
        re.DOTALL,
    ),

    # --- Bare TAGS at end (just the word, nothing after) --------------------
    re.compile(r"\s*TAGS\s*$"),

    # --- TIPS HUKUM sidebar block -------------------------------------------
    re.compile(
        r"TIPS HUKUM\s+Lihat Semua\s+.*?(?=\nBerbagai|\nKLINIK|\nButuh|$)",
        re.DOTALL,
    ),

    # --- KLINIK TERBARU sidebar block ---------------------------------------
    re.compile(
        r"KLINIK TERBARU\s*\n.*?(?=\nTIPS HUKUM|\nBerbagai|\nButuh|$)",
        re.DOTALL,
    ),

    # --- Butuh Lebih Banyak Artikel + Artikel Selanjutnya footer ------------
    re.compile(
        r"Butuh Lebih Banyak Artikel\s+Lihat Semua\s+Artikel Selanjutnya\s+.*$",
        re.DOTALL,
    ),
    re.compile(r"Butuh Lebih Banyak Artikel\s+Lihat Semua\s*"),
    re.compile(r"Artikel Selanjutnya\s+.*$", re.DOTALL),

    # --- Berbagai info akurat / Kunjungi newsletter block -------------------
    re.compile(
        r"Berbagai info akurat dan eksklusif seputar regulasi untuk insight Anda\s+Kunjungi\s+"
        r".*?(?=\n\S|\Z)",
        re.DOTALL,
    ),
    re.compile(r"Berbagai info akurat dan eksklusif.*?(?=$)", re.DOTALL),
    re.compile(r"Kunjungi\s*\n?.*?(?=$)", re.DOTALL),

    # --- Diposting dalam / Skala Dampak / Sektor Terdampak lines ------------
    re.compile(r"Diposting dalam\s+\d+\s+(?:jam|hari|menit)\s+yang lalu\s*"),
    re.compile(r"Diposting dalam\s+\d+\s+(?:jam|hari|menit)\s*"),
    re.compile(r"Skala Dampak:\s*\S+\s*"),
    re.compile(r"Sektor Terdampak:\s*\S+\s*"),
    re.compile(r"\d+\s+More\s*"),

    # --- Belajar Hukum Secara Online ad block -------------------------------
    re.compile(
        r"Belajar Hukum Secara Online dari Pengajar Berkompeten Dengan Biaya Terjangkau"
        r"\s+Mulai Dari Rp\.\s*[\d.]+.*?Lihat Semua Kelas\s*",
        re.DOTALL,
    ),
    re.compile(r"Belajar Hukum Secara Online.*?Lihat Semua Kelas\s*", re.DOTALL),

    # --- Perkaya riset hukum Anda ad ----------------------------------------
    re.compile(
        r"Perkaya riset hukum Anda dengan analisis hukum terbaru dwi\s*bahasa,"
        r"\s*serta koleksi terjemahan peraturan yang terintegrasi dalam "
        r"Hukumonline Pro,\s*pelajari lebih lanjut di sini\s*\.?\s*",
        re.DOTALL,
    ),
    re.compile(
        r"Perkaya riset hukum Anda dengan analisis hukum terbaru.*?"
        r"pelajari lebih lanjut di sini\s*\.?\s*",
        re.DOTALL,
    ),

    # --- Web External Justika CTA block -------------------------------------
    re.compile(r"Web External Justika\s*\n?"),

    # --- Punya Masalah Hukum? CTA block -------------------------------------
    re.compile(
        r"Punya Masalah Hukum yang sedang dihadapi\?"
        r".*?(?=\nKLINIK|\nTAGS|\nTIPS|$)",
        re.DOTALL,
    ),

    # --- Chat CTA lines -----------------------------------------------------
    re.compile(r"Chat dengan\s*\n?"),
    re.compile(r"Chat Sekarang\s*\n?"),
    re.compile(r"Konsultasi Hukum dengan Advokat Pilihan.*?(?=Daftar Isi|\nINTISARI|\nULASAN)", re.DOTALL),

    # --- Pricing (Rp ... Rp ...) lines --------------------------------------
    re.compile(r"Rp\d{1,3}(?:\.\d{3})*\s+Rp\d{1,3}(?:\.\d{3})*\s*\n?"),

    # --- Lihat Semua (standalone) -------------------------------------------
    re.compile(r"Lihat Semua\s*\n?"),

    # --- Temukan pengacara standalone (if not caught by TAGS block) ---------
    re.compile(
        r"Temukan pengacara dan kantor hukum sesuai kebutuhan Anda!"
        r"\s*Daftar jajaran ahli pada kantor hukum ternama di Indonesia,"
        r"\s*terlengkap dengan berbagai spesialisasi\s*Selengkapnya\s*",
        re.DOTALL,
    ),

    # --- Selengkapnya (standalone, often at end of ad blocks) ---------------
    re.compile(r"\s*Selengkapnya\s*$"),

    # --- Baca Disclaimer line -----------------------------------------------
    re.compile(r"Baca Disclaimer.*?(?=\n|$)", re.DOTALL),
    re.compile(r"atau konsultasi via chat mulai.*?(?=\n|$)", re.DOTALL),
    re.compile(r"kirim pertanyaan ke klinik\s*baca disclaimer.*?(?=\n|$)", re.DOTALL | re.IGNORECASE),

    # --- Powered by ---------------------------------------------------------
    re.compile(r"Powered by\s*\n?"),

    # --- Navigation crumbs --------------------------------------------------
    re.compile(r"Navigate (left|right)\s*", re.IGNORECASE),

    # --- Navigation header (survives in NO_MARKER articles) ----------------
    re.compile(
        r"Mulai Berlangganan Sekarang\s+"
        r"Profil\s+Keluar\s+"
        r"Ada pertanyaan\?\s*Hubungi Kami\s+"
        r"Bahasa\s+Bahasa Indonesia\s+English\s*",
    ),
    re.compile(
        r"Katalog Produk\s+Berlangganan Pro\s+Info Hukum Pro\s+"
        r"Info Hukum Solusi\s+Events & Awards\s+Klinik\s+"
        r"Berita\s+Hukumonline Stream\s+Data Pribadi\s+Jurnal\s*"
        r"(?:Home\s+)?Tips Hukum\s*.*?(?=ULASAN LENGKAP|INTISARI JAWABAN|PERTANYAAN)",
        re.DOTALL,
    ),
    re.compile(
        r"Halo,\s*Anda,\s*Segera Upgrade paket berlangganan Anda\.\s*"
        r"Dapatkan fitur lebih lengkap\s*Mulai Berlangganan Sekarang\s*",
    ),
    re.compile(r"Profil\s+Keluar\s+Ada pertanyaan\?\s*Hubungi Kami\s*"),
    re.compile(r"Bahasa\s+Bahasa Indonesia\s+English\s*"),
    re.compile(r"Share Article\s+Facebook\s+Twitter\s+Linkedin\s+Whatsapp\s+Copy Link\s*"),
    re.compile(r"Follow\s+Follow\s+Social Media\s+Whatsapp\s*"),

    # --- Category breadcrumb nav (e.g., "Bisnis Bisnis" repeated) ----------
    re.compile(r"(?:Pidana|Keluarga|Perdata|Kenegaraan|Profesi Hukum|Ilmu Hukum|"
               r"Bisnis|Pertanahan & Properti|Ketenagakerjaan|Perlindungan Konsumen|"
               r"Hak Asasi Manusia|Kekayaan Intelektual|Teknologi|Startup & UMKM|"
               r"Olahraga)\s+"
               r"(?:Pidana|Keluarga|Perdata|Kenegaraan|Profesi Hukum|Ilmu Hukum|"
               r"Bisnis|Pertanahan & Properti|Ketenagakerjaan|Perlindungan Konsumen|"
               r"Hak Asasi Manusia|Kekayaan Intelektual|Teknologi|Startup & UMKM|"
               r"Olahraga)\s*",
    ),

    # --- Personalisasi header fragment -------------------------------------
    re.compile(r"Personalisasi\s+Halo,\s*Anda,\s*"),
]


# ── Error detection ────────────────────────────────────────────────────────

def _is_error_content(content: str) -> bool:
    """Detect Cloudflare errors, bad gateways, and too-short content."""
    if len(content) < MIN_CONTENT_LENGTH:
        return True
    lower = content.lower()
    for sig in ERROR_SIGNATURES:
        if sig in lower:
            return True
    return False


# ── Start marker detection ─────────────────────────────────────────────────

def _find_content_start(content: str) -> int:
    """
    Find where the actual legal content begins.
    Returns the character index right after the best start marker.

    Strategy (by variant):
      1. INTISARI_FIRST: cut at "INTISARI JAWABAN"
      2. ULASAN_LENGKAP variants: cut at "ULASAN LENGKAP"
         - KT_EMBEDDED / TERIMA_KASIH_FIRST handled later by
           _strip_embedded_klinik_terkait()
      3. Fallback: "Terima kasih atas pertanyaan Anda"
      4. Last resort: return 0 (keep entire content)
    """
    candidates = []
    for marker in CONTENT_START_MARKERS:
        idx = content.find(marker)
        if idx != -1:
            candidates.append((idx, marker))

    if not candidates:
        return 0

    # Pick earliest marker
    candidates.sort(key=lambda x: x[0])
    idx, marker = candidates[0]
    return idx + len(marker)


# ── Embedded KLINIK TERKAIT removal ────────────────────────────────────────

def _strip_embedded_klinik_terkait(content: str) -> str:
    """
    Remove "KLINIK TERKAIT" block when it appears embedded near the start
    of the article body (after ULASAN_LENGKAP or INTISARI_JAWABAN).

    These blocks list 4-5 related article titles with dates and are NOT
    part of the actual legal content.

    Two common patterns:
      A) "ULASAN LENGKAP KLINIK TERKAIT [articles] Terima kasih ... [real content]"
         → KLINIK TERKAIT is between start marker and "Terima kasih"
      B) "ULASAN LENGKAP Terima kasih ... KLINIK TERKAIT [articles] [real content]"
         → "Terima kasih" comes first, then KT block, then real content

    Strategy: find the KT block, find the last date/article-title within it,
    then keep everything before KT and after the KT block's end.
    """
    kt_idx = content.find("KLINIK TERKAIT")
    if kt_idx == -1:
        return content

    # Only strip if KT appears near the beginning (within first 800 chars).
    if kt_idx > 800:
        return content

    # Find the end of the KT block — it's a list of article titles each
    # followed by a date like "DD Mmm YYYY".  We prioritize reliable
    # anchors over regex because legal content also contains dates.

    date_month = r"(?:Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agu|Sep|Okt|Nov|Des)"

    # ── Strategy 1: "Terima kasih" anchor (most reliable) ──────────────
    tks_global = content.find("Terima kasih atas pertanyaan Anda")
    if tks_global != -1:
        if kt_idx < tks_global:
            # Pattern A: KT block is between start and "Terima kasih"
            prefix = content[:kt_idx].rstrip()
            suffix = content[tks_global:]
            return prefix + "\n\n" + suffix
        else:
            # Pattern B: "Terima kasih" before KT.
            # The KT block sits mid-content. Strip it with a bounded
            # regex (max 6 entries) to avoid consuming legal citation dates.
            kt_tail = content[kt_idx:]
            m = re.match(
                r"KLINIK TERKAIT\s+"
                r"((?:.{10,150}?\d{1,2}\s+" + date_month + r"[a-z]*[,.]?\s+\d{4}\s*){1,6})",
                kt_tail,
                re.DOTALL,
            )
            if m:
                kt_block_end = kt_idx + m.end()
                suffix_len = len(content) - kt_block_end
                # Only apply if we kept most of the content
                if suffix_len > 100:
                    prefix = content[:kt_idx].rstrip()
                    suffix = content[kt_block_end:].lstrip()
                    return prefix + "\n\n" + suffix
            # Fallback: just remove the KT heading word itself
            return content[:kt_idx] + content[kt_idx + len("KLINIK TERKAIT"):].lstrip()

    # ── Strategy 2: No "Terima kasih" — bounded regex ─────────────────
    kt_tail = content[kt_idx:]
    m = re.match(
        r"KLINIK TERKAIT\s+"
        r"((?:.{10,150}?\d{1,2}\s+" + date_month + r"[a-z]*[,.]?\s+\d{4}\s*){1,6})",
        kt_tail,
        re.DOTALL,
    )
    if m:
        kt_block_end = kt_idx + m.end()
        suffix_len = len(content) - kt_block_end
        if suffix_len > 100:
            prefix = content[:kt_idx].rstrip()
            suffix = content[kt_block_end:].lstrip()
            return prefix + "\n\n" + suffix

    # ── Strategy 3: Content-like heading after KT ─────────────────────
    content_start_pattern = re.compile(
        r"\n(Jika|Menurut|Berdasarkan|Sebelumnya|Perizinan|Keharusan|"
        r"Pembudidayaan|Dalam|Terhadap|Pada|Sebagai|Ketentuan|Pengertian|"
        r"Pasal\s|Setiap|Apabila|Untuk|Terima kasih)",
    )
    m = content_start_pattern.search(content[kt_idx:])
    if m:
        cut = kt_idx + m.start()
        prefix = content[:kt_idx].rstrip()
        suffix = content[cut:].lstrip()
        return prefix + "\n\n" + suffix

    # ── Last resort ───────────────────────────────────────────────────
    return content


# ── End / cut-point detection ──────────────────────────────────────────────

def _find_content_end(content: str, start_from: int = 0) -> int:
    """
    Find the earliest end marker position (no newline dependency).
    Returns the character index where useful content ends and noise begins.
    If no marker found, returns len(content).
    """
    best = len(content)
    for marker in CONTENT_END_MARKERS:
        idx = content.find(marker, start_from)
        if idx != -1 and idx < best:
            best = idx

    return best


# ── Inline noise stripping ─────────────────────────────────────────────────

def _compress_disclaimer(text: str) -> str:
    """Compress lengthy legal disclaimers into a one-liner."""
    disclaimer_patterns = [
        (
            re.compile(
                r"Seluruh informasi hukum.*?Pernyataan Penyangkalan.*?(?=Untuk|$)",
                re.DOTALL,
            ),
            "Catatan: Seluruh informasi hukum disediakan untuk tujuan pendidikan "
            "dan bersifat umum.",
        ),
        (
            re.compile(
                r"Seluruh informasi hukum.*?\(lihat Pernyataan Penyangkalan.*?\)",
                re.DOTALL,
            ),
            "Catatan: Seluruh informasi hukum disediakan untuk tujuan pendidikan "
            "dan bersifat umum.",
        ),
        (
            re.compile(
                r"Seluruh informasi hukum dalam Klinik Hukumonline disediakan "
                r"semata-mata untuk tujuan pendidikan dan bersifat umum\..*?"
                r"Untuk memperoleh nasihat hukum.*?(?=\n\n|\Z)",
                re.DOTALL,
            ),
            "Catatan: Seluruh informasi hukum disediakan untuk tujuan pendidikan "
            "dan bersifat umum.",
        ),
    ]
    for pattern, replacement in disclaimer_patterns:
        text = pattern.sub(replacement, text)
    return text


def _strip_inline_noise(text: str) -> str:
    """Apply all inline noise patterns and normalize whitespace."""
    for pattern in INLINE_NOISE_PATTERNS:
        text = pattern.sub("", text)

    text = _compress_disclaimer(text)

    # Normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


# ── Structure normalization ────────────────────────────────────────────────

def _normalize_structure(text: str) -> str:
    """
    Ensure consistent article structure.
    - Remove leading/trailing whitespace
    - Remove lingering noise fragments
    - Ensure the content doesn't end mid-sentence with ad remnants
    """
    text = text.strip()

    # If the text ends with common ad-trailing fragments, strip them
    trailing_fragments = [
        "Lihat Semua",
        "Selengkapnya",
        "Kunjungi",
        "Skala Dampak:",
        "Sektor Terdampak:",
        "Diposting dalam",
        "More",
        "Artikel Selanjutnya",
        "Butuh Lebih Banyak Artikel",
    ]
    for frag in trailing_fragments:
        if text.endswith(frag):
            text = text[: -len(frag)].rstrip()
            break

    return text


# ── Validation ─────────────────────────────────────────────────────────────

# Noise keywords that should NEVER appear in cleaned content.
# NOTE: avoid common Indonesian words that also appear in nav headers
# (e.g., "Profil" alone is a normal word; "Profil Keluar" is nav noise).
FORBIDDEN_NOISE = [
    "Katalog Produk",
    "Berlangganan Pro",
    "Halo, Anda,",
    "Segera Upgrade paket berlangganan",
    "Profil Keluar",
    "Ada pertanyaan? Hubungi Kami",
    "Bahasa Indonesia English",
    "Share Article",
    "Follow Social Media",
    "Temukan pengacara dan kantor hukum",
    "Punya Masalah Hukum yang sedang dihadapi?",
    "Butuh Lebih Banyak Artikel",
    "Artikel Selanjutnya",
    "Web External Justika",
    "Navigate left",
    "Navigate right",
    "Berbagai info akurat dan eksklusif",
    "Diposting dalam",
    "Skala Dampak:",
    "Sektor Terdampak:",
    "Belajar Hukum Secara Online",
    "Lihat Semua Kelas",
    "Perkaya riset hukum Anda",
    "Chat Sekarang",
    "Chat dengan",
    "Powered by",
    "Mulai Berlangganan Sekarang",
    "Personalisasi Halo, Anda",
]


def _validate_cleaned_content(content: str, title: str = "") -> list[str]:
    """
    Check cleaned content for remaining noise.
    Returns list of noise keywords found (empty = clean).
    """
    found = []
    for noise in FORBIDDEN_NOISE:
        if noise.lower() in content.lower():
            found.append(noise)
    return found


# ── Main cleaning function ─────────────────────────────────────────────────

def clean_article_content(raw_content: str, title: str = "") -> Optional[str]:
    """
    Clean a single article's raw scraped content.

    Returns cleaned text or None if the article should be dropped
    (error page, too short, etc.).
    """
    # 1. Error detection
    if _is_error_content(raw_content):
        return None

    # 2. Find content start
    start = _find_content_start(raw_content)
    if start == 0:
        print(f"  WARNING: no content start marker found for '{title}', keeping as-is")

    # 3. Find content end (earliest noise marker)
    end = _find_content_end(raw_content, start_from=start)
    body = raw_content[start:end].strip()

    # 4. Fallback: if extracted body is too short, keep original
    if len(body) < MIN_CONTENT_LENGTH:
        print(f"  WARNING: extracted body too short ({len(body)} chars) for '{title}', "
              f"keeping full raw")
        body = raw_content.strip()

    # 5. Strip embedded KLINIK TERKAIT blocks
    body = _strip_embedded_klinik_terkait(body)

    # 6. Strip inline noise patterns
    body = _strip_inline_noise(body)

    # 7. Normalize structure
    body = _normalize_structure(body)

    # 8. Final length check
    if len(body) < MIN_CONTENT_LENGTH:
        return None

    return body


# ── Batch cleaning ─────────────────────────────────────────────────────────

def clean_articles(input_dir: str, output_dir: str, validate: bool = True):
    """
    Clean all JSON article files from input_dir and write to output_dir.

    Args:
        input_dir: Path to raw scraped articles (scrap/result/)
        output_dir: Path to write cleaned articles (scrap/cleaned/)
        validate: If True, run post-clean validation and print report
    """
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Collect all JSON files
    json_files = []
    for root, _dirs, files in os.walk(input_dir):
        for f in files:
            if f.endswith(".json"):
                json_files.append(os.path.join(root, f))

    total_articles = 0
    total_cleaned = 0
    total_dropped = 0
    total_kept_raw = 0
    validation_issues: list[dict] = []

    for file_path in json_files:
        rel_dir = os.path.relpath(os.path.dirname(file_path), input_dir)
        out_subdir = os.path.join(output_dir, rel_dir)
        os.makedirs(out_subdir, exist_ok=True)

        with open(file_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        cleaned_articles = []
        for article in data:
            total_articles += 1
            title = article.get("title", "No Title")
            raw = article.get("content", "")

            cleaned_content = clean_article_content(raw, title=title)

            if cleaned_content is None:
                total_dropped += 1
                print(f"  DROP: [{os.path.basename(file_path)}] {title}")
                continue

            is_raw_fallback = cleaned_content == raw.strip()
            if is_raw_fallback:
                total_kept_raw += 1

            # Validation
            if validate:
                noise_found = _validate_cleaned_content(cleaned_content, title=title)
                if noise_found:
                    validation_issues.append({
                        "title": title,
                        "file": os.path.basename(file_path),
                        "noise": noise_found,
                    })

            cleaned_article = {
                "title": article.get("title", ""),
                "link": article.get("link", ""),
                "publish_date": article.get("publish_date", ""),
                "theme": article.get("theme", ""),
                "tags": article.get("tags", []),
                "content": cleaned_content,
            }
            cleaned_articles.append(cleaned_article)
            total_cleaned += 1

        if cleaned_articles:
            out_path = os.path.join(out_subdir, os.path.basename(file_path))
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump(cleaned_articles, fh, ensure_ascii=False, indent=2)

    # Print summary
    print()
    print(f"=== CLEANING COMPLETE ===")
    print(f"  Total articles:        {total_articles}")
    print(f"  Cleaned successfully:  {total_cleaned}")
    print(f"  Dropped (errors/short): {total_dropped}")
    print(f"  Kept raw (no markers): {total_kept_raw}")
    print(f"  Output: {output_dir}")

    if validate:
        print(f"\n=== VALIDATION ===")
        if validation_issues:
            print(f"  Articles with remaining noise: {len(validation_issues)} "
                  f"({len(validation_issues)/max(total_cleaned,1)*100:.1f}%)")
            # Group by noise type
            from collections import Counter
            noise_counter = Counter()
            for issue in validation_issues:
                for n in issue["noise"]:
                    noise_counter[n] += 1
            print(f"  Top noise remnants:")
            for noise, count in noise_counter.most_common(10):
                print(f"    - {noise}: {count} articles")
        else:
            print(f"  ALL CLEAN — no forbidden noise detected in any article!")
    print()


if __name__ == "__main__":
    import sys
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "scrap/result"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "scrap/cleaned"
    clean_articles(input_dir, output_dir, validate=True)