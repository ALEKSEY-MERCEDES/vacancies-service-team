from aiogram.types import Document


def is_valid_resume(doc: Document) -> bool:
    if doc.file_size and doc.file_size > 20 * 1024 * 1024:
        return False

    mime = (doc.mime_type or "").lower()
    name = (doc.file_name or "").lower()

    if mime in (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ):
        return True

    return name.endswith(".pdf") or name.endswith(".docx")
