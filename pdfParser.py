import pdfplumber

def extract_routes(pdf_path):
    routes = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for line in text.split("\n"):
                # crude filter: look for NH routes
                if "NH" in line and "-" in line:
                    # Example: "NH-2 Delhi - Kanpur - Allahabad - Kolkata"
                    parts = line.split("-")
                    cities = [p.strip() for p in parts[1:]]  # skip "NH-2"
                    if len(cities) > 1:
                        routes.append(cities)
    return routes
