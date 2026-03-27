from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from models import Assignment, AssignmentSubmission, User
from database import get_db
from middleware import permission_required, get_user_from_session

# Pydantic models
class AttachmentSchema(BaseModel):
    name: str
    url: str

class GradeSubmissionRequest(BaseModel):
    grade: float = Field(..., gt=0, le=100)
    feedback: Optional[str] = None

class AssignmentBase(BaseModel):
    title: str
    courseCode: str
    courseTitle: str
    semester: int
    batch: str
    deadline: datetime
    description: str
    attachments: Optional[List[AttachmentSchema]] = None
    submissionType: str  # "file" | "link" | "text"
    status: str  # "active" | "past" | "draft"

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentResponse(AssignmentBase):
    id: int
    facultyName: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class SubmissionBase(BaseModel):
    assignmentId: int
    submissionContent: str
    submissionType: str  # "file" | "link" | "text"

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionResponse(SubmissionBase):
    id: int
    studentId: int
    submittedAt: datetime
    status: str
    grade: Optional[float] = None
    feedback: Optional[str] = None
    gradedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

router = APIRouter(prefix="/api/assignments", tags=["assignments"])

# Mock data for faculty assignments
mock_faculty_assignments = [
    {
        "id": 1,
        "title": "Database Normalization",
        "courseCode": "CSE303",
        "courseTitle": "Database Systems",
        "semester": 3,
        "batch": "2023",
        "deadline": datetime.now() + timedelta(days=7),
        "description": "Normalize the given database schema to 3NF and explain your steps.",
        "attachments": [
            {"name": "assignment1.pdf", "url": "/assets/assignments/assignment1.pdf"}
        ],
        "submissionType": "file",
        "status": "active",
        "facultyName": "Dr. Md. Shabbir Ahmed",
        "createdAt": datetime.now() - timedelta(days=2),
        "updatedAt": datetime.now() - timedelta(days=2),
        "submissionCount": 18,
        "totalStudents": 38
    },
    {
        "id": 2,
        "title": "AI Search Algorithms",
        "courseCode": "CSE405",
        "courseTitle": "Artificial Intelligence",
        "semester": 4,
        "batch": "2023",
        "deadline": datetime.now() + timedelta(days=5),
        "description": "Implement A* search algorithm for the 8-puzzle problem and analyze its performance.",
        "attachments": [
            {"name": "assignment2.pdf", "url": "/assets/assignments/assignment2.pdf"},
            {"name": "starter_code.py", "url": "/assets/assignments/starter_code.py"}
        ],
        "submissionType": "file",
        "status": "active",
        "facultyName": "Dr. Md. Shabbir Ahmed",
        "createdAt": datetime.now() - timedelta(days=3),
        "updatedAt": datetime.now() - timedelta(days=3),
        "submissionCount": 12,
        "totalStudents": 32
    },
    {
        "id": 3,
        "title": "Introduction to Programming",
        "courseCode": "CSE101",
        "courseTitle": "Introduction to Computer Science",
        "semester": 1,
        "batch": "2024",
        "deadline": datetime.now() - timedelta(days=10),
        "description": "Write a program to calculate factorial of a number using recursion.",
        "attachments": [],
        "submissionType": "file",
        "status": "past",
        "facultyName": "Dr. Md. Shabbir Ahmed",
        "createdAt": datetime.now() - timedelta(days=20),
        "updatedAt": datetime.now() - timedelta(days=20),
        "submissionCount": 40,
        "totalStudents": 45
    }
]

