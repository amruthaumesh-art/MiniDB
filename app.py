
import streamlit as st
from minidb import Database
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="MiniDB Studio",
    page_icon="🗄️",
    layout="wide"
)

DB_PATH = Path("data/demo_students.log")
DB_PATH.parent.mkdir(exist_ok=True)

db = Database(DB_PATH)

# --------------------------------------------------
# PROFESSIONAL DESIGN
# --------------------------------------------------


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

.stApp {
    background: #0b1120;
    color: #e5eaf5;
    font-family: 'Inter', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1500px;
    padding: 2rem 3rem 3rem;
}

h1, h2, h3 {
    color: #f1f5ff !important;
    font-weight: 700 !important;
}

p, label {
    color: #a8b4ca;
}

[data-testid="stSidebar"] {
    background: #101a2c;
    border-right: 1px solid #263650;
}

[data-testid="stSidebar"] * {
    color: #e5eaf5;
}

[data-testid="stMetric"] {
    background: #151f33;
    border: 1px solid #263650;
    border-radius: 14px;
    padding: 22px;
}

[data-testid="stMetricValue"] {
    color: #38bdf8 !important;
    font-family: 'JetBrains Mono', monospace;
}

.stButton > button,
.stFormSubmitButton > button {
    background: #38bdf8;
    color: #07111f;
    border: none;
    border-radius: 8px;
    font-weight: 700;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #7dd3fc;
    color: #07111f;
}

input, textarea {
    background: #151f33 !important;
    color: #f1f5ff !important;
    border: 1px solid #33445f !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #263650;
    border-radius: 12px;
}

div[data-testid="stForm"] {
    background: #151f33;
    padding: 22px;
    border: 1px solid #263650;
    border-radius: 12px;
}

hr {
    border-color: #263650;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HELPER
# --------------------------------------------------

def get_records():
    return db.all()


def get_semesters(records):
    values = []
    for record in records:
        try:
            values.append(int(record.get("semester", 0)))
        except (ValueError, TypeError):
            continue
    return values


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🗄️ MiniDB Studio")
    st.caption("DATABASE MANAGEMENT SYSTEM")

    st.divider()

    page = st.radio(
        "WORKSPACE",
        [
            "Overview",
            "Records",
            "Insert Student",
            "Search",
            "Analytics",
            "Query Lab"
        ],
        label_visibility="visible"
    )

    st.divider()

    st.markdown("### ENGINE STATUS")
    st.success("Database Connected")
    st.caption("Python Storage Engine")
    st.caption("MiniDB Prototype v1.0")

    st.divider()
    st.caption("Custom Database Project")


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

records = get_records()
semesters = get_semesters(records)

st.markdown(
    "<p style='color:#087e78;font-weight:700;"
    "letter-spacing:2px;font-size:12px;'>"
    "DATABASE MANAGEMENT WORKSPACE</p>",
    unsafe_allow_html=True
)

st.title("MiniDB Studio")

st.markdown(
    "Manage records, execute queries and monitor database operations."
)

st.divider()


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

if page == "Overview":

    st.subheader("Database Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Records", len(records))
    c2.metric("Storage Engine", "JSON Log")
    c3.metric("Query Engine", "Active")
    c4.metric("Indexes", len(db.indexes))

    st.write("")

    left, right = st.columns([1.5, 1])

    with left:
        st.markdown("### Recent Student Records")

        if records:
            st.dataframe(
                records[-5:][::-1],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No records available.")

    with right:
        st.markdown("### Database Information")

        st.markdown("""
        **System:** MiniDB

        **Architecture:** Custom Python Database Engine

        **Storage:** Append-only JSON operation log

        **Query Processing:** Custom parser and executor

        **Indexing:** In-memory index

        **Transactions:** Basic commit and rollback
        """)

        st.success("All core components initialized")


# --------------------------------------------------
# RECORDS
# --------------------------------------------------

elif page == "Records":

    st.subheader("Student Records")
    st.caption("Browse the records currently stored in MiniDB.")

    records = get_records()

    if records:
        st.dataframe(
            records,
            use_container_width=True,
            hide_index=True
        )
        st.info(f"{len(records)} records available in the database.")
    else:
        st.warning("The database is empty.")


# --------------------------------------------------
# INSERT STUDENT
# --------------------------------------------------

elif page == "Insert Student":

    st.subheader("Insert New Student")
    st.caption("Add a new record to the MiniDB storage engine.")

    with st.form("insert_student_form"):

        name = st.text_input("Student Name")

        branch = st.text_input(
            "Branch",
            value="CSE IoT-AI"
        )

        semester = st.number_input(
            "Semester",
            min_value=1,
            max_value=8,
            value=5
        )

        submitted = st.form_submit_button(
            "Save Student Record"
        )

        if submitted:

            if name.strip() and branch.strip():

                try:
                    db.insert({
                        "name": name.strip(),
                        "branch": branch.strip(),
                        "semester": int(semester)
                    })

                    st.success(
                        f"Student '{name}' added successfully!"
                    )

                    st.balloons()

                except Exception as e:
                    st.error(f"Insert failed: {e}")

            else:
                st.error("Please enter the student name and branch.")


# --------------------------------------------------
# SEARCH
# --------------------------------------------------

elif page == "Search":

    st.subheader("Search Records")
    st.caption("Find students by name or branch.")

    search_text = st.text_input(
        "Search database",
        placeholder="Enter student name or branch..."
    )

    records = get_records()

    if search_text:

        results = [
            record for record in records
            if search_text.lower() in str(record).lower()
        ]

        if results:
            st.success(f"{len(results)} matching records found.")

            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.warning("No matching records found.")

    else:
        st.info("Enter a search term to begin.")


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

elif page == "Analytics":

    st.subheader("Database Analytics")
    st.caption("Statistical insights from stored student records.")

    records = get_records()
    semesters = get_semesters(records)

    average = (
        sum(semesters) / len(semesters)
        if semesters else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("COUNT", len(records))
    c2.metric("SUM of Semesters", sum(semesters))
    c3.metric("AVG Semester", f"{average:.2f}")

    st.divider()

    st.markdown("### Semester Distribution")

    if semesters:

        distribution = {}

        for semester in semesters:
            key = str(semester)
            distribution[key] = distribution.get(key, 0) + 1

        st.bar_chart(
            distribution,
            x_label="Semester",
            y_label="Number of Students"
        )

    else:
        st.info("No numeric semester data available.")


# --------------------------------------------------
# QUERY LAB
# --------------------------------------------------

elif page == "Query Lab":

    st.subheader("SQL Query Lab")
    st.caption(
        "Execute SQL-like commands using your custom MiniDB engine."
    )

    st.markdown("### Query Editor")

    query = st.text_area(
        "MiniDB Query",
        value="SELECT * FROM students",
        height=160
    )

    if st.button("▶ Execute Query"):

        try:

            result = db.execute(query)

            st.success("Query executed successfully.")

            st.markdown("### Execution Result")

            if isinstance(result, list) and result:
                if all(isinstance(item, dict) for item in result):
                    st.dataframe(
                        result,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.write(result)

            else:
                st.write(result)

            stats = db.last_query_stats

            if stats:
                st.markdown("### Query Execution Statistics")

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Scan Type",
                    stats.get("scan_type", "N/A")
                )

                c2.metric(
                    "Records Examined",
                    stats.get("records_examined", 0)
                )

                c3.metric(
                    "Records Returned",
                    stats.get("records_returned", 0)
                )

                st.json(stats)

        except Exception as e:
            st.error(f"Query execution failed: {e}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "MiniDB Studio | Custom Database and Query Execution Engine"
)
