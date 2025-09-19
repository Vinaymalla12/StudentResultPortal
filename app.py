from flask import Flask, render_template, request
import pandas as pd

# ✅ Create Flask app before using routes
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    status = None
    name = ""
    
    if request.method == "POST":
        reg_no = request.form["reg_no"]
        try:
            df = pd.read_excel("6thsemrslts.xlsx")  # Make sure this file is in the same folder
            print("Data loaded successfully")

            student_data = df[df["Reg_No"] == int(reg_no)]
            print("Filtered data:", student_data)

            if not student_data.empty:
                grades = student_data["Grade"].tolist()
                if any(g in ['F', 'S'] for g in grades):
                    status = "❌ FAIL"
                else:
                    status = "✅ PASS"

                result = student_data[['Subject_Name', 'Grade', 'Credits']].to_html(index=False)
                name = student_data.iloc[0]["Name"]
            else:
                result = "No student found with that Reg_No."

        except Exception as e:
            result = f"Error: {e}"
            print("Error occurred:", result)

    return render_template("index.html", result=result, name=name, status=status)

# ✅ Run the app
if __name__ == "__main__":
    app.run(debug=True)