# Mock data for student submissions
mock_submissions = [
    {
        "id": 1,
        "assignmentId": 1,
        "studentId": 101,
        "studentName": "Md. Rakib Hasan",
        "studentRoll": "ASH2101",
        "submissionContent": "submission1.pdf",
        "submissionType": "file",
        "submittedAt": datetime.now() - timedelta(days=1),
        "status": "submitted",
        "grade": None,
        "feedback": None,
        "gradedAt": None
    },
    {
        "id": 2,
        "assignmentId": 1,
        "studentId": 102,
        "studentName": "Fatima Akter",
        "studentRoll": "ASH2102",
        "submissionContent": "submission2.pdf",
        "submissionType": "file",
        "submittedAt": datetime.now() - timedelta(days=2),
        "status": "submitted",
        "grade": None,
        "feedback": None,
        "gradedAt": None
    },
    {
        "id": 3,
        "assignmentId": 2,
        "studentId": 101,
        "studentName": "Md. Rakib Hasan",
        "studentRoll": "ASH2101",
        "submissionContent": "submission3.py",
        "submissionType": "file",
        "submittedAt": datetime.now() - timedelta(days=1),
        "status": "submitted",
        "grade": None,
        "feedback": None,
        "gradedAt": None
    },
    {
        "id": 4,
        "assignmentId": 3,
        "studentId": 103,
        "studentName": "Abdul Karim",
        "studentRoll": "ASH2103",
        "submissionContent": "submission4.py",
        "submissionType": "file",
        "submittedAt": datetime.now() - timedelta(days=15),
        "status": "graded",
        "grade": 85.0,
        "feedback": "Good implementation of recursion. Could improve code documentation.",
        "gradedAt": datetime.now() - timedelta(days=12)
    },
    {
        "id": 5,
        "assignmentId": 3,
        "studentId": 104,
        "studentName": "Nusrat Jahan",
        "studentRoll": "ASH2104",
        "submissionContent": "submission5.py",
        "submissionType": "file",
        "submittedAt": datetime.now() - timedelta(days=14),
        "status": "graded",
        "grade": 92.0,
        "feedback": "Excellent work! Clean code and efficient implementation.",
        "gradedAt": datetime.now() - timedelta(days=12)
    }
]

# ============= Faculty-specific endpoints =============
# These routes need to be defined before any dynamic routes with path parameters

