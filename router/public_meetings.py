                "id": meeting.faculty_id,
                "name": faculty_name or "Unknown Faculty",
            } if meeting.faculty_id else None,
            "student": {
                "id": meeting.student_id,
                "name": student_name or "Unknown Student",
            } if meeting.student_id else None
        }
        result.append(meeting_dict)
    
    return result
