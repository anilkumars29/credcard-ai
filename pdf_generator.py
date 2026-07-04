# CODE ARTIFACT: pdf_generator.py
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def build_sanction_pdf(metrics_data, chat_history):
    buffer = io.BytesIO()
    
    # Page setup with standard professional corporate margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Banking Typography Styles
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=22, leading=26,
        textColor=colors.HexColor('#1e3a8a'), spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14,
        textColor=colors.HexColor('#64748b'), spaceAfter=15
    )
    section_heading = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=colors.HexColor('#0f172a'), spaceBefore=12, spaceAfter=8
    )
    body_style = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=15,
        textColor=colors.HexColor('#334155'), spaceAfter=8
    )
    meta_label = ParagraphStyle('MetaLabel', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor('#1e293b'))
    meta_val = ParagraphStyle('MetaVal', fontName='Helvetica', fontSize=10, leading=12, textColor=colors.HexColor('#2563eb'))

    story = []
    
    # 1. CORPORATE BANKING HEADER BLOCK
    story.append(Paragraph("IDBI BANK MSME CREDIT UNDERWRITING CORE", title_style))
    story.append(Paragraph("CONFIDENTIAL // CREDIT COMMITTEE SANCTION MEMO // GENERATED VIA LLLM", subtitle_style))
    
    # Decorative separation rule
    rule_table = Table([[""]], colWidths=[504], rowHeights=[2])
    rule_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#cbd5e1'))]))
    story.append(rule_table)
    story.append(Spacer(1, 15))
    
    # 2. VERDICT STAMP BANNER
    v_text = metrics_data.get('verdict', 'PENDING REVIEW')
    # Determine background colors based on underwriting outcomes
    if "YES GO" in v_text:
        bg_color, txt_color = colors.HexColor('#dcfce7'), colors.HexColor('#166534')
    elif "MANUAL" in v_text:
        bg_color, txt_color = colors.HexColor('#fef3c7'), colors.HexColor('#92400e')
    else:
        bg_color, txt_color = colors.HexColor('#fee2e2'), colors.HexColor('#991b1b')
        
    stamp_style = ParagraphStyle('Stamp', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=txt_color, alignment=TA_CENTER)
    stamp_table = Table([[Paragraph(f"OFFICIAL RISK ASSESSMENT VERDICT: {v_text}", stamp_style)]], colWidths=[504])
    stamp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_color),
        ('PADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, txt_color)
    ]))
    story.append(stamp_table)
    story.append(Spacer(1, 15))
    
    # 3. CONSOLIDATED SCORECARD METRICS GRID
    story.append(Paragraph("Executive Scorecard Summary", section_heading))
    metrics_matrix = [
        [Paragraph("Trading Entity Legal Name:", meta_label), Paragraph(metrics_data.get('name', '-'), meta_val)],
        [Paragraph("Alternative Credit Index Rating:", meta_label), Paragraph(metrics_data.get('score', '-'), meta_val)],
        [Paragraph("Ecosystem Integrity Density:", meta_label), Paragraph(metrics_data.get('percentage', '-'), meta_val)],
    ]
    grid_table = Table(metrics_matrix, colWidths=[200, 304])
    grid_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
    ]))
    story.append(grid_table)
    story.append(Spacer(1, 15))
    
    # 4. RAW TELEMETRY INPUTS TABLE
    story.append(Paragraph("Ingested Alternative Network Streams", section_heading))
    inputs = metrics_data.get('inputs', {})
    telemetry_matrix = [
        [Paragraph("Metric Stream Vector", meta_label), Paragraph("Reported Value Matrix", meta_label)],
        [Paragraph("Average GST Filing Delays", body_style), Paragraph(f"{inputs.get('gst', '0')} Days", body_style)],
        [Paragraph("Daily UPI Inflow Variance Ratio", body_style), Paragraph(f"{inputs.get('upi', '0')}%", body_style)],
        [Paragraph("Net Corporate Workforce Delta (EPFO)", body_style), Paragraph(f"{inputs.get('staff', '0')} Employees", body_style)],
        [Paragraph("Industrial Power Consumption Slope", body_style), Paragraph(f"{inputs.get('power', '0')} kWh Delta", body_style)],
    ]
    telemetry_table = Table(telemetry_matrix, colWidths=[250, 254])
    telemetry_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(telemetry_table)
    story.append(Spacer(1, 15))
    
    # 5. CONTEXTUAL MEMO TRANSCRIPTS
    if chat_history:
        story.append(Paragraph("AI-Assisted Underwriting Consultation Log", section_heading))
        chat_elements = []
        for msg in chat_history:
            role = msg.get('role')
            content = msg.get('content', '').replace('**', '') # Strips markdown tags for standard clean lines

            # Skip internal ingestion/system messages and also avoid printing the label "[System Response]:"
            if role == 'user' and "Ingest target data" in content:
                continue

            if role == 'assistant' and content.strip() in {"Metrics logged. Processing interactive evaluation thread.", "Ingested successfully"}:
                continue

            if role == 'assistant' and not "Ingested successfully" in content:
                # Print brief + assistant answers as plain text
                chat_elements.append(Paragraph(content, body_style))
                chat_elements.append(Spacer(1, 10))
            elif role == 'user':
                # Keep RM queries if needed
                chat_elements.append(Paragraph(f"<b>[RM Query]:</b> {content}", body_style))
                chat_elements.append(Spacer(1, 4))

        if chat_elements:
            story.append(KeepTogether(chat_elements))

    # 6. Validation warning footer (italic, small font) - always printed
    warning_style = ParagraphStyle(
        'FooterWarning', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=9, leading=11,
        textColor=colors.HexColor('#64748b'), alignment=TA_LEFT
    )
    story.append(Spacer(1, 10))
    story.append(Paragraph("<i>*AI-assisted document. Reviewed and validated by the project team.</i>", warning_style))

    # Build document pipeline safely
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
