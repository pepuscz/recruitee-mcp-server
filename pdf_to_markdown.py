#!/usr/bin/env python3
"""
Simple PDF to Markdown Extractor
Uses enhanced PDF parsing with automatic method selection
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the source directory to the path
sys.path.append('./src')

from recruitee_mcp.server import extract_pdf_text_enhanced

async def pdf_to_markdown(pdf_file, output_file=None, use_ocr=True):
    """
    Extract text from PDF and save to markdown file
    
    Args:
        pdf_file: Path to PDF file
        output_file: Output markdown file (optional, auto-generated if not provided)
        use_ocr: Whether to use OCR for scanned documents
    """
    
    if not os.path.exists(pdf_file):
        print(f"❌ Error: File '{pdf_file}' not found")
        return
    
    # Generate output filename if not provided
    if not output_file:
        base_name = os.path.splitext(os.path.basename(pdf_file))[0]
        output_file = f"{base_name}_extracted.md"
    
    print(f"🔍 Extracting text from: {pdf_file}")
    print(f"📄 Output file: {output_file}")
    print(f"👁️  OCR enabled: {use_ocr}")
    
    # Extract text using enhanced parsing (work with local file directly)
    from recruitee_mcp.server import _extract_with_pdfplumber, _extract_with_pymupdf, _extract_with_pypdf2, _extract_with_ocr, _choose_best_extraction
    
    # Try all methods and choose the best
    results = []
    methods_attempted = []
    
    # Try PDFPlumber
    try:
        result = await _extract_with_pdfplumber(pdf_file)
        if result["success"]:
            results.append(("pdfplumber", result))
            methods_attempted.append("pdfplumber")
    except Exception as e:
        methods_attempted.append("pdfplumber (failed)")
    
    # Try PyMuPDF
    try:
        result = await _extract_with_pymupdf(pdf_file)
        if result["success"]:
            results.append(("pymupdf", result))
            methods_attempted.append("pymupdf")
    except Exception as e:
        methods_attempted.append("pymupdf (failed)")
    
    # Try PyPDF2
    try:
        result = await _extract_with_pypdf2(pdf_file)
        if result["success"]:
            results.append(("pypdf2", result))
            methods_attempted.append("pypdf2")
    except Exception as e:
        methods_attempted.append("pypdf2 (failed)")
    
    # Try OCR if enabled
    if use_ocr:
        try:
            result = await _extract_with_ocr(pdf_file)
            if result["success"]:
                results.append(("ocr", result))
                methods_attempted.append("ocr")
        except Exception as e:
            methods_attempted.append("ocr (failed)")
    
    # Choose best result
    if results:
        method_used, result = _choose_best_extraction(results)
        result["method_used"] = method_used
        result["methods_attempted"] = methods_attempted
    else:
        result = {
            "success": False,
            "error": "All extraction methods failed",
            "methods_attempted": methods_attempted
        }
    
    if not result.get("success"):
        print(f"❌ Extraction failed: {result.get('error', 'Unknown error')}")
        return
    
    # Get extraction info
    method_used = result.get("method_used", "unknown")
    char_count = result.get("character_count", 0)
    word_count = result.get("word_count", 0)
    page_count = result.get("page_count", 0)
    
    print(f"✅ Extraction successful using {method_used}")
    print(f"📊 Stats: {char_count:,} chars, {word_count:,} words, {page_count} pages")
    
    # Create markdown content
    markdown_content = f"""# {os.path.splitext(os.path.basename(pdf_file))[0]}

**Extracted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Source:** {pdf_file}  
**Method:** {method_used}  
**Stats:** {char_count:,} characters, {word_count:,} words, {page_count} pages

---

{result['full_text']}

---

*Text extracted using Enhanced PDF Parsing*
"""
    
    # Write to markdown file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        file_size = os.path.getsize(output_file)
        print(f"💾 Saved to: {output_file} ({file_size:,} bytes)")
        
    except Exception as e:
        print(f"❌ Error writing file: {e}")

def main():
    """Main function with command line interface"""
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_markdown.py <pdf_file> [output_file] [--no-ocr]")
        print("")
        print("Examples:")
        print("  python pdf_to_markdown.py document.pdf")
        print("  python pdf_to_markdown.py document.pdf extracted.md")
        print("  python pdf_to_markdown.py document.pdf --no-ocr")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = None
    use_ocr = True
    
    # Parse arguments
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--no-ocr":
            use_ocr = False
        elif not arg.startswith("--") and output_file is None:
            output_file = arg
    
    # Run the extraction
    asyncio.run(pdf_to_markdown(pdf_file, output_file, use_ocr))

if __name__ == "__main__":
    main() 