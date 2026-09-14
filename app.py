import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page configuration
st.set_page_config(page_title="School Admission & Withdrawal System", page_icon="🏫", layout="wide")

# Database file path
DB_FILE = "student_records.csv"

# Initialize database with explicit string types to prevent type errors
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, dtype=str)
        return df
    else:
        df = pd.DataFrame(columns=[
            "Admission_No", "Student_Name", "Father_Name", 
            "Class", "Date_Of_Admission", "Status", "Date_Of_Withdrawal", "Remarks"
        ], dtype=str)
        df.to_csv(DB_FILE, index=False)
        return df

df = load_data()

st.title("🏫 School Admission & Withdrawal Management System")
st.markdown("Manage student entries, active rolls, and school leaving/withdrawals seamlessly.")

# Sidebar Navigation
menu = st.sidebar.selectbox("Navigation Menu", ["Dashboard Overview", "New Admission", "Process Withdrawal", "Student Directory"])

if menu == "Dashboard Overview":
    st.subheader("📊 System Summary")
    total_students = len(df)
    active_students = len(df[df["Status"] == "Active"])
    withdrawn_students = len(df[df["Status"] == "Withdrawn"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", total_students)
    col2.metric("Active Students", active_students)
    col3.metric("Withdrawn Students", withdrawn_students)
    
    st.markdown("---")
    st.subheader("Recent System Activity")
    if not df.empty:
        st.dataframe(df.tail(5), use_container_width=True)
    else:
        st.info("No records available yet.")

elif menu == "New Admission":
    st.subheader("📝 Register New Student Admission")
    
    with st.form("admission_form"):
        col1, col2 = st.columns(2)
        with col1:
            adm_no = st.text_input("Admission / Serial Number")
            student_name = st.text_input("Student Full Name")
            father_name = st.text_input("Father's Name")
        with col2:
            student_class = st.selectbox("Class/Grade", ["6th", "7th", "8th", "9th", "10th", "11th", "12th"])
            adm_date = st.date_input("Date of Admission", datetime.today())
            
        submitted = st.form_submit_button("Confirm Admission")
        
        if submitted:
            if not adm_no or not student_name:
                st.error("Please fill out Admission Number and Student Name.")
            elif adm_no in df["Admission_No"].astype(str).values:
                st.error(f"Admission Number {adm_no} already exists!")
            else:
                new_row = pd.DataFrame([{
                    "Admission_No": str(adm_no),
                    "Student_Name": str(student_name),
                    "Father_Name": str(father_name),
                    "Class": str(student_class),
                    "Date_Of_Admission": str(adm_date),
                    "Status": "Active",
                    "Date_Of_Withdrawal": "",
                    "Remarks": "Enrolled"
                }], dtype=str)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success(f"Successfully registered admission for {student_name}!")

elif menu == "Process Withdrawal":
    st.subheader("❌ Process Student Withdrawal / Leaving")
    
    active_df = df[df["Status"] == "Active"]
    if active_df.empty:
        st.info("No active students found in the database.")
    else:
        selected_adm = st.selectbox("Select Student by Admission No & Name", 
                                    active_df.apply(lambda x: f"{x['Admission_No']} - {x['Student_Name']}", axis=1))
        
        if selected_adm:
            adm_id = selected_adm.split(" - ")[0]
            
            with st.form("withdrawal_form"):
                withdrawal_date = st.date_input("Date of Withdrawal / Leaving", datetime.today())
                remarks = st.text_area("Reason for Withdrawal (e.g., Transfer, Course Completion)")
                withdraw_submitted = st.form_submit_button("Execute Withdrawal")
                
                if withdraw_submitted:
                    df.loc[df["Admission_No"].astype(str) == adm_id, "Status"] = "Withdrawn"
                    df.loc[df["Admission_No"].astype(str) == adm_id, "Date_Of_Withdrawal"] = str(withdrawal_date)
                    df.loc[df["Admission_No"].astype(str) == adm_id, "Remarks"] = str(remarks)
                    df.to_csv(DB_FILE, index=False)
                    st.success("Student has been marked as Withdrawn successfully.")
                    st.rerun()

elif menu == "Student Directory":
    st.subheader("📂 Complete Master Student Directory")
    
    status_filter = st.radio("Filter by Status", ["All", "Active", "Withdrawn"], horizontal=True)
    
    if status_filter != "All":
        filtered_df = df[df["Status"] == status_filter]
    else:
        filtered_df = df
        
    st.dataframe(filtered_df, use_container_width=True)
    
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Directory as CSV",
        data=csv_data,
        file_name='school_student_records.csv',
        mime='text/csv',
    )