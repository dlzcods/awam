def format_docs_with_metadata(docs):
    """
    Formats the retrieved documents into a string with rich metadata headers.
    
    Args:
        docs: List of langchain Document objects.
        
    Returns:
        String of formatted documents.
    """
    formatted = []
    for d in docs:
        meta = d.metadata
        # Format text with Metadata Header so LLM is context-aware
        # Using the keys from the User's provided schema: title, publish_date, theme, tags
        text = (
            f"[JUDUL]: {meta.get('title', 'Unknown')}\n"
            f"[TANGGAL TERBIT]: {meta.get('publish_date', 'Unknown')}\n"
            f"[KATEGORI]: {meta.get('theme', 'General')} | [TAGS]: {meta.get('tags', [])}\n"
            f"[ISI KONTEN]:\n{d.page_content}\n"
            f"--------------------------------------------------"
        )
        formatted.append(text)
    return "\n\n".join(formatted)
