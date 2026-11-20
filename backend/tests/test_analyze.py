"""Tests for PrepPilot's resume analysis endpoint."""

from io import BytesIO

import pytest
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

from app import create_app


def sample_pdf():
    """Build a small, readable resume PDF entirely in memory."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})
    })
    content = DecodedStreamObject()
    content.set_data(b"BT /F1 14 Tf 50 700 Td (Python Flask) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(content)

    pdf = BytesIO()
    writer.write(pdf)
    pdf.seek(0)
    return pdf


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Prevent real AI requests: only the analysis API is under test.
    monkeypatch.setattr("app.llm.suggestions", lambda *args: "Mocked suggestions")
    app = create_app(str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        response = test_client.post("/api/register", json={
            "email": "tester@example.com", "password": "password123"
        })
        assert response.status_code == 200
        token = response.get_json()["token"]
        yield test_client, {"Authorization": f"Bearer {token}"}


def test_analyze_happy_path(client):
    test_client, headers = client
    response = test_client.post("/api/analyze", headers=headers, data={
        "resume": (sample_pdf(), "resume.pdf"),
        "jd": "Looking for Python, Flask, and Docker experience.",
    })
    result = response.get_json()

    assert response.status_code == 200
    assert result["score"] == 67
    assert result["matched"] == ["flask", "python"]
    assert result["missing"] == ["docker"]
    assert result["tips"] == "Mocked suggestions"
    assert isinstance(result["id"], int)


def test_analyze_rejects_empty_job_description(client):
    test_client, headers = client
    response = test_client.post("/api/analyze", headers=headers, data={
        "resume": (sample_pdf(), "resume.pdf"),
        "jd": "   ",
    })
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_analyze_rejects_non_pdf_file(client):
    test_client, headers = client
    response = test_client.post("/api/analyze", headers=headers, data={
        "resume": (BytesIO(b"This is a text file, not a PDF."), "resume.txt"),
        "jd": "Python developer",
    })
    assert response.status_code == 400
    assert "error" in response.get_json()
