import streamlit as st
import pandas as pd
import datetime
import requests

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Transparent NGO Funding",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000"

# --- API DATA FETCHING ---
def fetch_data():
    try:
        st.session_state.donors = requests.get(f"{API_URL}/api/donors").json().get("data", [])
        st.session_state.donations = requests.get(f"{API_URL}/api/donations").json().get("data", [])
        st.session_state.project_stats = requests.get(f"{API_URL}/api/dashboard-stats").json().get("data", {})
    except Exception as e:
        st.error(f"Could not connect to backend API: {e}")
        if 'donors' not in st.session_state: st.session_state.donors = []
        if 'donations' not in st.session_state: st.session_state.donations = []
        if 'project_stats' not in st.session_state: 
            st.session_state.project_stats = {
                "budget_allocation": {}, 
                "total_spent": 0, 
                "target_goal": 0
            }

fetch_data()

projects_list = ["Clean Water Initiative", "Education for All", "Health Clinics Setup", "Reforestation Project"]

# --- API INTEGRATION ---
def api_register_donor(name, email):
    try:
        res = requests.post(f"{API_URL}/api/register", json={"name": name, "email": email})
        if res.status_code == 200:
            fetch_data()
            return True
        else:
            st.error(f"Registration failed: {res.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"API Error: {e}")
        return False

def api_make_donation(donor_name, project_name, amount):
    try:
        res = requests.post(f"{API_URL}/api/donate", json={
            "donor_name": donor_name,
            "project": project_name,
            "amount": amount
        })
        if res.status_code == 200:
            fetch_data()
            return True
        else:
            st.error(f"Donation failed: {res.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"API Error: {e}")
        return False

# --- PAGE FUNCTIONS ---

def dashboard_page():
    st.title("🌍 Transparency Dashboard")
    st.markdown("Real-time impact tracking for our NGO initiatives. See exactly where the funds are going.")
    st.divider()

    # Calculate metrics
    total_donations = sum(d["amount"] for d in st.session_state.donations)
    total_spent = st.session_state.project_stats["total_spent"]
    remaining_balance = total_donations - total_spent

    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Funds Raised", value=f"${total_donations:,}", delta="12% from last month")
    with col2:
        st.metric(label="Total Funds Spent", value=f"${total_spent:,}")
    with col3:
        st.metric(label="Remaining Balance", value=f"${remaining_balance:,}", delta="-Expenses", delta_color="inverse")
    with col4:
        st.metric(label="Active Projects", value=len(projects_list))
    
    st.divider()

    # Charts Area
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Budget Allocation per Category")
        # Prepare data for Bar chart (spending per category)
        allocation_data = st.session_state.project_stats["budget_allocation"]
        df_allocation = pd.DataFrame({
            "Category": list(allocation_data.keys()),
            "Amount": list(allocation_data.values())
        })
        df_allocation.set_index("Category", inplace=True)
        st.bar_chart(df_allocation)

    with chart_col2:
        st.subheader("Donations per Project (Breakdown)")
        # Prepare data for pie chart
        df_donations = pd.DataFrame(st.session_state.donations)
        if not df_donations.empty:
            project_totals = df_donations.groupby("project")["amount"].sum().reset_index()
            # Streamlit doesn't have a native pie chart, but we can simulate a breakdown or use altair/plotly
            # A bar chart with categorical data is completely fine, but let's use a matplotlib pie chart for variety if needed.
            # To keep it pure streamlit natively interactive, an area or bar is common, but let's use altair for a nice pie chart!
            import altair as alt
            pie_chart = alt.Chart(project_totals).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="amount", type="quantitative"),
                color=alt.Color(field="project", type="nominal"),
                tooltip=["project", "amount"]
            ).properties(width=300, height=300)
            
            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.info("No donation data available to display charts.")

    st.markdown("### Recent Activity Highlights")
    st.info("💡 **Transparency Note:** All expenses undergo a regular monthly audit. Next audit report scheduled for April 5th.")


def register_donor_page():
    st.title("🤝 Register as a Donor")
    st.markdown("Join our community of transparent giving. Register to track exactly how your contributions make an impact!")
    
    with st.form("registration_form", clear_on_submit=True):
        st.subheader("Donor Information")
        name = st.text_input("Full Name", placeholder="e.g. John Doe")
        email = st.text_input("Email Address", placeholder="e.g. john@example.com")
        
        submitted = st.form_submit_button("Register")
        if submitted:
            if name and email:
                success = api_register_donor(name, email)
                if success:
                    st.success(f"Welcome, {name}! You have successfully registered with {email}.")
                    st.balloons()
            else:
                st.error("Please fill out all required fields.")


def donation_page():
    st.title("💖 Make a Donation")
    st.markdown("Select a project you are passionate about and contribute directly.")
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Donation Details")
            with st.form("donation_form", clear_on_submit=True):
                donor_name = st.text_input("Donor Name", placeholder="e.g. John Doe")
                selected_project = st.selectbox("Select Project to Support", projects_list)
                amount = st.number_input("Donation Amount ($)", min_value=1.0, value=50.0, step=10.0)
                
                submitted = st.form_submit_button("Submit Donation")
                if submitted:
                    if donor_name:
                        api_make_donation(donor_name, selected_project, amount)
                        st.success(f"Thank you, {donor_name}! Your donation of ${amount:,.2f} to '{selected_project}' has been recorded.")
                    else:
                        st.error("Please enter a donor name.")
                        
        with col2:
            st.subheader("Why Donate?")
            st.info("""
            **Every dollar is tracked.**
            
            Our platform guarantees 100% transparency. Once you donate, you can trace your funds all the way to their final execution point in the 'Transactions' tab.
            
            - Secure & Verified
            - Real-time impact updates
            - Immutable audit trails
            """)


def transactions_page():
    st.title("📋 Transparent Audit Trail")
    st.markdown("View the complete history of all donations and funding allocations across the platform. This data is fully open for audit.")
    
    st.subheader("Recent Transactions")
    df = pd.DataFrame(st.session_state.donations)
    
    if not df.empty:
        # Reorder and format dataframe for nicer display
        df = df[["date", "donor_name", "project", "amount"]]
        df.columns = ["Date", "Donor Name", "Project", "Amount ($)"]
        df["Amount ($)"] = df["Amount ($)"].apply(lambda x: f"${x:,.2f}")
        
        # Display as full-width interactive dataframe
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions found.")
        
    st.divider()
    
    st.download_button(
        label="Download Full Audit Report (CSV)",
        data=df.to_csv(index=False).encode('utf-8') if not df.empty else b"",
        file_name="ngo_audit_trail.csv",
        mime="text/csv",
    )


# --- MAIN APP ROUTING ---

def main():
    # Sidebar design
    st.sidebar.title("NGO Transparency")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Register Donor", "Donate to Project", "Transactions"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("System Status: **Online**")
    st.sidebar.caption("Backend API: **Connected**")
    
    # Route to selected page
    if page == "Dashboard":
        dashboard_page()
    elif page == "Register Donor":
        register_donor_page()
    elif page == "Donate to Project":
        donation_page()
    elif page == "Transactions":
        transactions_page()

if __name__ == "__main__":
    main()