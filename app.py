import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime

# --- 1. PAGE CONFIG & LIGHT PROFESSIONAL STYLING ---
st.set_page_config(page_title="Accounting Intelligence", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for Light Professional Theme with proper Header/Footer
st.markdown("""
    <style>
    /* Main Background - Clean Light Gray */
    .stApp {
        background-color: #fcfcfc;
        color: #1e293b;
    }
    
    /* Header Container - Solid Professional Blue */
    .header-container {
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        border-radius: 0 0 20px 20px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
    }

    /* Tab Styling - High Visibility */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #ffffff;
        padding: 10px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px;
        padding: 0 20px;
        background-color: #f1f5f9;
        color: #475569;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
    }

    /* Card/Box Styling */
    .report-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* Footer Styling */
    .footer {
        text-align: center;
        padding: 30px;
        font-size: 0.9rem;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER SECTION ---
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">ACCOUNTING INTELLIGENCE DASHBOARD</h1>
        <p style="color: #e2e8f0; font-weight: 500; font-size: 1.1rem; margin-top: 10px;">
            Strategic Financial Automation & Real-Time Analytics
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
tabs = st.tabs(["📝 Journal", "🛒 Manager", "🏛️ Reporting", "🇧🇴 Loans", "💻 Assets", "📓 Ledger"])

with tabs[0]: # Journal Entries
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("General Journal Posting")
    col1, col2 = st.columns(2)
    j_date = col1.date_input("Transaction Date", datetime.date.today(), key="j_date")
    j_desc = col2.text_input("Memo / Description", key="j_desc")
    
    entry_df = pd.DataFrame([{"Account": "Cash", "Debit": 0.0, "Credit": 0.0}, {"Account": "Revenue", "Debit": 0.0, "Credit": 0.0}])
    edited = st.data_editor(entry_df, num_rows="dynamic", use_container_width=True, key="j_editor")
    
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
            st.success("✅ Transaction Posted Successfully")
        else:
            st.error("❌ Out of Balance: Debits must equal Credits")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]: # Transaction Manager
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("Fast-Track Business Actions")
    c1, c2, c3 = st.columns(3)
    q_date = c1.date_input("Date", datetime.date.today(), key="q_date")
    q_memo = c2.text_input("Memo", key="q_memo")
    q_amt = c3.number_input("Amount ($)", min_value=0.0, key="q_amt")
    
    b1, b2, b3, b4 = st.columns(4)
    if b1.button("💰 Record Sale", use_container_width=True):
        # Automatic logic for quick sales
        sale_entries = [
            {"Account": "Cash", "Debit": q_amt, "Credit": 0.0},
            {"Account": "Revenue", "Debit": 0.0, "Credit": q_amt}
        ]
        new_gl = []
        for entry in sale_entries:
            info = COA_MAP.get(entry['Account'])
            new_gl.append({
                'Date': q_date, 'Account': entry['Account'], 'Type': info['type'],
                'Sub': info['sub'], 'Debit': entry['Debit'], 'Credit': entry['Credit'], 'Description': q_memo
            })
        st.session_state.gl = pd.concat([st.session_state.gl, pd.DataFrame(new_gl)], ignore_index=True)
        st.success("Sale Recorded!")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[2]: # Financial Reporting
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("Official Financial Disclosure")
        if not st.session_state.gl.empty:
        df = st.session_state.gl.copy()
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Debits", f"${df['Debit'].sum():,.2f}")
        m2.metric("Total Credits", f"${df['Credit'].sum():,.2f}")
        st.write("---")
        st.markdown("### Trial Balance (Requirement #2 Totals)")
        tb = df.groupby('Account')[['Debit', 'Credit']].sum()
        st.dataframe(tb, use_container_width=True)
        st.write(f"**Grand Total:** DR ${df['Debit'].sum():,.2f} | CR ${df['Credit'].sum():,.2f}")
    else:
        st.info("No records found in Ledger. Please post a transaction.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[3]: # Loan Amortization
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.subheader("Debt Amortization Analysis")
    st.write("Track principal and interest payments over time.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[4]: # Assets
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.subheader("Fixed Asset Valuation")
    st.write("Monitor asset book value and depreciation expense.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[5]: # Ledger
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("Master General Ledger")
    st.dataframe(st.session_state.gl, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. FOOTER SECTION ---
st.markdown("""
    <div class="footer">
        © 2026 ACCOUNTING INTELLIGENCE DASHBOARD | Professional Financial Systems | Built for Enterprise
    </div>
    """, unsafe_allow_html=True)
