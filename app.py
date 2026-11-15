
import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================
# 1. PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="EduPro Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# =====================================
# 2. PROFESSIONAL STYLING
# =====================================

st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
h1 {
    color: #17365D;
    font-weight: 800;
}
h2, h3 {
    color: #24476B;
}
[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #e1e7ef;
    padding: 18px;
    border-radius: 12px;
}
[data-testid="stSidebar"] {
    background-color: #eaf0f8;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 EduPro Analytics Dashboard")
st.markdown("### Student, Course and Revenue Insights")

# =====================================
# 3. LOAD DATASETS
# =====================================

users = pd.read_csv("users.csv")
courses = pd.read_csv("courses.csv")
teachers = pd.read_csv("teachers.csv")
transactions = pd.read_csv("transactions.csv")

users["Age"] = pd.to_numeric(users["Age"], errors="coerce")
transactions["Amount"] = pd.to_numeric(
    transactions["Amount"], errors="coerce"
)
transactions["TransactionDate"] = pd.to_datetime(
    transactions["TransactionDate"], errors="coerce"
)
teachers["TeacherRating"] = pd.to_numeric(
    teachers["TeacherRating"], errors="coerce"
)

# =====================================
# 4. DASHBOARD FILTERS
# =====================================

st.sidebar.title("Dashboard Filters")

gender_options = ["All"] + sorted(
    users["Gender"].dropna().unique().tolist()
)

selected_gender = st.sidebar.selectbox(
    "Select Gender", gender_options
)

valid_ages = users["Age"].dropna()

min_age = int(valid_ages.min())
max_age = int(valid_ages.max())

if min_age < max_age:
    selected_age = st.sidebar.slider(
        "Select Age Range",
        min_age,
        max_age,
        (min_age, max_age)
    )
else:
    selected_age = (min_age, max_age)

category_options = ["All Categories"] + sorted(
    courses["CourseCategory"].dropna().unique().tolist()
)

selected_category = st.sidebar.selectbox(
    "Select Course Category", category_options
)

available_courses = courses.copy()

if selected_category != "All Categories":
    available_courses = available_courses[
        available_courses["CourseCategory"] == selected_category
    ]

course_options = ["All Courses"] + sorted(
    available_courses["CourseName"].dropna().unique().tolist()
)

selected_course = st.sidebar.selectbox(
    "Select Course", course_options
)

# =====================================
# 5. DATE FILTER
# =====================================

st.sidebar.subheader("Transaction Date Filter")

valid_dates = transactions["TransactionDate"].dropna()

if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    selected_dates = ()

# =====================================
# 6. APPLY FILTERS
# =====================================

filtered_users = users.copy()
filtered_courses = available_courses.copy()
filtered_transactions = transactions.copy()

if selected_gender != "All":
    filtered_users = filtered_users[
        filtered_users["Gender"] == selected_gender
    ]

filtered_users = filtered_users[
    filtered_users["Age"].between(
        selected_age[0], selected_age[1]
    )
]

if selected_course != "All Courses":
    filtered_courses = filtered_courses[
        filtered_courses["CourseName"] == selected_course
    ]

filtered_transactions = filtered_transactions[
    filtered_transactions["UserID"].isin(
        filtered_users["UserID"]
    )
]

filtered_transactions = filtered_transactions[
    filtered_transactions["CourseID"].isin(
        filtered_courses["CourseID"]
    )
]

if len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_transactions = filtered_transactions[
        (filtered_transactions["TransactionDate"].dt.date >= start_date) &
        (filtered_transactions["TransactionDate"].dt.date <= end_date)
    ]

st.sidebar.success("Filters Applied!")

# =====================================
# 7. KPI CARDS
# =====================================

st.subheader("EduPro Business Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Students",
        f"{filtered_users['UserID'].nunique():,}"
    )

with col2:
    st.metric(
        "Total Courses",
        f"{filtered_courses['CourseID'].nunique():,}"
    )

with col3:
    st.metric(
        "Total Enrollments",
        f"{len(filtered_transactions):,}"
    )

with col4:
    st.metric(
        "Total Revenue",
        f"₹{filtered_transactions['Amount'].sum():,.2f}"
    )

st.divider()

# =====================================
# 8. CREATE CHART 1
# =====================================

gender_count = (
    filtered_users["Gender"]
    .value_counts()
    .reset_index()
)
gender_count.columns = ["Gender", "Students"]

fig1 = px.pie(
    gender_count,
    names="Gender",
    values="Students",
    title="1. Student Gender Distribution",
    hole=0.4
)
fig1.update_traces(textinfo="label+percent+value")

# =====================================
# 9. CREATE CHART 2
# =====================================

age_count = (
    filtered_users["Age"]
    .dropna()
    .value_counts()
    .sort_index()
    .reset_index()
)
age_count.columns = ["Age", "Students"]

fig2 = px.bar(
    age_count,
    x="Age",
    y="Students",
    title="2. Student Age Distribution",
    text="Students"
)

# =====================================
# 10. CREATE CHART 3
# =====================================

enrollment = (
    filtered_transactions["CourseID"]
    .value_counts()
    .reset_index()
)
enrollment.columns = ["CourseID", "Enrollments"]

course_data = enrollment.merge(
    filtered_courses[["CourseID", "CourseName"]],
    on="CourseID",
    how="left"
)

fig3 = px.bar(
    course_data,
    x="CourseName",
    y="Enrollments",
    title="3. Course Enrollment Analysis",
    text="Enrollments"
)

# =====================================
# 11. CREATE CHART 4
# =====================================

revenue = (
    filtered_transactions
    .groupby("CourseID")["Amount"]
    .sum()
    .reset_index()
)
revenue.columns = ["CourseID", "Revenue"]

revenue_data = revenue.merge(
    filtered_courses[["CourseID", "CourseName"]],
    on="CourseID",
    how="left"
)

fig4 = px.bar(
    revenue_data.sort_values("Revenue", ascending=False),
    x="CourseName",
    y="Revenue",
    title="4. Revenue by Course",
    text_auto=True
)

# =====================================
# 12. CREATE CHART 5
# =====================================

payment_count = (
    filtered_transactions["PaymentMethod"]
    .value_counts()
    .reset_index()
)
payment_count.columns = ["Payment Method", "Transactions"]

fig5 = px.pie(
    payment_count,
    names="Payment Method",
    values="Transactions",
    title="5. Payment Method Analysis",
    hole=0.45
)
fig5.update_traces(textinfo="label+percent+value")

# =====================================
# 13. CREATE CHART 6
# =====================================

category_data = filtered_transactions.merge(
    filtered_courses[["CourseID", "CourseCategory"]],
    on="CourseID",
    how="left"
)

category_count = (
    category_data.groupby("CourseCategory")
    .size()
    .reset_index(name="Enrollments")
)

fig6 = px.pie(
    category_count,
    names="CourseCategory",
    values="Enrollments",
    title="6. Course Category Analysis",
    hole=0.45
)
fig6.update_traces(textinfo="label+percent+value")

# =====================================
# 14. CREATE CHART 7
# =====================================

teacher_performance = (
    teachers[["TeacherName", "TeacherRating"]]
    .dropna()
    .sort_values("TeacherRating", ascending=False)
)

fig7 = px.bar(
    teacher_performance,
    x="TeacherName",
    y="TeacherRating",
    title="7. Teacher Performance Analysis",
    text="TeacherRating"
)

# =====================================
# 15. DISPLAY CHARTS SIDE BY SIDE
# =====================================

st.subheader("EduPro Analytics Visualizations")

# ROW 1

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        fig1, use_container_width=True,
        key="gender_chart"
    )

with col2:
    st.plotly_chart(
        fig2, use_container_width=True,
        key="age_chart"
    )

# ROW 2

col3, col4 = st.columns(2)

with col3:
    st.plotly_chart(
        fig3, use_container_width=True,
        key="enrollment_chart"
    )

with col4:
    st.plotly_chart(
        fig4, use_container_width=True,
        key="revenue_chart"
    )

# ROW 3

col5, col6 = st.columns(2)

with col5:
    st.plotly_chart(
        fig5, use_container_width=True,
        key="payment_chart"
    )

with col6:
    st.plotly_chart(
        fig6, use_container_width=True,
        key="category_chart"
    )

# ROW 4

st.plotly_chart(
    fig7,
    use_container_width=True,
    key="teacher_chart"
)

# =====================================
# 16. DOWNLOAD FILTERED DATA
# =====================================

st.divider()

st.subheader("Download EduPro Data")

csv_data = filtered_transactions.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Transactions CSV",
    data=csv_data,
    file_name="EduPro_Filtered_Transactions.csv",
    mime="text/csv",
    key="download_transactions"
)

st.success("EduPro Dashboard Successfully Loaded!")