@router.get("/faculty", response_model=List[dict])
def get_faculty_assignments(
    course_code: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Get all assignments created by the faculty member"""
    # In a real implementation, we would filter by the faculty ID
    # For now, return mock data
    
    # Filter by course code if provided
    filtered_assignments = mock_faculty_assignments
    if course_code:
        filtered_assignments = [a for a in filtered_assignments if a["courseCode"] == course_code]
    
    # Filter by status if provided
    if status:
        filtered_assignments = [a for a in filtered_assignments if a["status"] == status]
    
    return filtered_assignments

@router.post("/faculty", response_model=dict)
def create_faculty_assignment(
    assignment: AssignmentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Create a new assignment as a faculty member"""
    # Validate deadline
    if assignment.deadline < datetime.now():
        raise HTTPException(status_code=400, detail="Assignment deadline cannot be in the past")
    
    # Create a new assignment with mock data
    new_assignment = {
        "id": len(mock_faculty_assignments) + 1,
        **assignment.dict(),
        "facultyName": user.get("name", "Faculty User"),
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "submissionCount": 0,
        "totalStudents": 45
    }
    
    # Add to mock data
    mock_faculty_assignments.append(new_assignment)
    
    return new_assignment

@router.get("/faculty/{assignment_id}", response_model=dict)
def get_faculty_assignment_detail(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Get details of a specific assignment created by the faculty member"""
    # Find the assignment in mock data
    assignment = next((a for a in mock_faculty_assignments if a["id"] == assignment_id), None)
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return assignment

@router.get("/faculty/{assignment_id}/submissions", response_model=List[dict])
def get_faculty_assignment_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Get all submissions for a specific assignment"""
    # Filter submissions for the given assignment
    submissions = [s for s in mock_submissions if s["assignmentId"] == assignment_id]
    
    return submissions

@router.put("/faculty/submissions/{submission_id}/grade", response_model=dict)
def grade_faculty_submission(
    submission_id: int,
    grade_data: GradeSubmissionRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Grade a student submission"""
    # Find the submission in mock data
    submission = next((s for s in mock_submissions if s["id"] == submission_id), None)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Update the submission with grade data
    submission["grade"] = grade_data.grade
    submission["feedback"] = grade_data.feedback
    submission["gradedAt"] = datetime.now()
    submission["status"] = "graded"
    
    return submission

# Routes
@router.get("", response_model=List[AssignmentResponse])
def get_assignments(db: Session = Depends(get_db)):
    """Get all assignments"""
    assignments = db.query(Assignment).all()
    return assignments

@router.get("/my-submissions", response_model=List[SubmissionResponse])
def get_my_submissions(
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Get all submissions for the current user"""
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.studentId == user["id"]
    ).all()
    
    return submissions

@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Get a specific assignment by ID"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@router.post("", response_model=AssignmentResponse)
def create_assignment(
    assignment: AssignmentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Create a new assignment (requires MANAGE_ASSIGNMENTS permission)"""
    # Check if deadline is in the past
    if assignment.deadline < datetime.now():
        raise HTTPException(
            status_code=400, 
            detail="Assignment deadline cannot be in the past"
        )
    
    # Get faculty name from user
    faculty = db.query(User).filter(User.id == user["id"]).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty user not found")
    
    # Create new assignment
    db_assignment = Assignment(
        title=assignment.title,
        courseCode=assignment.courseCode,
        courseTitle=assignment.courseTitle,
        semester=assignment.semester,
        batch=assignment.batch,
        deadline=assignment.deadline,
        description=assignment.description,
        attachments=assignment.attachments,
        submissionType=assignment.submissionType,
        status=assignment.status,
        facultyId=user["id"],
        facultyName=faculty.name
    )
    
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: int,
    assignment_update: AssignmentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Update an existing assignment (requires MANAGE_ASSIGNMENTS permission)"""
    # Find the assignment
    db_assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if the user is the faculty who created the assignment
    if db_assignment.facultyId != user["id"]:
        raise HTTPException(
            status_code=403, 
            detail="You can only update assignments that you created"
        )
    
    # Update assignment fields
    for field, value in assignment_update.dict().items():
        setattr(db_assignment, field, value)
    
    # Update timestamps
    db_assignment.updatedAt = datetime.utcnow()
    
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.delete("/{assignment_id}", status_code=204)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Delete an assignment (requires MANAGE_ASSIGNMENTS permission)"""
    # Find the assignment
    db_assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if the user is the faculty who created the assignment
    if db_assignment.facultyId != user["id"]:
        raise HTTPException(
            status_code=403, 
            detail="You can only delete assignments that you created"
        )
    
    # Delete the assignment
    db.delete(db_assignment)
    db.commit()
    return {"detail": "Assignment deleted successfully"}

@router.post("/submit", response_model=SubmissionResponse)
def submit_assignment(
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """
    Submit an assignment - IMPORTANT: Permission checks have been intentionally removed.
    Any authenticated user can submit assignments as requested.
    Only authentication (valid session) is required.
    """
    # Check if assignment exists
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignmentId).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if deadline has passed
    if assignment.deadline < datetime.now():
        # Allow submission but mark as late
        submission_status = "late"
    else:
        submission_status = "submitted"
    
    # Check if student has already submitted
    existing_submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignmentId == submission.assignmentId,
        AssignmentSubmission.studentId == user["id"]
    ).first()
    
    if existing_submission:
        # Update existing submission
        existing_submission.submissionContent = submission.submissionContent
        existing_submission.submissionType = submission.submissionType
        existing_submission.submittedAt = datetime.utcnow()
        existing_submission.status = submission_status
        db.commit()
        db.refresh(existing_submission)
        return existing_submission
    else:
        # Create new submission
        db_submission = AssignmentSubmission(
            assignmentId=submission.assignmentId,
            studentId=user["id"],
            submissionContent=submission.submissionContent,
            submissionType=submission.submissionType,
            submittedAt=datetime.utcnow(),
            status=submission_status
        )
        db.add(db_submission)
        db.commit()
        db.refresh(db_submission)
        return db_submission

@router.get("/submissions/{assignment_id}", response_model=List[SubmissionResponse])
def get_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Get all submissions for an assignment (no permission check)"""
    # Check if assignment exists and belongs to the faculty
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if assignment.facultyId != user["id"]:
        raise HTTPException(
            status_code=403, 
            detail="You can only view submissions for assignments that you created"
        )
    
    # Get all submissions for the assignment
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignmentId == assignment_id
    ).all()
    
    return submissions

@router.put("/submissions/{submission_id}/grade", response_model=SubmissionResponse)
def grade_submission(
    submission_id: int,
    grade_data: GradeSubmissionRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    # Check if user has permission to grade assignments
    if "MANAGE_ASSIGNMENTS" not in user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to grade assignments"
        )
    
    # Get the submission
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Update the submission with grade data
    submission.grade = grade_data.grade
    submission.feedback = grade_data.feedback
    submission.gradedAt = datetime.now()
    submission.status = "graded"
    
    db.commit()
    db.refresh(submission)
    
    return submission

# Faculty-specific endpoints
# These routes need to be defined before the dynamic /{assignment_id} routes
@router.get("/faculty", response_model=List[dict])
def get_faculty_assignments(
    course_code: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Get all assignments created by the faculty member"""
    # In a real implementation, we would filter by the faculty ID
    # For now, return mock data
    
    # Filter by course code if provided
    filtered_assignments = mock_faculty_assignments
    if course_code:
        filtered_assignments = [a for a in filtered_assignments if a["courseCode"] == course_code]
    
    # Filter by status if provided
    if status:
        filtered_assignments = [a for a in filtered_assignments if a["status"] == status]
    
    return filtered_assignments

@router.get("/faculty/{assignment_id}", response_model=dict)
def get_faculty_assignment_detail(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Get details of a specific assignment created by the faculty member"""
    # Find the assignment in mock data
    assignment = next((a for a in mock_faculty_assignments if a["id"] == assignment_id), None)
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return assignment

@router.get("/faculty/{assignment_id}/submissions", response_model=List[dict])
def get_faculty_assignment_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Get all submissions for a specific assignment"""
    # Filter submissions for the given assignment
    submissions = [s for s in mock_submissions if s["assignmentId"] == assignment_id]
    
    return submissions

@router.post("/faculty", response_model=dict)
def create_faculty_assignment(
    assignment: AssignmentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Create a new assignment as a faculty member"""
    # In a real implementation, we would save to the database
    # For now, just return a mock response with an ID
    
    # Check if deadline is in the past
    if assignment.deadline < datetime.now():
        raise HTTPException(
            status_code=400, 
            detail="Assignment deadline cannot be in the past"
        )
    
    # Create a new assignment with a mock ID
    new_assignment = {
        "id": len(mock_faculty_assignments) + 1,
        **assignment.dict(),
        "facultyName": user.get("name", "Faculty User"),
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "submissionCount": 0,
        "totalStudents": 45  # Mock value
    }
    
    # In a real implementation, we would save to the database
    # For now, just add to our mock list
    mock_faculty_assignments.append(new_assignment)
    
    return new_assignment

@router.put("/faculty/submissions/{submission_id}/grade", response_model=dict)
def grade_faculty_submission(
    submission_id: int,
    grade_data: GradeSubmissionRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Grade a student submission as a faculty member"""
    # Find the submission in mock data
    submission = next((s for s in mock_submissions if s["id"] == submission_id), None)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Update the submission with grade data
    submission["grade"] = grade_data.grade
    submission["feedback"] = grade_data.feedback
    submission["gradedAt"] = datetime.now()
    submission["status"] = "graded"
    
    return submission

@router.post("/grade/{submission_id}", response_model=SubmissionResponse)
def grade_submission(
    submission_id: int,
    grade_data: GradeSubmissionRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """Grade a submission (requires MANAGE_ASSIGNMENTS permission)"""
    # Find the submission
    submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Check if the assignment belongs to the faculty
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignmentId).first()
    if not assignment or assignment.facultyId != user["id"]:
        raise HTTPException(
            status_code=403, 
            detail="You can only grade submissions for assignments that you created"
        )
    
    # Update submission with grade
    submission.grade = grade_data.grade
    submission.feedback = grade_data.feedback
    submission.status = "graded"
    submission.gradedAt = datetime.utcnow()
    
    db.commit()
    db.refresh(submission)
    return submission
