import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime

# --- 1. PAGE CONFIG & EXECUTIVE STYLING ---
st.set_page_config(page_title="Accounting Intelligence", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for Excellent Styling, Responsive Layout, and Refined Components
st.markdown("""
    <style>
    /* Main Background and Executive Color Palette */
    .stApp { background-color: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Professional Header: Gradient and Exact Title */
    .header-container {
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
        border-radius: 0 0 30px 30px;
        margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    /* Refined Components: Report-Card CSS class */
    .report-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 12px;
        background-color: #1e293b;
        color: #94a3b8;
        border: 1px solid #334155;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
    }

    /* Footer Section */
    .footer {
        text-align: center;
        padding: 25px;
        color: #64748b;
        border-top: 1px solid #334155;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER SECTION ---
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">ACCOUNTING INTELLIGENCE DASHBOARD</h1>
        <p style="color: #94a3b8; font-size: 1.2rem; margin-top: 10px;">Automated Financial Engineering & Strategic Analytics</p>
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
tabs = st.tabs(["📝 Journal", "🛒 Manager", "🏛️ Reporting", "🇧🇴 Loans", "💻 Assets", "📓 Ledger"])

# --- TAB 1: JOURNAL ENTRIES ---
with tabs[0]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("Manual Journal Posting")
    col1, col2 = st.columns(2)
    j_date = col1.date_input("Date", datetime.date.today(), key="j_date")
    j_desc = col2.text_input("Description", placeholder="Memo", key="j_desc")
    
    # Responsive Value Table
    entry_df = pd.DataFrame([{"Account": "Cash", "Debit": 0.0, "Credit": 0.0}, {"Account": "Revenue", "Debit": 0.0, "Credit": 0.0}])
    edited = st.data_editor(entry_df, num_rows="dynamic", use_container_width=True, key="j_editor")
    
    if st.button("Post to Ledger", use_container_width=True):
        if edited['Debit'].sum() == edited['Credit'].sum() and edited['Debit'].sum() > 0:
            new_rows = []
            for _, r in edited.iterrows():
                info = COA_MAP.get(r['Account'], {"type": "Other", "sub": "Other"})
                new_rows.append({'Date': j_date, 'Account': r['Account'], 'Type': info['type'], 'Sub': info['sub'], 'Debit': r['Debit'], 'Credit': r['Credit'], 'Description': j_desc})
            st.session_state.gl = pd.concat([st.session_state.gl, pd.DataFrame(new_rows)], ignore_index=True)
            st.success("✅ Transaction Record Secured.")
        else:
            st.error("❌ Out of Balance: Debits must equal Credits.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: TRANSACTION MANAGER ---
with tabs[1]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("⚡ Fast-Track Financial Actions")
    c1, c2, c3 = st.columns(3)
    q_date = c1.date_input("Action Date", datetime.date.today(), key="q_date")
    q_memo = c2.text_input("Action Memo", key="q_memo")
    q_amt = c3.number_input("Amount ($)", min_value=0.0, key="q_amt")
    
    b1, b2, b3, b4 = st.columns(4)
    if b1.button("💰 Record Sale", use_container_width=True):
        st.info("Recording Revenue...")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 3: FINANCIAL REPORTING ---
with tabs[2]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("🏛️ Official Disclosure & Statements")
    
    if not st.session_state.gl.empty:
        df = st.session_state.gl.copy()
        m1, m2, m3 = st.columns(3)
        m1.metric("Net Income", f"${df[df['Type']=='Revenue']['Credit'].sum() - df[df['Type']=='Expense']['Debit'].sum():,.2f}")
        m2.metric("Trial Balance Total", f"${df['Debit'].sum():,.2f}")
        st.dataframe(df.groupby('Account')[['Debit', 'Credit']].sum(), use_container_width=True)
    else:
        st.info("Ledger is empty. Please post a transaction.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 4: LOAN AMORTIZATION ---
with tabs[3]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    
    st.subheader("Debt Amortization Trajectory")
    st.write("Calculate principal and interest over tenure.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 5: ASSET DEPRECIATION ---
with tabs[4]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    
    st.subheader("Fixed Asset Valuation")
    st.write("Track book value decay over useful life.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 6: GENERAL LEDGER ---
with tabs[5]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("📓 Master General Ledger")
    st.dataframe(st.session_state.gl, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. FOOTER SECTION ---
st.markdown("""
    <div class="footer">
        © 2026 ACCOUNTING INTELLIGENCE DASHBOARD | Enterprise Resource Planning | Built with Streamlit
    </div>
    """, unsafe_allow_html=True)
