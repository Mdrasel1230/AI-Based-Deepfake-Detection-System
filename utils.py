import os
import io
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from app import app


def get_file_extension(filename):
    """Get the file extension from a filename."""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def is_video(extension):
    """Check if the file extension is for a video."""
    video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv']
    return extension.lower() in video_extensions


def generate_report(detection_result, output_path):
    """Generate a PDF report for a detection result."""
    try:
        # Create a PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title_style = styles["Title"]
        elements.append(Paragraph("Deepfake Detection Report", title_style))
        elements.append(Spacer(1, 20))
        
        # Date and Time
        date_style = styles["Normal"]
        date_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"Date and Time: {date_string}", date_style))
        elements.append(Spacer(1, 10))
        
        # Detection Information
        detection_style = styles["Heading2"]
        elements.append(Paragraph("Detection Information", detection_style))
        
        normal_style = styles["Normal"]
        elements.append(Paragraph(f"Detection ID: {detection_result.id}", normal_style))
        elements.append(Paragraph(f"Media Filename: {detection_result.media.original_filename}", normal_style))
        elements.append(Paragraph(f"Media Type: {detection_result.media.media_type}", normal_style))
        elements.append(Paragraph(f"Detection Date: {detection_result.created_at.strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        elements.append(Spacer(1, 20))
        
        # Results
        result_style = styles["Heading2"]
        elements.append(Paragraph("Detection Results", result_style))
        
        result_text = "DEEPFAKE DETECTED" if detection_result.is_deepfake else "AUTHENTIC MEDIA"
        result_color = colors.red if detection_result.is_deepfake else colors.green
        
        result_style = styles["Heading3"]
        result_style.textColor = result_color
        elements.append(Paragraph(result_text, result_style))
        
        confidence_percentage = detection_result.confidence_score * 100
        elements.append(Paragraph(f"Confidence Score: {confidence_percentage:.2f}%", normal_style))
        elements.append(Spacer(1, 20))
        
        # Explanation
        explanation_style = styles["Heading2"]
        elements.append(Paragraph("Technical Explanation", explanation_style))
        
        if detection_result.is_deepfake:
            explanation = """
            This media has been identified as a deepfake. The AI model has detected visual inconsistencies 
            typically associated with synthetically generated or manipulated content. The areas highlighted 
            in the heatmap image below indicate regions where the model detected potential manipulation 
            artifacts.
            """
        else:
            explanation = """
            This media appears to be authentic. The AI model did not detect significant visual inconsistencies 
            typically associated with deepfakes. The heatmap below shows the areas the model analyzed, with 
            no strong indications of manipulation found.
            """
        
        elements.append(Paragraph(explanation, normal_style))
        elements.append(Spacer(1, 20))
        
        # Heatmap
        if detection_result.heatmap_path:
            heatmap_style = styles["Heading2"]
            elements.append(Paragraph("Visual Analysis", heatmap_style))
            
            heatmap_path = os.path.join(app.config['UPLOAD_FOLDER'], detection_result.heatmap_path)
            if os.path.exists(heatmap_path):
                img = ReportImage(heatmap_path, width=450, height=300)
                elements.append(img)
            
            elements.append(Spacer(1, 20))
        
        # Footer
        footer_style = styles["Normal"]
        footer_style.textColor = colors.gray
        elements.append(Paragraph("This report was generated automatically by DeepFake AI Detection System.", footer_style))
        elements.append(Paragraph("For more information or assistance, please contact the system administrator.", footer_style))
        
        # Build the PDF
        doc.build(elements)
        return True
    
    except Exception as e:
        print(f"Error generating report: {e}")
        return False
