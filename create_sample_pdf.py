"""Generate a sample logistics PDF for testing"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Sample content
SAMPLE_CONTENT = """
LOGISTICS OPERATIONS MANUAL
Chapter 3: Hazardous Materials Handling

3.1 Hazmat Classification
All hazardous materials must be classified according to IMDG Code standards.
Class 3 materials (flammable liquids) require special storage at Port X.

3.2 Port X Specific Protocols
- Temperature-controlled storage: -5°C to +25°C
- Maximum storage duration: 72 hours
- Required permits: Form HAZ-2024-A
- Contact: Port Safety Officer at +1-555-PORT

3.3 Emergency Procedures
In case of spill:
1. Evacuate area within 50-meter radius
2. Contact emergency line: 555-EMERGENCY
3. Deploy spill containment kit (Location: Dock 4, Bay 12)

""", """
LOGISTICS OPERATIONS MANUAL
Chapter 5: Freight Cost Structure

5.1 Standard Shipping Rates (Effective Jan 2025)
- Container (20ft): $1,200 base + $50/ton
- Container (40ft): $2,000 base + $45/ton
- Refrigerated surcharge: +15%

5.2 Express Shipping
Guaranteed 72-hour delivery available for premium of 25% above standard rates.
Not available for hazmat shipments.

5.3 Port Fees
Port X charges:
- Docking fee: $500/day
- Handling fee: $100/container
- Customs processing: $75/shipment

"""

def create_sample_pdf():
    """Generate a sample logistics PDF"""
    doc = SimpleDocTemplate(
        "data/raw/logistics_manual.pdf",
        pagesize=letter,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=18
    )
    
    Story = []
    styles = getSampleStyleSheet()
    
    for page_content in SAMPLE_CONTENT:
        for line in page_content.strip().split('\n'):
            if line.strip():
                Story.append(Paragraph(line, styles['Normal']))
                Story.append(Spacer(1, 0.2*inch))
        Story.append(PageBreak())
    
    doc.build(Story)
    print("✓ Created sample PDF: data/raw/logistics_manual.pdf")

if __name__ == "__main__":
    # Install reportlab first: pip install reportlab
    create_sample_pdf()