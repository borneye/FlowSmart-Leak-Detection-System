import streamlit as st
import sqlite3
import hashlib
import os
from pathlib import Path
import sensor_data
import time
import pandas as pd
import altair as alt

# ===== INITIAL CONFIG =====
st.set_page_config(page_title="FlowSmart Leak Detection System", page_icon="🚰", layout="wide")

# ===== DATABASE CONFIGURATION =====
DB_FOLDER = Path("data")
DB_PATH = DB_FOLDER / "users.db"

def initialize_database():
    DB_FOLDER.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(""" 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Administrator', 'Maintenance', 'User'))
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Pending', 'Resolved')) DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        conn.commit()

def save_report(user_id, report_content):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO reports (user_id, report_content, timestamp, status) 
            VALUES (?, ?, ?, 'Pending')
        """, (user_id, report_content, timestamp))
        conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def sign_up_user(username, email, password, role):
    hashed_password = hash_password(password)
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                         (username, email, hashed_password, role))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def validate_user(username, password):
    hashed_password = hash_password(password)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, role FROM users WHERE username = ? AND password_hash = ?", 
                    (username, hashed_password))
        return cur.fetchone()

# ===== AUTH PAGES =====
def auth_pages():
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "Login"

    if st.session_state.auth_tab == "Login":
        show_login()
    else:
        show_signup()

def show_login():
    st.markdown("<h1 style='text-align: center; color: #1877f2;'>Log in to FlowSmart Leak Detection System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Stay connected to your water network.</p>", unsafe_allow_html=True)

    with st.container():
        st.write("")  # Add vertical spacing
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("---")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            login_btn = st.button("Log In")

            if login_btn:
                user_data = validate_user(username, password)
                if user_data:
                    st.session_state["user"] = user_data[1]
                    st.session_state["role"] = user_data[2]
                    st.session_state["user_id"] = user_data[0]
                    st.success(f"Welcome, {user_data[1]}! Role: {user_data[2]}")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            st.write("Don't have an account?")
            if st.button("Create New Account"):
                st.session_state.auth_tab = "Sign Up"
                st.rerun()
            if st.button("Forgotten account?"):
                st.session_state.auth_tab = "Forgot Password"
    st.rerun()


def show_signup():
    st.subheader("Sign Up")
    new_username = st.text_input("New Username", key="reg_user")
    new_email = st.text_input("Email", key="reg_email")
    new_password = st.text_input("New Password", type="password", key="reg_pass")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_pass")
    role = st.selectbox("Select Role", ["Administrator", "Maintenance", "User"], key="reg_role")
    sign_up_btn = st.button("Sign Up")

    if sign_up_btn:
        if new_password != confirm_password:
            st.error("Passwords do not match!")
        elif sign_up_user(new_username, new_email, new_password, role):
            st.success("Sign-up successful! Please log in.")
            st.session_state.auth_tab = "Login"
            st.rerun()
        else:
            st.error("Username or email already taken.")

    st.write("Already have an account?")
    if st.button("Login", key="login_link"):
        st.session_state.auth_tab = "Login"
        st.rerun()

# ===== DASHBOARD =====
def initialize_database():
    DB_FOLDER.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(""" 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Administrator', 'Maintenance', 'User'))
        )""")
        conn.execute(""" 
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            pressure REAL NOT NULL,
            flow REAL NOT NULL,
            leak_status TEXT NOT NULL
        )""")
        conn.commit()

def save_sensor_data(timestamp, pressure, flow, leak_status):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(""" 
            INSERT INTO sensor_data (timestamp, pressure, flow, leak_status)
            VALUES (?, ?, ?, ?)
        """, (timestamp, pressure, flow, leak_status))
        conn.commit()

# ===== AUTH PAGES =====
def auth_pages():
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "Login"

    if st.session_state.auth_tab == "Login":
        show_login()
    elif st.session_state.auth_tab == "Sign Up":
        show_signup()
    elif st.session_state.auth_tab == "Forgot Password":
        show_forgot_password()

def show_forgot_password():
    st.subheader("Reset Your Password")
    email = st.text_input("Enter your registered email address")

    if st.button("Send Reset Link"):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            user = cur.fetchone()
            if user:
                # For now, just show a success message (simulate email sending)
                st.success("A password reset link would be sent to your email (simulated).")
            else:
                st.error("No account found with that email.")

    if st.button("Back to Login"):
        st.session_state.auth_tab = "Login"
        st.rerun()

# Admin Dashboard

