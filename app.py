import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime

# --- 1. PAGE CONFIG & PREMIUM STYLING ---
st.set_page_config(page_title="Modern Ledger intelligence", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for "Excellent Styling" and Responsive Layout
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

    /* Tab Styling: Indigo Highlights */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 12px;
        padding: 0 25px;
        background-color: #1e293b;
        color: #94a3b8;
        border: 1px solid #334155;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4f46e5 !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(79, 70, 229, 0.5);
    }

    /* Refined Components: Card-style boxes */
    .report-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
    }
    
    /* Fast-Track Panel */
    .transaction-panel { background: #111827; padding: 20px; border-radius: 15px; border: 1px solid #4b5563; }

    /* Footer Section */
    .footer {
        text-align: center;
        padding: 25px;
        color: #64748b;
        border-top: 1px solid #334155;
        margin-top: 50px;
    }

    /* Responsive Image Styling */
    .img-fluid {
        border-radius: 15px;
        box-shadow: 0 10px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER SECTION ---
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">ACCOUNTING INTELLIGENCE DASHBOARD</h1>
        <p style="color: #94a3b8; font-size: 1.2rem; margin-top: 10px;">Strategic Financial Automation & Real-Time Analytics</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'gl' not in st.session_state:
    st.session_state.gl = pd.DataFrame(columns=['Date', 'Account', 'Type', 'Sub', 'Debit', 'Credit', 'Description'])

COA_MAP = {
    "Cash": {"type": "Asset", "sub": "Current Asset"},
    "Inventory": {"type": "Asset", "sub": "Current Asset"},
    "Equipment": {"type": "Asset", "sub": "Fixed Asset"},
    "Accumulated Depreciation": {"type": "Asset", "sub": "Contra Asset"},
    "Accounts Payable": {"type": "Liability", "sub": "Current Liability"},
    "Common Stock": {"type": "Equity", "sub": "Equity"},
    "Revenue": {"type": "Revenue", "sub": "Operating"},
    "Cost of Goods Sold": {"type": "Expense", "sub": "Operating"}
}

# --- 4. NAVIGATION TABS ---

tabs = st.tabs(["📝 Journal Entries", "🛒 Transaction Manager", "🏛️ Financial Reporting", "🇧🇴 Loan Amortization", "💻 Asset Depreciation", "📓 General Ledger"])

# --- TAB: JOURNAL ---
with tabs[0]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("Manual Journal Posting (Excel-Style Table)")
    col1, col2 = st.columns(2)
    j_date = col1.date_input("Date", datetime.date.today(), key="j_date")
    j_desc = col2.text_input("Memo", placeholder="Rent / Payroll", key="j_desc")
    
    # Modern data editor for double-entry
    entry_df = pd.DataFrame([{"Account": "Cash", "Debit": 0.0, "Credit": 0.0}, {"Account": "Revenue", "Debit": 0.0, "Credit": 0.0}])
    edited = st.data_editor(entry_df, num_rows="dynamic", use_container_width=True, key="j_editor")
    
    if st.button("Post Transaction", variant="primary", use_container_width=True):
        if edited['Debit'].sum() == edited['Credit'].sum() and edited['Debit'].sum() > 0:
            for _, r in edited.iterrows():
                info = COA_MAP.get(r['Account'], {"type": "Other", "sub": "Other"})
                new_row = pd.DataFrame([{
                    'Date': j_date, 'Account': r['Account'], 'Type': info['type'],
                    'Sub': info['sub'], 'Debit': r['Debit'], 'Credit': r['Credit'], 'Description': j_desc
                }])
                st.session_state.gl = pd.concat([st.session_state.gl, new_row], ignore_index=True)
            st.toast("Transaction recorded in General Ledger.")
        else: st.error("❌ Out of Balance: Debits must equal Credits.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB: TRANSACTION MANAGER ---
with tabs[1]:
    st.markdown("<div class='transaction-panel'>", unsafe_allow_html=True)
    st.subheader("⚡ Fast-Track Action Center")
    colA, colB, colC = st.columns(3)
    q_date = colA.date_input("Date", datetime.date.today(), key="q_date")
    q_desc = colB.text_input("Memo", placeholder="e.g. Consulting Revenue", key="q_desc")
    q_amt = colC.number_input("Amount ($)", min_value=0.0, key="q_amt")
    
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("💰 Record Sale", use_container_width=True):
        st.info("Recognizing Revenue.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB: FINANCIAL REPORTING ---
with tabs[2]:
    st.subheader("🏛️ Official Disclosure & Statements")
    
    if not st.session_state.gl.empty:
        df = st.session_state.gl.copy()
        df['Net'] = df['Debit'] - df['Credit']
        m1, m2, m3 = st.columns(3)
        m1.metric("Net Income", f"${df[df['Type']=='Revenue']['Credit'].sum():,.2f}")
        m2.metric("Asset Balance", f"${df[df['Type']=='Asset']['Net'].sum():,.2f}")
        st.write("---")
        st.markdown("### Trial Balance (Requirement #2)")
        st.dataframe(df.groupby('Account')[['Debit', 'Credit']].sum(), use_container_width=True)
    else: st.info("Ledger is empty. Post a transaction to see statements.")

# --- TAB: LOAN AMORTIZATION ---
with tabs[3]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    
    st.subheader("Debt Amortization Analysis")
    st.write("Calculate principal and interest trajectories.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB: ASSET DEPRECIATION ---
with tabs[4]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    
    st.subheader("Fixed Asset Valuation")
    st.write("Track equipment value decay.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB: GENERAL LEDGER ---
with tabs[5]:
    st.subheader("📓 Master General Ledger")
    st.dataframe(st.session_state.gl, use_container_width=True)

# --- 5. FOOTER SECTION ---
st.markdown("""
    <div class="footer">
        © 2026 ACCOUNTING INTELLIGENCE DASHBOARD | Enterprise Resource Planning | Built with Streamlit
    </div>
    """, unsafe_allow_html=True)
