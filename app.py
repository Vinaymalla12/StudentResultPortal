from flask import Flask, render_template, request
import pandas as pd
import os
import re

app = Flask(__name__)

# Map semester -> file
SEM_FILES = {
    "1": "sem1rslts.xls",
    "4": "sem4rslts.xls",
    "6": "sem6rslts.xlsx"
}

# Grades that count as backlog
BACKLOG_GRADES = {"F", "S"}

def parse_credits(val):
    """Parse a Credits cell into a float sum."""
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if s == "":
        return 0.0
    nums = re.findall(r'\d+(?:\.\d+)?', s)
    return sum(float(n) for n in nums) if nums else 0.0

@app.route("/", methods=["GET", "POST"])
def index():
    reg_no = None
    semester = None
    name = None
    result_html = None
    error = None
    total_credits = 0.0
    backlog_count = 0

    if request.method == "POST":
        reg_no = request.form.get("reg_no", "").strip()
        semester = request.form.get("semester", "")

        try:
            # If "all", combine all semester files
            if semester.lower() == "all":
                all_students = []
                for sem, file_path in SEM_FILES.items():
                    if os.path.exists(file_path):
                        df = pd.read_excel(file_path, dtype=str)
                        df.columns = [c.strip() for c in df.columns]
                        df["Reg_No"] = df["Reg_No"].astype(str).str.strip()
                        student = df[df["Reg_No"] == reg_no]
                        if not student.empty:
                            all_students.append(student)
                            if name is None:
                                name = student.iloc[0].get("Name", "")
                if all_students:
                    student = pd.concat(all_students, ignore_index=True)
                    display_cols = [c for c in ["Subject_Name", "Grade", "Credits"] if c in student.columns]
                    result_html = student[display_cols].to_html(index=False)

                    non_backlog = student[~student["Grade"].astype(str).str.strip().str.upper().isin(BACKLOG_GRADES)]
                    total_credits = non_backlog["Credits"].apply(parse_credits).sum()
                    backlog_count = student["Grade"].astype(str).str.strip().str.upper().isin(BACKLOG_GRADES).sum()
                else:
                    error = f"No record found for Reg_No {reg_no} in any semester."
            else:
                # Single semester view
                file_path = SEM_FILES.get(semester)
                if not file_path or not os.path.exists(file_path):
                    raise FileNotFoundError(f"Semester {semester} result file not found.")
                
                df = pd.read_excel(file_path, dtype=str)
                df.columns = [c.strip() for c in df.columns]
                df["Reg_No"] = df["Reg_No"].astype(str).str.strip()
                student = df[df["Reg_No"] == reg_no]

                if not student.empty:
                    name = student.iloc[0].get("Name", "")
                    display_cols = [c for c in ["Subject_Name", "Grade", "Credits"] if c in student.columns]
                    result_html = student[display_cols].to_html(index=False)

                    non_backlog = student[~student["Grade"].astype(str).str.strip().str.upper().isin(BACKLOG_GRADES)]
                    total_credits = non_backlog["Credits"].apply(parse_credits).sum()
                    backlog_count = student["Grade"].astype(str).str.strip().str.upper().isin(BACKLOG_GRADES).sum()
                else:
                    error = f"No record found for Reg_No {reg_no} in Semester {semester}."

        except Exception as e:
            error = f"Error: {e}"

    return render_template(
        "index.html",
        reg_no=reg_no,
        semester=semester,
        name=name,
        result_html=result_html,
        total_credits=total_credits,
        backlog_count=backlog_count,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)
