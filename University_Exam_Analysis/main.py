
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import os
from getpass import getpass

# ==========================================
# 1. POSTGRESQL DATABASE CONFIGURATION
# ==========================================

DB_NAME = "University_Exam_DW"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

conn = None

try:
    # Enter PostgreSQL password
    password = getpass("Enter your PostgreSQL password: ")

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=password,
        host=DB_HOST,
        port=DB_PORT
    )

    print("\nSuccessfully connected to PostgreSQL!")

    # ==========================================
    # 2. FETCH EXAMINATION DATA
    # ==========================================

    query = """
        SELECT *
        FROM public.vw_exam_result_details;
    """

    df = pd.read_sql_query(query, conn)

    print("\nEXAMINATION DATA")
    print(df.to_string(index=False))

    print("\nTotal rows fetched:", len(df))

    # Calculate percentage for each examination record
    df["percentage"] = (
        df["marks_obtained"] / df["max_marks"]
    ) * 100

    # ==========================================
    # 3. OVERALL ACADEMIC PERFORMANCE
    # ==========================================

    print("\n1. OVERALL ACADEMIC PERFORMANCE")

    overall_average = df["percentage"].mean()

    print(
        "Overall Average Percentage:",
        round(overall_average, 2), "%"
    )

    # ==========================================
    # 4. DEPARTMENT-WISE PERFORMANCE
    # ==========================================

    print("\n2. DEPARTMENT-WISE PERFORMANCE")

    department_analysis = df.groupby("department_name").agg(
        average_percentage=("percentage", "mean"),
        total_records=("result_key", "count")
    ).round(2)

    print(department_analysis)

    # ==========================================
    # 5. PASS AND FAIL ANALYSIS
    # ==========================================

    print("\n3. PASS AND FAIL ANALYSIS")

    status = (
        df["result_status"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    pass_percentage = (status == "pass").mean() * 100
    fail_percentage = (status == "fail").mean() * 100

    print(
        "Pass Percentage:",
        round(pass_percentage, 2), "%"
    )

    print(
        "Fail Percentage:",
        round(fail_percentage, 2), "%"
    )

    print("\nPass and Fail Record Count:")
    print(df["result_status"].value_counts())

    # ==========================================
    # 6. SEMESTER-WISE PERFORMANCE
    # ==========================================

    print("\n4. SEMESTER-WISE PERFORMANCE")

    semester_analysis = df.groupby(
        "semester_number"
    )["percentage"].mean().round(2)

    print(semester_analysis)

    # ==========================================
    # 7. EXAMINATION TYPE COMPARISON
    # ==========================================

    print("\n5. EXAMINATION TYPE COMPARISON")

    exam_analysis = df.groupby(
        "exam_type"
    )["percentage"].mean().round(2)

    print(exam_analysis)

    # ==========================================
    # 8. CREATE OUTPUT FOLDER
    # ==========================================

    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Python_Reports"
    )

    os.makedirs(output_dir, exist_ok=True)

    print("\nGenerating Python charts...")

    # ==========================================
    # 9. DEPARTMENT-WISE PERFORMANCE CHART
    # ==========================================

    plt.figure(figsize=(9, 5))

    department_analysis["average_percentage"].plot(
        kind="bar",
        title="Department-wise Academic Performance"
    )

    plt.ylabel("Average Percentage")
    plt.xlabel("Department")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            output_dir,
            "department_performance.png"
        )
    )

    plt.close()

    # ==========================================
    # 10. SEMESTER-WISE PERFORMANCE CHART
    # ==========================================

    plt.figure(figsize=(9, 5))

    semester_analysis.plot(
        kind="line",
        marker="o",
        title="Semester-wise Academic Performance"
    )

    plt.ylabel("Average Percentage")
    plt.xlabel("Semester")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            output_dir,
            "semester_performance.png"
        )
    )

    plt.close()

    # ==========================================
    # 11. PASS VS FAIL CHART
    # ==========================================

    plt.figure(figsize=(6, 6))

    df["result_status"].value_counts().plot(
        kind="pie",
        autopct="%1.1f%%",
        title="Pass vs Fail Analysis"
    )

    plt.ylabel("")
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            output_dir,
            "pass_fail_analysis.png"
        )
    )

    plt.close()

    # ==========================================
    # 12. EXAMINATION TYPE COMPARISON CHART
    # ==========================================

    plt.figure(figsize=(8, 5))

    exam_analysis.plot(
        kind="bar",
        title="Mid Semester vs End Semester"
    )

    plt.ylabel("Average Percentage")
    plt.xlabel("Examination Type")
    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            output_dir,
            "exam_type_comparison.png"
        )
    )

    plt.close()

    print("All four charts generated successfully!")

    # ==========================================
    # 13. EXPORT ANALYSIS TO EXCEL
    # ==========================================

    overall_summary = pd.DataFrame({
        "Metric": [
            "Total Examination Records",
            "Overall Average Percentage",
            "Pass Percentage",
            "Fail Percentage"
        ],
        "Value": [
            len(df),
            round(overall_average, 2),
            round(pass_percentage, 2),
            round(fail_percentage, 2)
        ]
    })

    excel_path = os.path.join(
        output_dir,
        "Academic_Performance_Report.xlsx"
    )

    with pd.ExcelWriter(excel_path) as writer:

        overall_summary.to_excel(
            writer,
            sheet_name="Overall Summary",
            index=False
        )

        department_analysis.to_excel(
            writer,
            sheet_name="Department Analysis"
        )

        semester_analysis.to_frame(
            name="Average Percentage"
        ).to_excel(
            writer,
            sheet_name="Semester Analysis"
        )

        exam_analysis.to_frame(
            name="Average Percentage"
        ).to_excel(
            writer,
            sheet_name="Exam Comparison"
        )

        df.to_excel(
            writer,
            sheet_name="Examination Records",
            index=False
        )

    print("\nExcel report generated successfully!")

    # ==========================================
    # 14. FINAL STATUS
    # ==========================================

    print("\nPYTHON ANALYSIS COMPLETED SUCCESSFULLY!")

    print("\nReports saved in:")
    print(output_dir)

except Exception as e:
    print("\nAn error occurred:", e)

finally:
    if conn is not None:
        conn.close()
        print("\nDatabase connection closed.")
