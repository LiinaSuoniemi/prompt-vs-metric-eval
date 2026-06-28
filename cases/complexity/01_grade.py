def assign_grade(score, attendance, late_days, extra_credit, retake):
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"
    if attendance < 0.75:
        if grade in ("A", "B"):
            grade = "C"
        elif grade == "C":
            grade = "D"
    if late_days > 5 and grade != "F":
        grade = "D"
    if extra_credit and grade != "A":
        grade = "B"
    if retake and grade == "F":
        grade = "D"
    return grade
