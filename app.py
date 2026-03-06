import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime

# --- 1. PAGE CONFIG & UI THEME ---
st.set_page_config(page_title="Accounting Intelligence", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for Premium Styling
st.markdown("""
    <style>
    /* Main App Background */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header Styling */
    .header-container {
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
        border-radius: 0 0 30px 30px;
        margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(to right, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 12px;
        padding: 0 25px;
        background-color: #1e293b;
        color: #94a3b8;
        border: 1px solid #334155;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
    }

    /* Card/Box Styling */
    .report-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    /* Footer Styling */
    .footer {
        text-align: center;
        padding: 20px;
        font-size: 0.8rem;
        color: #64748b;
        border-top: 1px solid #334155;
        margin-top: 50px;
    }

    /* Image Styling */
    .img-fluid {
        border-radius: 15px;
        box-shadow: 0 10px 15px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER SECTION ---
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">ACCOUNTING INTELLIGENCE DASHBOARD</h1>
        <p style="color: #94a3b8; font-weight: 500; font-size: 1.1rem; margin-top: 10px;">
            Strategic Automation & Real-Time Financial Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. STATE MANAGEMENT ---
if 'gl' not in st.session_state:
    st.session_state.gl = pd.DataFrame(columns=['Date', 'Account', 'Type', 'Sub', 'Debit', 'Credit', 'Description'])

COA_MAP = {
    "Cash": {"type": "Asset", "sub": "Current Asset"},
    "Accounts Receivable": {"type": "Asset", "sub": "Current Asset"},
    "Inventory": {"type": "Asset", "sub": "Current Asset"},
    "Equipment": {"type": "Asset", "sub": "Fixed Asset"},
    "Accounts Payable": {"type": "Liability", "sub": "Current Liability"},
    "Common Stock": {"type": "Equity", "sub": "Equity"},
    "Revenue": {"type": "Revenue", "sub": "Operating"},
    "Expenses": {"type": "Expense", "sub": "Operating"}
}

# --- 4. NAVIGATION TABS ---
tabs = st.tabs(["📝 Journal", "🛒 Manager", "📊 Reports", "🇧🇴 Loans", "💻 Assets", "📓 Ledger"])

with tabs[0]: # Journal Entries
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("General Journal Posting")
    col1, col2 = st.columns(2)
    j_date = col1.date_input("Transaction Date", datetime.date.today())
    j_desc = col2.text_input("Memo / Reference")
    
    entry_df = pd.DataFrame([{"Account": "Cash", "Debit": 0.0, "Credit": 0.0}, {"Account": "Revenue", "Debit": 0.0, "Credit": 0.0}])
    edited = st.data_editor(entry_df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Post Transaction", use_container_width=True):
        if edited['Debit'].sum() == edited['Credit'].sum() and edited['Debit'].sum() > 0:
            for _, r in edited.iterrows():
                info = COA_MAP.get(r['Account'], {"type": "Other", "sub": "Other"})
                new_row = pd.DataFrame([{
                    'Date': j_date, 'Account': r['Account'], 'Type': info['type'],
                    'Sub': info['sub'], 'Debit': r['Debit'], 'Credit': r['Credit'], 'Description': j_desc
                }])
                st.session_state.gl = pd.concat([st.session_state.gl, new_row], ignore_index=True)
            st.toast("Transaction successfully posted to Ledger!")
        else: st.error("❌ Out of Balance: Debits must equal Credits.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]: # Transaction Manager
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("Fast-Track Business Actions")
    c1, c2, c3 = st.columns(3)
    q_date = c1.date_input("Action Date", datetime.date.today(), key="q_date")
    q_memo = c2.text_input("Memo", placeholder="e.g. March Sales")
    q_amt = c3.number_input("Amount ($)", min_value=0.0)
    
    btn_cols = st.columns(4)
    if btn_cols[0].button("💰 Record Sale", use_container_width=True):
        st.toast("Revenue Recognized.")
    if btn_cols[1].button("📈 Issue Equity", use_container_width=True):
        st.toast("Capital Issued.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[2]: # Financial Reporting
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("Official Financial Disclosure")
    if not st.session_state.gl.empty:
        df = st.session_state.gl.copy()
        df['Net'] = df['Debit'] - df['Credit']
        m1, m2, m3 = st.columns(3)
        m1.metric("Net Income", f"${df[df['Type']=='Revenue']['Credit'].sum() - df[df['Type']=='Expense']['Debit'].sum():,.2f}")
        m2.metric("Total Assets", f"${df[df['Type']=='Asset']['Net'].sum():,.2f}")
        m3.metric("Equity Balance", f"${abs(df[df['Type']=='Equity']['Net'].sum()):,.2f}")
    else: st.info("Post transactions to view real-time reports.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[3]: # Loan Amortization
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.subheader("Loan Debt Analysis")
    st.write("Calculate principal and interest trajectories.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[4]: # Assets
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.subheader("Fixed Asset Depreciation")
    st.write("Track equipment value decay.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[5]: # Ledger
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("Master General Ledger")
    st.dataframe(st.session_state.gl, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. FOOTER SECTION ---
st.markdown("""
    <div class="footer">
        © 2026 Accounting Intelligence Dashboard | Secure Ledger System | Built for Modern Finance
    </div>
    """, unsafe_allow_html=True)
