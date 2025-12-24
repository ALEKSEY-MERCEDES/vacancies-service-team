from aiogram.types import Document
from src.bot.utils.files import is_valid_resume


def make_doc(
    file_name=None,
    mime_type=None,
    file_size=1024,
):
    return Document(
        file_id="1",
        file_unique_id="2",
        file_name=file_name,
        mime_type=mime_type,
        file_size=file_size,
    )


def test_valid_pdf_mime():
    doc = make_doc(
        file_name="cv.pdf",
        mime_type="application/pdf",
    )
    assert is_valid_resume(doc)


def test_valid_docx_mime():
    doc = make_doc(
        file_name="cv.docx",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert is_valid_resume(doc)


def test_valid_by_extension_only():
    doc = make_doc(
        file_name="resume.docx",
        mime_type="application/octet-stream",
    )
    assert is_valid_resume(doc)


def test_invalid_extension():
    doc = make_doc(
        file_name="virus.exe",
        mime_type="application/octet-stream",
    )
    assert not is_valid_resume(doc)


def test_too_large_file():
    doc = make_doc(
        file_name="cv.pdf",
        mime_type="application/pdf",
        file_size=25 * 1024 * 1024,
    )
    assert not is_valid_resume(doc)
