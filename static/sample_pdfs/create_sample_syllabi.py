import os
import random
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Create directory if it doesn't exist
output_dir = "static/sample_pdfs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Sample course data
courses = [
    {
        "code": "CSE101",
        "title": "Introduction to Computer Science",
        "credits": 4,
        "year": 1,
        "semester": 1,
        "topics": [
            "Computer Systems Overview",
            "Introduction to Programming",
            "Data Representation",
            "Basic Algorithms",
            "Problem Solving Techniques"
        ]
    },
    {
        "code": "CSE203",
        "title": "Data Structures",
        "credits": 4,
        "year": 2,
        "semester": 1,
        "topics": [
            "Arrays and Linked Lists",
            "Stacks and Queues",
            "Trees and Graphs",
            "Hashing",
            "Algorithm Analysis"
        ]
    },
    {
        "code": "CSE307",
        "title": "Operating Systems",
        "credits": 3,
        "year": 3,
        "semester": 1,
        "topics": [
            "Process Management",
            "Memory Management",
            "File Systems",
            "I/O Systems",
            "Virtualization"
        ]
    },
    {
        "code": "CSE405",
        "title": "Machine Learning",
        "credits": 3,
        "year": 4,
        "semester": 1,
        "topics": [
            "Supervised Learning",
            "Unsupervised Learning",
            "Neural Networks",
            "Deep Learning",
            "Reinforcement Learning"
        ]
    }
]

def create_syllabus_pdf(course):
    """Create a sample syllabus PDF for a course"""
    filename = f"{output_dir}/{course['code']}_syllabus.pdf"
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading1"]
    subheading_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # Content elements
    elements = []
    
    # Title
    elements.append(Paragraph(f"Course Syllabus: {course['code']}", title_style))
    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph(course['title'], heading_style))
    elements.append(Spacer(1, 0.5 * inch))
    
    # Course Information
    elements.append(Paragraph("Course Information", heading_style))
    elements.append(Spacer(1, 0.1 * inch))
    
    course_info = [
        ["Course Code:", course['code']],
        ["Course Title:", course['title']],
        ["Credits:", str(course['credits'])],
        ["Year:", f"Year {course['year']}"],
        ["Semester:", f"Semester {course['semester']}"],
        ["Department:", "Computer Science and Engineering"],
        ["Institution:", "University of Dhaka"]
    ]
    
    # Create a table for course information
    info_table = Table(course_info, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Course Description
    elements.append(Paragraph("Course Description", heading_style))
    elements.append(Spacer(1, 0.1 * inch))
    
    descriptions = {
        "CSE101": "This course introduces fundamental concepts of computer science including algorithms, programming, and computer organization. Students will learn basic problem-solving techniques and develop simple programs.",
        "CSE203": "This course covers fundamental data structures and algorithms used in computer science. Students will learn how to analyze, design, and implement efficient data structures and algorithms.",
        "CSE307": "This course explores the principles and design of operating systems. Topics include process management, memory management, file systems, and security considerations.",
        "CSE405": "This course provides an introduction to machine learning concepts and techniques. Students will learn about supervised and unsupervised learning algorithms and their applications."
    }
    
    elements.append(Paragraph(descriptions.get(course['code'], "Course description not available."), normal_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Course Objectives
    elements.append(Paragraph("Learning Objectives", heading_style))
    elements.append(Spacer(1, 0.1 * inch))
    
    objectives = [
        "Understand core concepts and principles related to the subject matter",
        "Develop practical skills in applying theoretical knowledge",
        "Analyze and solve complex problems in the field",
        "Communicate ideas and solutions effectively",
        "Work collaboratively in team-based projects"
    ]
    
    for obj in objectives:
        elements.append(Paragraph(f"• {obj}", normal_style))
        elements.append(Spacer(1, 0.05 * inch))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Course Topics
    elements.append(Paragraph("Course Topics", heading_style))
    elements.append(Spacer(1, 0.1 * inch))
    
    for i, topic in enumerate(course['topics']):
        elements.append(Paragraph(f"{i+1}. {topic}", normal_style))
        elements.append(Spacer(1, 0.05 * inch))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Assessment
    elements.append(Paragraph("Assessment", heading_style))
    elements.append(Spacer(1, 0.1 * inch))
    
    assessment = [
        ["Component", "Weight"],
        ["Midterm Examination", "30%"],
        ["Final Examination", "40%"],
        ["Assignments", "15%"],
        ["Lab Work", "10%"],
        ["Attendance", "5%"]
    ]
    
    assessment_table = Table(assessment, colWidths=[3*inch, 2*inch])
    assessment_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(assessment_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Textbooks
    elements.append(Paragraph("Recommended Textbooks", heading_style))
    elements.append(Spacer(1, 0.1 * inch))
    
    textbooks = {
        "CSE101": [
            "Introduction to Computer Science using Python by Charles Dierbach",
            "Computer Science: An Overview by Glenn Brookshear"
        ],
        "CSE203": [
            "Data Structures and Algorithm Analysis in C++ by Mark Allen Weiss",
            "Introduction to Algorithms by Cormen, Leiserson, Rivest, and Stein"
        ],
        "CSE307": [
            "Operating System Concepts by Silberschatz, Galvin, and Gagne",
            "Modern Operating Systems by Andrew S. Tanenbaum"
        ],
        "CSE405": [
            "Pattern Recognition and Machine Learning by Christopher Bishop",
            "Deep Learning by Ian Goodfellow, Yoshua Bengio, and Aaron Courville"
        ]
    }
    
    for book in textbooks.get(course['code'], ["Textbook information not available"]):
        elements.append(Paragraph(f"• {book}", normal_style))
        elements.append(Spacer(1, 0.05 * inch))
    
    # Build the PDF
    doc.build(elements)
    return filename

# Create syllabi for all courses
for course in courses:
    filename = create_syllabus_pdf(course)
    print(f"Created syllabus: {filename}")

print("All sample syllabi created successfully!")
