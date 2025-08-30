# app/routes/session2_classlist.py

from flask import Blueprint, render_template, request
from app.services.classlist_service import get_classlist_data

session2_bp = Blueprint("session2_classlist", __name__, template_folder="../templates/session2")

@session2_bp.route("/classlist", methods=["GET", "POST"])
def classlist_view():
    selected_subject = request.form.get("subject")
    selected_semester = request.form.get("semester")

    try:
        classlist = get_classlist_data(subject=selected_subject, semester=selected_semester)
        subjects = sorted(set(item['SubjectCode'] for item in classlist))
        semesters = sorted(set(item['Semester'] for item in classlist))

        return render_template("session2/classlist.html",
                               classlist=classlist,
                               subjects=subjects,
                               semesters=semesters,
                               selected_subject=selected_subject,
                               selected_semester=selected_semester)
    except Exception as e:
        return f"Error fetching class list: {str(e)}", 500
