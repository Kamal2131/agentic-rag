#!/usr/bin/env python
"""
Django management command to ingest PDFs.
Run with: python manage.py ingest_pdfs raw_data
"""
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.knowledgebase.services import DocumentService


class Command(BaseCommand):
    help = "Ingest PDF files from a directory into the vector database"

    def add_arguments(self, parser):
        parser.add_argument(
            "directory",
            type=str,
            default="raw_data",
            help="Directory containing PDF files to ingest",
        )

    def handle(self, *args, **options):
        directory_path = options["directory"]
        doc_service = DocumentService()
        directory = Path(directory_path)

        if not directory.exists():
            self.stdout.write(self.style.ERROR(f"❌ Directory not found: {directory_path}"))
            return

        # Find all PDF files
        pdf_files = list(directory.glob("*.pdf"))

        if not pdf_files:
            self.stdout.write(self.style.WARNING(f"⚠️  No PDF files found in {directory_path}"))
            return

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("🚀 PDF Ingestion"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"📁 Directory: {directory_path}")
        self.stdout.write(f"📚 Found {len(pdf_files)} PDF file(s) to ingest\n")

        # Process each PDF
        success_count = 0
        error_count = 0

        for i, pdf_path in enumerate(pdf_files, 1):
            self.stdout.write(f"[{i}/{len(pdf_files)}] Processing: {pdf_path.name}")

            try:
                # Open PDF file
                with open(pdf_path, "rb") as pdf_file:
                    # Extract metadata from filename
                    title = pdf_path.stem.replace("-", " ").replace("_", " ")

                    # Add metadata
                    metadata = {
                        "source": directory_path,
                        "filename": pdf_path.name,
                        "category": "apple_business",
                        "type": "financial_filing" if "10-" in pdf_path.name else "document",
                    }

                    # Process PDF
                    document = doc_service.process_pdf(
                        file_obj=pdf_file, title=title, metadata=metadata
                    )

                    self.stdout.write(
                        self.style.SUCCESS(f"   ✅ Successfully ingested: {document.title}")
                    )
                    self.stdout.write(f"   📄 Document ID: {document.id}")
                    self.stdout.write(
                        f"   📊 Content length: {len(document.content)} characters\n"
                    )
                    success_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Error processing {pdf_path.name}: {e}\n"))
                import traceback

                traceback.print_exc()
                error_count += 1
                continue

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS(f"✨ Ingestion complete!"))
        self.stdout.write(f"✅ Successfully ingested: {success_count}")
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f"❌ Errors: {error_count}"))
        self.stdout.write("=" * 60)
