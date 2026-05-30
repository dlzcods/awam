MAX_CHUNK_CHARS = 600


def format_docs_with_metadata(docs):
    """
    Formats the retrieved documents into a string with metadata.

    Each document is prefixed with its citation number. The LLM MUST only use
    numbers [1] to [N] where N is the total document count. Metadata labels
    use plain text (no brackets) to avoid confusion with citation markers.
    """
    count = len(docs)
    formatted = []
    for i, d in enumerate(docs, 1):
        meta = d.metadata
        content = d.page_content[:MAX_CHUNK_CHARS]
        if len(d.page_content) > MAX_CHUNK_CHARS:
            content += "..."

        text = (
            f"--- DOKUMEN {i} (sitasi sebagai [{i}]) ---\n"
            f"Judul: {meta.get('title', 'Unknown')}\n"
            f"Tanggal: {meta.get('publish_date', 'Unknown')}\n"
            f"Kategori: {meta.get('theme', 'General')}\n"
            f"Isi:\n{content}"
        )
        formatted.append(text)

    header = f"TERSEDIA {count} DOKUMEN. HANYA gunakan sitasi [1] sampai [{count}].\n\n"
    return header + "\n\n".join(formatted)
