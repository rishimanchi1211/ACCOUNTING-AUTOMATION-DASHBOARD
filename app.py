import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime

# --- 1. PREMIUM THEMING & CSS ---
st.set_page_config(page_title="Modern Ledger Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Main Background and Fonts */
    .main { background-color: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #1e293b; border-radius: 12px; padding: 10px; }
    .stTabs [data-baseweb="tab"] { height: 45px; border-radius: 8px; color: #94a3b8; font-weight: 600; border: none; }
    .stTabs [aria-selected="true"] { background-color: #4f46e5 !important; color: white !important; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4); }
    
    /* Metric and Card Styling */
    div[data-testid="stMetricValue"] { color: #818cf8; font-weight: 800; }
    .report-card { background: #1e293b; border: 1px solid #334155; padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    
    /* Button Styling */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 700; transition: all 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE STATE MANAGEMENT ---
if 'gl' not in st.session_state:
    st.session_state.gl = pd.DataFrame(columns=['Date', 'Account', 'Type', 'Sub', 'Debit', 'Credit', 'Description'])

COA_MAP = {
    "Cash": {"type": "Asset", "sub": "Current Asset"},
    "Accounts Receivable": {"type": "Asset", "sub": "Current Asset"},
    "Equipment": {"type": "Asset", "sub": "Fixed Asset"},
    "Accumulated Depreciation": {"type": "Asset", "sub": "Contra Asset"},
    "Accounts Payable": {"type": "Liability", "sub": "Current Liability"},
    "Notes Payable": {"type": "Liability", "sub": "Long-term"},
    "Common Stock": {"type": "Equity", "sub": "Equity"},
    "Retained Earnings": {"type": "Equity", "sub": "Equity"},
    "Revenue": {"type": "Revenue", "sub": "Operating"},
    "Operating Expenses": {"type": "Expense", "sub": "Operating"},
}

# --- 3. BUSINESS LOGIC FUNCTIONS ---
def post_transaction(date, desc, rows):
    new_entries = []
    for r in rows:
        if r['Account'] in COA_MAP:
            info = COA_MAP[r['Account']]
            new_entries.append({
                'Date': date, 'Account': r['Account'], 'Type': info['type'],
                'Sub': info['sub'], 'Debit': float(r['Debit']), 'Credit': float(r['Credit']),
                'Description': desc
            })
    if new_entries:
        st.session_state.gl = pd.concat([st.session_state.gl, pd.DataFrame(new_entries)], ignore_index=True)
        st.toast(f"✅ Transaction Posted: {desc}")

# --- 4. HEADER & BRANDING ---
st.markdown("<div style='text-align: center; padding: 20px;'><h1>💎 MODERN LEDGER INTELLIGENCE</h1><p style='color: #6366f1; font-weight: bold;'>Strategic Financial Automation Dashboard</p></div>", unsafe_allow_html=True)

# Navigation
tabs = st.tabs(["📝 Journal Entries", "🛒 Transaction Manager", "🏛️ Financial Reporting", "🇧🇴 Loan Amortization", "💻 Asset Depreciation", "📓 General Ledger"])

# --- TAB 1: JOURNAL ENTRIES ---
with tabs[0]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("Manual Double-Entry Journal")
    col1, col2 = st.columns(2)
    j_date = col1.date_input("Transaction Date", datetime.date.today())
    j_desc = col2.text_input("Memo / Reference", placeholder="e.g. Office Rent")
    
    st.info("💡 Pro-Tip: Ensure your total Debits equal your total Credits.")
    # Professional Data Editor (The Value Section)
    entry_df = pd.DataFrame([{"Account": "Cash", "Debit": 0.0, "Credit": 0.0}, {"Account": "Revenue", "Debit": 0.0, "Credit": 0.0}])
    edited = st.data_editor(entry_df, num_rows="dynamic", use_container_width=True, key="journal_editor")
    
    if st.button("Post Journal Entry"):
        if edited['Debit'].sum() == edited['Credit'].sum() and edited['Debit'].sum() > 0:
            post_transaction(j_date, j_desc, edited.to_dict('records'))
        else:
            st.error("❌ Unbalanced Entry or Zero Value. Please check your math.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: TRANSACTION MANAGER ---
with tabs[1]:
    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("⚡ Fast-Track Financial Actions")
    c_date, c_memo, c_amt = st.columns([1, 2, 1])
    q_date = c_date.date_input("Action Date", datetime.date.today())
    q_memo = c_memo.text_input("Transaction Memo")
    q_amt = c_amt.number_input("Amount ($)", min_value=0.0)
    
    btn_cols = st.columns(4)
    if btn_cols[0].button("💰 Record Sale"):
        post_transaction(q_date, q_memo, [{"Account": "Cash", "Debit": q_amt, "Credit": 0}, {"Account": "Revenue", "Debit": 0, "Credit": q_amt}])
    if btn_cols[1].button("📈 Issue Equity"):
        post_transaction(q_date, q_memo, [{"Account": "Cash", "Debit": q_amt, "Credit": 0}, {"Account": "Common Stock", "Debit": 0, "Credit": q_amt}])
    if btn_cols[2].button("🏦 Borrow Capital"):
        post_transaction(q_date, q_memo, [{"Account": "Cash", "Debit": q_amt, "Credit": 0}, {"Account": "Notes Payable", "Debit": 0, "Credit": q_amt}])
    if btn_cols[3].button("🏗️ Buy Fixed Asset"):
        post_transaction(q_date, q_memo, [{"Account": "Equipment", "Debit": q_amt, "Credit": 0}, {"Account": "Cash", "Debit": 0, "Credit": q_amt}])
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 3: FINANCIAL REPORTING ---
with tabs[2]:
    if st.session_state.gl.empty:
        st.warning("No data found. Post a transaction to see financial reports.")
    else:
        # Image of a professional corporate financial report structure
        st.subheader("🏛️ Official Financial Disclosure")
        df = st.session_state.gl.copy()
        df['Net'] = df['Debit'] - df['Credit']
        summary = df.groupby(['Account', 'Type', 'Sub'])['Net'].sum().reset_index()
        
        # Financial Snapshot Metrics
        rev = summary[summary['Type'] == 'Revenue']['Net'].sum() * -1
        exp = summary[summary['Type'] == 'Expense']['Net'].sum()
        ni = rev - exp
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Net Income", f"${ni:,.2f}")
        m2.metric("Total Assets", f"${summary[summary['Type'] == 'Asset']['Net'].sum():,.2f}")
        m3.metric("Total Liabilities", f"${abs(summary[summary['Type'] == 'Liability']['Net'].sum()):,.2f}")

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("### Income Statement")
            st.table(summary[summary['Type'].isin(['Revenue', 'Expense'])])
            st.markdown("### Stockholders Equity")
            st.table(summary[summary['Type'] == 'Equity'])
            
        with col_right:
            st.markdown("### Balance Sheet")
            st.table(summary[summary['Type'].isin(['Asset', 'Liability'])])
            st.markdown("### Cash Flow (Operating)")
            st.info(f"Net Operating Cash: ${ni:,.2f}")

        st.markdown("### ⚖️ Trial Balance (Req #2 Totals)")
        st.dataframe(summary[['Account', 'Net']], use_container_width=True)
        st.markdown(f"<p style='text-align: right; font-size: 20px;'><b>Total Debits:</b> {df.Debit.sum():,.2f} | <b>Total Credits:</b> {df.Credit.sum():,.2f}</p>", unsafe_allow_html=True)

# --- TAB 4: LOAN AMORTIZATION ---
with tabs[3]:
    # Image of loan amortization schedule
    st.subheader("🇧🇴 Loan Amortization Analysis")
    with st.container():
        p = st.number_input("Principal", value=110000.0)
        r = st.slider("Interest Rate (%)", 0.0, 15.0, 5.0) / 100
        m = st.number_input("Months", value=60)
        
        monthly_rate = r / 12
        payment = p * (monthly_rate / (1 - (1 + monthly_rate) ** -m))
        st.success(f"Estimated Monthly Payment: ${payment:,.2f}")

# --- TAB 5: ASSET DEPRECIATION ---
with tabs[4]:
    # Image of straight line depreciation graph
    st.subheader("💻 Asset Depreciation Trajectory")
    cost = st.number_input("Asset Cost", value=50000.0)
    life = st.number_input("Useful Life (Years)", value=5)
    if st.button("Calculate Depreciation"):
        annual_dep = cost / life
        st.write(f"Annual Depreciation: ${annual_dep:,.2f}")

# --- TAB 6: GENERAL LEDGER ---
with tabs[5]:
    st.subheader("📓 Master General Ledger")
    st.dataframe(st.session_state.gl, use_container_width=True)