def show_dashboard():
    st.sidebar.title("Navigation")
    role = st.session_state.get("role")

    if role == "Administrator":
        st.sidebar.header("Administrator Panel")
        st.title("Admin Dashboard")

        tab1, tab2, tab3 = st.tabs(["📡 Monitor Network", "📊 Analyze Data", "🚨 Leak Notifications"])

        with tab1:
            st.subheader("Live Sensor Feed")
            if st.button("🔄 Refresh Sensor Data"):
                st.success("Sensor data refreshed!")
            timestamp, pressure, flow, leak_status = sensor_data.get_latest_sensor_data()
            st.metric("🕒 Timestamp", timestamp)
            st.metric("🔧 Pressure (PSI)", pressure)
            st.metric("💧 Flow Rate (L/min)", flow)
            st.metric("🚨 Leak Status", leak_status)

        with tab2:
            st.subheader("Analyze Sensor Data")

            # Load sensor data from the database
            with sqlite3.connect(DB_PATH) as conn:
                query = "SELECT timestamp, pressure, flow, leak_status FROM sensor_data ORDER BY timestamp DESC"
                df = pd.read_sql(query, conn)

            if df.empty:
                st.info("No sensor data available.")
            else:
                # Display data as a table
                st.dataframe(df)

                # Visualization - Pressure vs Flow
                st.subheader("Pressure vs Flow Visualization")
                chart = alt.Chart(df).mark_circle().encode(
                    x='pressure',
                    y='flow',
                    color='leak_status',
                    tooltip=['timestamp', 'pressure', 'flow', 'leak_status']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)

                # Visualization - Pressure over Time
                st.subheader("Pressure Over Time")
                chart = alt.Chart(df).mark_line().encode(
                    x='timestamp:T',
                    y='pressure:Q',
                    color='leak_status'
                ).interactive()
                st.altair_chart(chart, use_container_width=True)

                # Filters for data analysis (for example, filtering by leak status)
                st.subheader("Filter Data")
                leak_status_filter = st.selectbox("Select Leak Status", ['All', 'Leak Detected', 'No Leak'], index=0)
                if leak_status_filter != 'All':
                    df = df[df['leak_status'] == leak_status_filter]

                st.dataframe(df)

        with tab3:
            st.subheader("Leak Status Monitor")
            _, _, _, leak_status = sensor_data.get_latest_sensor_data()

            if leak_status == "Leak Detected":
                st.error("🚨 Leak Detected! Immediate action required.")
            else:
                st.success("✅ No leaks detected.")

            if leak_status == "Leak Detected":
                resolved = sensor_data.check_leak_resolution()
                if resolved:
                    st.success("✅ Leak resolved. System status updated.")
                else:
                    st.warning("🚨 Leak still unresolved. Monitoring ongoing.")

    elif role == "Maintenance":
        st.sidebar.header("Maintenance Panel")
        st.title("Maintenance Dashboard")

        if st.button("🔄 Refresh Sensor Data"):
            st.success("Sensor data refreshed!")

        timestamp, pressure, flow, leak_status = sensor_data.get_latest_sensor_data()

        col1, col2, col3 = st.columns(3)
        col1.metric("📅 Last Updated", timestamp)
        col2.metric("🔧 Pressure (PSI)", pressure)
        col3.metric("💧 Flow Rate (L/min)", flow)

        if leak_status == "Leak Detected":
            st.error("🚨 Leak Detected! Immediate attention required.")
            
            # Task Logging and Leak Resolution
            st.subheader("💬 Resolve the Leak")
            task_description = st.text_area("Enter maintenance task description")
            
            if st.button("Log Maintenance Task"):
                if task_description:
                    # Log the task in the session or database
                    if "maintenance_tasks" not in st.session_state:
                        st.session_state.maintenance_tasks = []
                    st.session_state.maintenance_tasks.append((time.strftime("%Y-%m-%d %H:%M:%S"), task_description))
                    st.success("Task logged! The leak is being addressed.")
                
                    # Update the database to mark the task related to the leak as resolved
                    with sqlite3.connect(DB_PATH) as conn:
                        conn.execute("UPDATE reports SET status = 'Resolved' WHERE report_content LIKE 'Leak Detected%'")
                        conn.commit()
                    st.success("Leak resolved. Status updated.")
            
           
        else:
            st.success("✅ No leaks detected.")

        st.subheader("🛠️ User Reports")
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(""" 
                SELECT reports.id, users.username, reports.report_content, 
                       reports.timestamp, reports.status 
                FROM reports 
                JOIN users ON users.id = reports.user_id 
                ORDER BY reports.timestamp DESC
            """)
            reports = cur.fetchall()

        if reports:
            for report in reports:
                st.write(f"**Report ID:** {report[0]} | **User:** {report[1]} | **Timestamp:** {report[3]} | **Status:** {report[4]}")
                st.write(f"**Issue Description:** {report[2]}")
                if report[4] == "Pending":
                    if st.button(f"Resolve Issue {report[0]}"):
                        with sqlite3.connect(DB_PATH) as conn:
                            conn.execute("UPDATE reports SET status = 'Resolved' WHERE id = ?", (report[0],))
                            conn.commit()
                        st.success(f"Issue {report[0]} marked as resolved.")
                st.markdown("---")
        else:
            st.info("No reports available.")

    elif role == "User":
        st.sidebar.header("User Panel")
        st.title("User Dashboard")

        if st.button("🔄 Refresh Sensor Data"):
            st.success("Sensor data refreshed!")

        timestamp, pressure, flow, leak_status = sensor_data.get_latest_sensor_data()

        st.write(f"📅 **Last Updated:** {timestamp}")
        st.write(f"🔧 **Pressure:** {pressure} PSI")
        st.write(f"💧 **Flow Rate:** {flow} L/min")
        st.write(f"🚨 **Leak Status:** {leak_status}")

        st.subheader("🗂️ Your Reported Issues")

        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, report_content, timestamp, status FROM reports WHERE user_id = ?", 
                        (st.session_state.get("user_id"),))
            user_reports = cur.fetchall()

        if user_reports:
            for report in user_reports:
                st.write(f"**Report ID:** {report[0]} | **Timestamp:** {report[2]} | **Status:** {report[3]}")
                st.write(f"**Issue Description:** {report[1]}")
                st.markdown("---")
        else:
            st.info("You haven't reported any issues yet.")

        st.subheader("🆘 Report an Issue")
        issue_description = st.text_area("Describe the issue you are facing")
        report_btn = st.button("Submit Report")

        if report_btn:
            if issue_description:
                user_id = st.session_state.get("user_id")
                if user_id:
                    save_report(user_id, issue_description)
                    st.success("Your issue has been reported. Thank you!")
                else:
                    st.error("User not logged in.")
            else:
                st.error("Please describe the issue.")

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.success("Logged out successfully")
        st.rerun()


# ===== MAIN APP FLOW =====
def main():
    initialize_database()
    if "user" not in st.session_state:
        auth_pages()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()

