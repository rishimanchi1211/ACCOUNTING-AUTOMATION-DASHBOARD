import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime

# --- 1. PAGE CONFIG & PREMIUM STYLING ---
st.set_page_config(page_title="Accounting Intelligence", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for Excellent Styling
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    /* Header Container */
    .header-container {
        text-align: center;
        padding: 30px;
        background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
        border-radius: 0 0 25px 25px;
        margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(to right, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    /* Professional Card Styling */
    .report-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 25px;
        border-radius: 18px;
        margin-bottom: 20px;
    }

    /* Custom Footer */
    .footer {
        text-align: center;
        padding: 30px;
        color: #64748b;
        border-top: 1px solid #334155;
        margin-top: 50px;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">ACCOUNTING INTELLIGENCE DASHBOARD</h1>
        <p style="color: #94a3b8; font-size: 1.1rem; margin-top: 10px;">Strategic Financial Automation & Real-Time Analytics</p>
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
    "Notes Payable": {"type": "Liability", "sub": "Long-term Liability"},
    "Common Stock": {"type": "Equity", "sub": "Equity"},
    "Retained Earnings": {"type": "Equity", "sub": "Equity"},
    "Revenue": {"type": "Revenue", "sub": "Operating Revenue"},
    "Operating Expenses": {"type": "Expense", "sub": "Operating Expense"},
}

# --- 4. NAVIGATION TABS ---
tabs = st.tabs(["📝 Journal Entries", "🛒 Transaction Manager", "🏛️ Financial Reporting", "🇧🇴 Loan Amortization", "💻 Asset Depreciation", "📓 General Ledger"])

# --- TAB 1: JOURNAL ENTRIES ---
with tabs[0]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("General Ledger Posting")
    col1, col2 = st.columns(2)
    j_date = col1.date_input("Transaction Date", datetime.date.today())
    j_desc = col2.text_input("Memo / Description", placeholder="e.g. Initial Investment")
    
    entry_df = pd.DataFrame([{"Account": "Cash", "Debit": 0.0, "Credit": 0.0}, {"Account": "Revenue", "Debit": 0.0, "Credit": 0.0}])
    edited = st.data_editor(entry_df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Post Transaction", use_container_width=True):
        if edited['Debit'].sum() == edited['Credit'].sum() and edited['Debit'].sum() > 0:
            new_rows = []
            for _, r in edited.iterrows():
                info = COA_MAP.get(r['Account'], {"type": "Other", "sub": "Other"})
                new_rows.append({
                    'Date': j_date, 'Account': r['Account'], 'Type': info['type'],
                    'Sub': info['sub'], 'Debit': r['Debit'], 'Credit': r['Credit'], 'Description': j_desc
                })
            st.session_state.gl = pd.concat([st.session_state.gl, pd.DataFrame(new_rows)], ignore_index=True)
            st.success("✅ Transaction successfully posted!")
        else:
            st.error("❌ Out of Balance: Total Debits must equal Total Credits.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: TRANSACTION MANAGER ---
with tabs[1]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("⚡ Fast-Track Actions")
    c1, c2, c3 = st.columns(3)
    q_date = c1.date_input("Action Date", datetime.date.today(), key="q_date")
    q_memo = c2.text_input("Transaction Memo", key="q_memo")
    q_amt = c3.number_input("Amount ($)", min_value=0.0, key="q_amt")
    
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    # Action logic would be added here
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 3: FINANCIAL REPORTING ---
with tabs[2]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("🏛️ Official Financial Disclosure")
        if not st.session_state.gl.empty:
        df = st.session_state.gl.copy()
        df['Net'] = df['Debit'] - df['Credit']
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Net Income", f"${df[df['Type']=='Revenue']['Credit'].sum() - df[df['Type']=='Expense']['Debit'].sum():,.2f}")
        m2.metric("Total Assets", f"${df[df['Type']=='Asset']['Net'].sum():,.2f}")
        m3.metric("Total Debits/Credits", f"${df['Debit'].sum():,.2f}")

        st.markdown("### Trial Balance (Requirement #2)")
        st.dataframe(df.groupby('Account')[['Debit', 'Credit']].sum(), use_container_width=True)
        st.write(f"**Final Total Sum:** DR ${df['Debit'].sum():,.2f} | CR ${df['Credit'].sum():,.2f}")
    else:
        st.info("No data available. Please post a transaction to view reports.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 4: LOAN AMORTIZATION ---
with tabs[3]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.subheader("Loan Debt Trajectory")
    # Loan calculation logic
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 5: ASSET DEPRECIATION ---
with tabs[4]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.subheader("Asset Value Decay")
    # Depreciation logic
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 6: GENERAL LEDGER ---
with tabs[5]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("📓 Master General Ledger")
    st.dataframe(st.session_state.gl, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. FOOTER ---
st.markdown("""
    <div class="footer">
        © 2026 ACCOUNTING INTELLIGENCE DASHBOARD | Professional Financial Management System | Built with Streamlit
    </div>
    """, unsafe_allow_html=True)
