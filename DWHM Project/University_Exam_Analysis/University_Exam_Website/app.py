
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="University Exam Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM LIGHT + PURPLE DESIGN
# --------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #F8F7FC;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F0EBFF 0%, #F8F6FF 100%);
        border-right: 1px solid #E6DFFC;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #4C2C91;
    }

    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #302052;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #817795;
        font-size: 14px;
        margin-bottom: 24px;
    }

    .hero {
        background: linear-gradient(120deg, #6842B8, #9272DB);
        padding: 30px;
        border-radius: 18px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(104, 66, 184, 0.16);
    }

    .hero h1 {
        color: white;
        font-size: 29px;
        margin-bottom: 8px;
    }

    .hero p {
        color: #F0EAFE;
        font-size: 15px;
        margin-bottom: 0;
    }

    .metric-card {
        background: white;
        border: 1px solid #ECE7F7;
        border-radius: 15px;
        padding: 20px;
        min-height: 125px;
        box-shadow: 0 3px 12px rgba(52, 32, 87, 0.04);
    }

    .metric-label {
        color: #827895;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 10px;
    }

    .metric-value {
        color: #4C2C91;
        font-size: 29px;
        font-weight: 800;
    }

    .metric-note {
        color: #9B91AA;
        font-size: 11px;
        margin-top: 5px;
    }

    .section-heading {
        color: #38245E;
        font-size: 19px;
        font-weight: 700;
        margin-top: 22px;
        margin-bottom: 12px;
    }

    .info-card {
        background: white;
        border: 1px solid #ECE7F7;
        border-radius: 14px;
        padding: 19px;
        min-height: 120px;
    }

    .info-card h3 {
        color: #5A399C;
        font-size: 16px;
    }

    .info-card p {
        color: #817795;
        font-size: 13px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #ECE7F7;
        padding: 15px;
        border-radius: 14px;
    }

    div[data-testid="stMetricLabel"] {
        color: #827895;
    }

    div[data-testid="stMetricValue"] {
        color: #4C2C91;
    }

    .stButton button {
        background-color: #6842B8;
        color: white;
        border: none;
        border-radius: 9px;
    }

    .stButton button:hover {
        background-color: #523294;
        color: white;
    }

    div[data-baseweb="select"] > div {
        border-color: #DDD3F2;
        border-radius: 9px;
    }

    h1, h2, h3 {
        color: #38245E;
    }

    .footer {
        text-align: center;
        color: #A49AAF;
        font-size: 12px;
        padding: 25px 0 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

@st.cache_resource
def get_engine(password):
    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username="postgres",
        password=password,
        host="localhost",
        port=5432,
        database="University_Exam_DW"
    )
    return create_engine(connection_url)


@st.cache_data(ttl=60)
def load_data(password):
    engine = get_engine(password)

    query = text("""
        SELECT *
        FROM public.vw_exam_result_details
    """)

    with engine.connect() as connection:
        data = pd.read_sql(query, connection)

    return data


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def metric_card(label, value, note=""):
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
    """, unsafe_allow_html=True)


def section_title(title):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True
    )


def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="white",
        font=dict(family="Inter", color="#514665"),
        title_font=dict(size=17, color="#38245E"),
        margin=dict(l=25, r=25, t=55, b=25),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            font=dict(color="#665B78")
        )
    )
    return fig


def show_footer():
    st.markdown("""
        <div class="footer">
            University Examination Result OLAP Analysis
            | Academic Performance Analytics
        </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR - LOGIN AND NAVIGATION
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🎓 Exam Analytics")
    st.caption("University Performance Portal")

    st.divider()

    st.markdown("### Database Connection")

    password = st.text_input(
        "PostgreSQL password",
        type="password",
        help="Enter your local PostgreSQL password."
    )

    if not password:
        st.info("Enter your PostgreSQL password to access the dashboard.")
        st.stop()

    try:
        df = load_data(password)
    except Exception as error:
        st.error("Database connection failed.")
        st.caption(
            "Check that PostgreSQL is running and your password is correct."
        )
        st.stop()

    if df.empty:
        st.warning("No examination records were found.")
        st.stop()

    # Calculate percentage
    df["percentage"] = (
        df["marks_obtained"] / df["max_marks"] * 100
    )

    df["result_status"] = (
        df["result_status"].astype(str).str.strip().str.title()
    )

    st.success("Database connected")

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Choose a page",
        [
            "Home",
            "Dashboard",
            "Department Analysis",
            "Semester Analysis",
            "Examination Analysis",
            "Pass/Fail Analysis",
            "Records"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.caption("Data source: PostgreSQL")
    st.caption("Database: University_Exam_DW")


# --------------------------------------------------
# COMMON FILTERS
# --------------------------------------------------

filtered_df = df.copy()

if page != "Home":
    with st.sidebar:
        st.markdown("### Filters")

        if "department_name" in df.columns:
            departments = sorted(
                df["department_name"].dropna().unique().tolist()
            )
            selected_departments = st.multiselect(
                "Department",
                departments,
                default=departments
            )
            filtered_df = filtered_df[
                filtered_df["department_name"].isin(selected_departments)
            ]

        if "semester_number" in df.columns:
            semesters = sorted(
                df["semester_number"].dropna().unique().tolist()
            )
            selected_semesters = st.multiselect(
                "Semester",
                semesters,
                default=semesters
            )
            filtered_df = filtered_df[
                filtered_df["semester_number"].isin(selected_semesters)
            ]

        if "academic_year" in df.columns:
            years = sorted(
                df["academic_year"].dropna().unique().tolist()
            )
            selected_years = st.multiselect(
                "Academic Year",
                years,
                default=years
            )
            filtered_df = filtered_df[
                filtered_df["academic_year"].isin(selected_years)
            ]


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if page == "Home":

    st.markdown("""
        <div class="hero">
            <h1>University Examination Analytics</h1>
            <p>
                Welcome to the University Examination Result OLAP Analysis
                portal. Explore student performance, compare departments,
                analyse semesters and understand examination results.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="main-title">Project Overview</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">An interactive academic performance analysis system</div>',
        unsafe_allow_html=True
    )

    total_students = df["student_id"].nunique()
    total_records = len(df)
    total_departments = df["department_name"].nunique()
    average_percentage = df["percentage"].mean()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Total Students", f"{total_students:,}")
    with c2:
        metric_card("Departments", f"{total_departments}")
    with c3:
        metric_card("Exam Records", f"{total_records:,}")
    with c4:
        metric_card("Average Percentage", f"{average_percentage:.2f}%")

    section_title("Explore the Portal")

    a, b = st.columns(2)

    with a:
        st.markdown("""
            <div class="info-card">
                <h3>📊 Performance Dashboard</h3>
                <p>View key academic indicators and overall examination performance.</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="info-card">
                <h3>🏛️ Department Analysis</h3>
                <p>Compare academic performance across AI&DS, CSE and CSIT.</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="info-card">
                <h3>📚 Semester Analysis</h3>
                <p>Understand performance trends across all eight semesters.</p>
            </div>
        """, unsafe_allow_html=True)

    with b:
        st.markdown("""
            <div class="info-card">
                <h3>📝 Examination Analysis</h3>
                <p>Compare Mid Semester and End Semester examination performance.</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="info-card">
                <h3>✅ Pass/Fail Analysis</h3>
                <p>Explore pass and fail records and overall success percentages.</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="info-card">
                <h3>📁 Examination Records</h3>
                <p>Explore and download the underlying examination records.</p>
            </div>
        """, unsafe_allow_html=True)

    section_title("About This Project")

    st.write("""
    This project uses a PostgreSQL data warehouse to organise university
    examination data and perform OLAP analysis. Python and Pandas support
    data analysis, while interactive visualisations help explore academic
    performance from different perspectives.
    """)

    show_footer()


# --------------------------------------------------
# DASHBOARD PAGE
# --------------------------------------------------

elif page == "Dashboard":

    st.markdown(
        '<div class="main-title">Academic Performance Dashboard</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Overall examination statistics and insights</div>',
        unsafe_allow_html=True
    )

    total_students = filtered_df["student_id"].nunique()
    total_records = len(filtered_df)
    average_percentage = filtered_df["percentage"].mean()

    passed = (
        filtered_df["result_status"] == "Pass"
    ).sum()

    failed = (
        filtered_df["result_status"] == "Fail"
    ).sum()

    pass_percentage = (
        passed / total_records * 100 if total_records else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Students", f"{total_students:,}")
    with c2:
        metric_card("Exam Records", f"{total_records:,}")
    with c3:
        metric_card("Average Percentage", f"{average_percentage:.2f}%")
    with c4:
        metric_card("Pass Percentage", f"{pass_percentage:.2f}%")

    section_title("Department Performance")

    department_data = (
        filtered_df.groupby("department_name")["percentage"]
        .mean().reset_index()
    )

    fig = px.bar(
        department_data,
        x="department_name",
        y="percentage",
        color="department_name",
        text_auto=".2f",
        title="Average Percentage by Department",
        labels={
            "department_name": "Department",
            "percentage": "Average Percentage"
        },
        color_discrete_sequence=[
            "#6842B8", "#9272DB", "#B9A2ED"
        ]
    )
    fig.update_yaxes(title="Average Percentage (%)")
    st.plotly_chart(style_chart(fig), use_container_width=True)

    left, right = st.columns(2)

    with left:
        section_title("Pass vs Fail")

        result_counts = (
            filtered_df["result_status"].value_counts()
            .rename_axis("Result")
            .reset_index(name="Records")
        )

        fig = px.pie(
            result_counts,
            names="Result",
            values="Records",
            hole=0.55,
            color="Result",
            color_discrete_map={
                "Pass": "#7652C8",
                "Fail": "#D6C9EF"
            },
            title="Examination Result Distribution"
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)

    with right:
        section_title("Exam Type Comparison")

        exam_data = (
            filtered_df.groupby("exam_type")["percentage"]
            .mean().reset_index()
        )

        fig = px.bar(
            exam_data,
            x="exam_type",
            y="percentage",
            color="exam_type",
            text_auto=".2f",
            title="Average Percentage by Exam Type",
            color_discrete_sequence=["#6842B8", "#B9A2ED"]
        )
        fig.update_yaxes(title="Average Percentage (%)")
        st.plotly_chart(style_chart(fig), use_container_width=True)

    show_footer()


# --------------------------------------------------
# DEPARTMENT ANALYSIS
# --------------------------------------------------

elif page == "Department Analysis":

    st.markdown(
        '<div class="main-title">Department Analysis</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Compare academic performance across departments</div>',
        unsafe_allow_html=True
    )

    department_data = (
        filtered_df.groupby("department_name")
        .agg(
            Average_Percentage=("percentage", "mean"),
            Total_Records=("percentage", "count")
        )
        .reset_index()
    )

    fig = px.bar(
        department_data,
        x="department_name",
        y="Average_Percentage",
        color="department_name",
        text_auto=".2f",
        title="Department-wise Average Percentage",
        color_discrete_sequence=[
            "#6842B8", "#9272DB", "#B9A2ED"
        ]
    )
    fig.update_yaxes(title="Average Percentage (%)")
    st.plotly_chart(style_chart(fig), use_container_width=True)

    section_title("Department Summary")
    st.dataframe(
        department_data.round(2),
        use_container_width=True,
        hide_index=True
    )

    show_footer()


# --------------------------------------------------
# SEMESTER ANALYSIS
# --------------------------------------------------

elif page == "Semester Analysis":

    st.markdown(
        '<div class="main-title">Semester Analysis</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Explore academic performance across semesters</div>',
        unsafe_allow_html=True
    )

    semester_data = (
        filtered_df.groupby("semester_number")["percentage"]
        .mean().reset_index()
        .sort_values("semester_number")
    )

    fig = px.line(
        semester_data,
        x="semester_number",
        y="percentage",
        markers=True,
        text=semester_data["percentage"].round(2),
        title="Semester-wise Academic Performance",
        labels={
            "semester_number": "Semester",
            "percentage": "Average Percentage"
        }
    )
    fig.update_traces(
        line=dict(color="#7652C8", width=3),
        marker=dict(size=9, color="#7652C8")
    )
    fig.update_yaxes(title="Average Percentage (%)")
    st.plotly_chart(style_chart(fig), use_container_width=True)

    section_title("Semester Summary")
    st.dataframe(
        semester_data.round(2),
        use_container_width=True,
        hide_index=True
    )

    show_footer()


# --------------------------------------------------
# EXAMINATION ANALYSIS
# --------------------------------------------------

elif page == "Examination Analysis":

    st.markdown(
        '<div class="main-title">Examination Analysis</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Compare examination types and their performance</div>',
        unsafe_allow_html=True
    )

    exam_data = (
        filtered_df.groupby("exam_type")["percentage"]
        .mean().reset_index()
    )

    fig = px.bar(
        exam_data,
        x="exam_type",
        y="percentage",
        color="exam_type",
        text_auto=".2f",
        title="Mid Semester vs End Semester",
        color_discrete_sequence=["#6842B8", "#B9A2ED"]
    )
    fig.update_yaxes(title="Average Percentage (%)")
    st.plotly_chart(style_chart(fig), use_container_width=True)

    section_title("Examination Summary")
    st.dataframe(
        exam_data.round(2),
        use_container_width=True,
        hide_index=True
    )

    show_footer()


# --------------------------------------------------
# PASS / FAIL ANALYSIS
# --------------------------------------------------

elif page == "Pass/Fail Analysis":

    st.markdown(
        '<div class="main-title">Pass/Fail Analysis</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Understand student examination outcomes</div>',
        unsafe_allow_html=True
    )

    result_counts = (
        filtered_df["result_status"].value_counts()
        .rename_axis("Result")
        .reset_index(name="Records")
    )

    total = len(filtered_df)
    passed = (filtered_df["result_status"] == "Pass").sum()
    failed = (filtered_df["result_status"] == "Fail").sum()

    pass_pct = passed / total * 100 if total else 0
    fail_pct = failed / total * 100 if total else 0

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Passed Records", f"{passed:,}", f"{pass_pct:.2f}%")
    with c2:
        metric_card("Failed Records", f"{failed:,}", f"{fail_pct:.2f}%")
    with c3:
        metric_card("Total Records", f"{total:,}")

    fig = px.pie(
        result_counts,
        names="Result",
        values="Records",
        hole=0.55,
        color="Result",
        color_discrete_map={
            "Pass": "#7652C8",
            "Fail": "#D6C9EF"
        },
        title="Pass and Fail Distribution"
    )
    st.plotly_chart(style_chart(fig), use_container_width=True)

    section_title("Result Summary")
    st.dataframe(
        result_counts,
        use_container_width=True,
        hide_index=True
    )

    show_footer()


# --------------------------------------------------
# EXAMINATION RECORDS
# --------------------------------------------------

elif page == "Records":

    st.markdown(
        '<div class="main-title">Examination Records</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">View and download filtered examination data</div>',
        unsafe_allow_html=True
    )

    st.markdown(f"**Records displayed:** {len(filtered_df):,}")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download Examination Records (CSV)",
        data=csv_data,
        file_name="University_Examination_Records.csv",
        mime="text/csv"
    )

    show_footer()
