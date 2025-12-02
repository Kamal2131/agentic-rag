"""
Verification script for PDF ingestion.
"""

import io
import os

import django
import pypdf
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.knowledgebase.models import Document  # noqa: E402
from apps.vectorstore.services import QdrantService  # noqa: E402


def create_dummy_pdf():
    """Create a dummy PDF file for testing."""
    buffer = io.BytesIO()
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=72, height=72)

    # Add some text (simulated, as pypdf writing text is complex)
    # For this test, we'll rely on the fact that we can upload it,
    # even if extraction yields empty text for a blank page.
    # To make it real, we'd need reportlab, but let's try to mock the extraction or use a real file.
    # Actually, let's just use a text file masquerading as PDF for the service test
    # OR better, let's mock the PdfReader in the service if we want to avoid reportlab dependency.

    # Wait, we installed pypdf. Let's try to write a minimal valid PDF.
    writer.write(buffer)
    return buffer.getvalue()


def verify():
    print("Starting Ingestion Verification...")

    # 1. Mock PDF Content
    # Since generating a PDF with text via pypdf is hard without reportlab,
    # and we want to verify the *flow*, we will create a dummy PDF.
    # However, our service expects to extract text.
    # If extraction fails/returns empty, that's a case to handle.

    # Let's create a simple PDF using a raw string structure if possible,
    # or just skip the PDF generation complexity and test the service logic directly with a mock if needed.
    # BUT, we want to test the full flow.

    # Alternative: Create a text file and modify the service to accept it?
    # No, the requirement is PDF.

    # Let's use a minimal valid PDF byte string.
    # This is a minimal PDF with "Hello World"
    pdf_content = b"%PDF-1.7\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<<>>/Contents 4 0 R>>\nendobj\n4 0 obj\n<</Length 21>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000117 00000 n\n0000000224 00000 n\ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n294\n%%EOF\n"

    file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")

    # 2. Test API Upload
    print("\n1. Testing API Upload...")
    from rest_framework.test import APIClient

    client = APIClient()

    # We need to seek to 0 if we read it before, but here we just created it.
    file.seek(0)

    response = client.post(
        "/api/knowledgebase/documents/upload/",
        {"file": file, "title": "Test PDF"},
        format="multipart",
        HTTP_HOST="localhost",
    )

    # view = DocumentViewSet.as_view({'post': 'upload'})
    # response = view(request)

    if response.status_code == 201:
        print("✅ Upload successful")
        doc_id = response.data["id"]
        print(f"   Document ID: {doc_id}")
        print(f"   Title: {response.data['title']}")

        # 3. Verify Database
        print("\n2. Verifying Database...")
        doc = Document.objects.get(id=doc_id)
        print(f"✅ Document found in DB: {doc.title}")
        # Note: Our minimal PDF might not extract text correctly with pypdf if fonts aren't standard,
        # but let's check.
        print(f"   Content length: {len(doc.content)}")

        # 4. Verify Vector Store
        print("\n3. Verifying Vector Store...")
        qdrant = QdrantService()
        # We search for the document ID in the payload
        results = qdrant.client.scroll(
            collection_name=QdrantService.COLLECTION_NAME,
            scroll_filter={"must": [{"key": "document_id", "match": {"value": str(doc_id)}}]},
            limit=1,
        )

        if results[0]:
            print("✅ Vectors found in Qdrant")
            print(f"   Chunk content: {results[0][0].payload.get('content', '')[:50]}...")
        else:
            print("❌ No vectors found in Qdrant")

    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        # print(response.data)


if __name__ == "__main__":
    verify()
