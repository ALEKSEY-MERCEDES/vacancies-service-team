from aiogram.types import Document


def is_valid_resume(doc: Document) -> bool:
    if doc.file_size > 20 * 1024 * 1024:
        return False

    return doc.mime_type in (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
