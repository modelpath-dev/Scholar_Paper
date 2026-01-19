import fitz  # PyMuPDF
import re
from typing import Dict

def extract_text_by_section(pdf_path: str) -> Dict[str, str]:
    """
    Extracts text from a PDF and attempts to split it into sections 
    (Abstract, Introduction, Methods, Results, Conclusion).
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
    
    sections = {}
    
    # Define section headers to look for (common in research papers)
    # Using regex to find headers at the start of a line
    headers = ["Abstract", "Introduction", "Methods", "Results", "Conclusion", "References"]
    
    # Find positions of headers
    positions = []
    for header in headers:
        match = re.search(rf"^\s*{header}\s*$", full_text, re.MULTILINE | re.IGNORECASE)
        if match:
            positions.append((match.start(), header))
            
    # Sort positions by their appearance in the text
    positions.sort()
    
    # Extract text between headers
    for i in range(len(positions)):
        start_pos, section_name = positions[i]
        end_pos = positions[i+1][0] if i + 1 < len(positions) else len(full_text)
        
        # Don't store References as a concept section usually
        if section_name.lower() == "references":
            continue
            
        content = full_text[start_pos:end_pos].strip()
        # Remove the header itself from the content start
        content = re.sub(rf"^\s*{section_name}\s*", "", content, count=1, flags=re.IGNORECASE).strip()
        
        if content:
            sections[section_name] = content
            
    # Fallback if no sections detected
    if not sections:
        sections["Full Content"] = full_text[:10000] # Limit size for LLM

    return sections

if __name__ == "__main__":
    # Test on one of the provided PDFs
    test_pdf = "rp1.pdf"
    try:
        res = extract_text_by_section(test_pdf)
        for section, text in res.items():
            print(f"--- {section} ({len(text)} chars) ---")
            print(text[:200] + "...")
    except Exception as e:
        print(f"Error parsing PDF: {e}")
