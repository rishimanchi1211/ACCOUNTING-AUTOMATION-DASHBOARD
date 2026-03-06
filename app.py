import pandas as pd
import numpy as np
import json
import gradio as gr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# ---------------------------
# 1. Global State & Chart of Accounts
# ---------------------------
general_ledger_df = pd.DataFrame(columns=['Date', 'Account', 'Type', 'Sub', 'Debit', 'Credit', 'Description'])
journal_entries_df = pd.DataFrame(columns=['Date', 'Description', 'Entries'])

COA_MAP = {
    "Cash": {"type": "Asset", "sub": "Current Asset"},
    "Accounts Receivable": {"type": "Asset", "sub": "Current Asset"},
    "Inventory": {"type": "Asset", "sub": "Current Asset"},
    "Equipment": {"type": "Asset", "sub": "Fixed Asset"},
    "Accumulated Depreciation": {"type": "Asset", "sub": "Contra Asset"},
    "Accounts Payable": {"type": "Liability", "sub": "Current Liability"},
    "Notes Payable": {"type": "Liability", "sub": "Long-term Liability"},
    "Common Stock": {"type": "Equity", "sub": "Equity"},
    "Retained Earnings": {"type": "Equity", "sub": "Equity"},
    "Revenue": {"type": "Revenue", "sub": "Operating Revenue"},
    "Cost of Goods Sold": {"type": "Expense", "sub": "Operating Expense"},
    "Operating Expenses": {"type": "Expense", "sub": "Operating Expense"},
}

# ---------------------------
# 2. Logic Engines (Reporting & Core)
# ---------------------------

def generate_financial_reports():
    if general_ledger_df.empty:
        return [pd.DataFrame(columns=["Status", "No Data"])] * 5 + [go.Figure()]

    df = general_ledger_df.copy()
    df['Net'] = df['Debit'] - df['Credit']
    summary = df.groupby(['Account', 'Type', 'Sub'])['Net'].sum().reset_index()

    # Income Statement
    rev = summary[summary['Type'] == 'Revenue']['Net'].sum() * -1
    exp = summary[summary['Type'] == 'Expense']['Net'].sum()
    ni = rev - exp
    is_df = pd.DataFrame([["Revenue", rev], ["Expenses", exp], ["Net Income", ni]], columns=["Line Item", "Amount"])

    # Equity
    cs = summary[summary['Account'] == 'Common Stock']['Net'].sum() * -1
    re_balance = summary[summary['Account'] == 'Retained Earnings']['Net'].sum() * -1 + ni
    se_df = pd.DataFrame([["Common Stock", cs], ["Retained Earnings", re_balance], ["Total Equity", cs + re_balance]], columns=["Component", "Value"])

    # Balance Sheet
    assets = summary[summary['Type'] == 'Asset']['Net'].sum()
    liabs = summary[summary['Type'] == 'Liability']['Net'].sum() * -1
    bs_df = pd.DataFrame([["Total Assets", assets], ["Total Liabilities", liabs], ["Total Equity", cs + re_balance]], columns=["Category", "Amount"])

    # Cash Flow
    cf_df = pd.DataFrame([["Net Income (Operating)", ni], ["Cash on Hand", summary[summary['Account'] == 'Cash']['Net'].sum()]], columns=["Activity", "Cash Impact"])

    # Trial Balance
    total_dr, total_cr = general_ledger_df['Debit'].sum(), general_ledger_df['Credit'].sum()
    tb_df = summary[['Account', 'Net']].copy()
    tb_df.loc[len(tb_df)] = ["TOTAL SUM", f"DR: {total_dr} | CR: {total_cr}"]

    fig = go.Figure(go.Pie(labels=summary['Account'], values=summary['Net'].abs(), hole=.3))
    fig.update_layout(title="Capital Weighting", template="plotly_white")

    return is_df, se_df, bs_df, cf_df, tb_df, fig

def add_journal_entry_from_table(date_str, description, table_data):
    global general_ledger_df, journal_entries_df
    valid_rows = table_data[table_data['Account'].str.strip() != ""]
    if valid_rows.empty:
        return general_ledger_df, journal_entries_df, go.Figure()

    gl_list = []
    for _, row in valid_rows.iterrows():
        acc = str(row['Account']).strip()
        info = COA_MAP.get(acc, {"type": "Other", "sub": "Other"})
        gl_list.append({
            'Date': pd.to_datetime(date_str), 'Account': acc,
            'Type': info['type'], 'Sub': info['sub'],
            'Debit': float(row['Debit'] or 0), 'Credit': float(row['Credit'] or 0),
            'Description': description
        })

    new_gl_entries = pd.DataFrame(gl_list)
    general_ledger_df = pd.concat([general_ledger_df, new_gl_entries], ignore_index=True)
    new_je = pd.DataFrame([{'Date': date_str, 'Description': description, 'Entries': "Posted"}])
    journal_entries_df = pd.concat([journal_entries_df, new_je], ignore_index=True)

    fig = go.Figure(data=[
        go.Bar(name='Debit', x=new_gl_entries['Account'], y=new_gl_entries['Debit'], marker_color='#10B981'),
        go.Bar(name='Credit', x=new_gl_entries['Account'], y=new_gl_entries['Credit'], marker_color='#EF4444')
    ])
    fig.update_layout(barmode='group', title="Entry Impact", template="plotly_white")

    return general_ledger_df, journal_entries_df, fig

# --- Amortization & Depreciation Functions ---


def loan_ui(principal, rate, months, start_date):
    p, r, m = float(principal), float(rate), int(months)
    df = pd.DataFrame([[i, round(p/m, 2)] for i in range(1, m+1)], columns=['Month', 'Payment'])
    return df, go.Figure(go.Scatter(y=df['Payment'], fill='tozeroy'))


def asset_ui(cost, life, start_date):
    cost, life = float(cost), int(life)
    years = max(1, int(life / 12))
    annual_dep = cost / years
    data = []
    val = cost
    for i in range(1, years + 1):
        val -= annual_dep
        data.append([i, round(annual_dep, 2), max(0, round(val, 2))])
    df = pd.DataFrame(data, columns=['Year', 'Depreciation', 'Book Value'])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Year'], y=df['Depreciation'], name='Yearly Depr.', marker_color='#FBBF24'))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Book Value'], name='Asset Value', line=dict(color='#D97706', width=4)))
    fig.update_layout(title="Asset Depreciation Trajectory", template="plotly_white")
    return df, fig

def get_account_balances(gl_df):
    if gl_df.empty: return pd.DataFrame(columns=['Account', 'Balance']), go.Figure()
    bals = gl_df.groupby('Account').apply(lambda x: x['Debit'].sum() - x['Credit'].sum()).reset_index()
    bals.columns = ['Account', 'Balance']
    fig = go.Figure(go.Treemap(labels=bals['Account'], parents=[""] * len(bals), values=bals['Balance'].abs()))
    return bals, fig

# --- Fast-Track Business Helpers ---
def record_sale(d, desc, amt): return add_journal_entry_from_table(d, desc, pd.DataFrame([{"Account": "Cash", "Debit": amt, "Credit": 0}, {"Account": "Revenue", "Debit": 0, "Credit": amt}]))
def record_stock(d, desc, amt): return add_journal_entry_from_table(d, desc, pd.DataFrame([{"Account": "Cash", "Debit": amt, "Credit": 0}, {"Account": "Common Stock", "Debit": 0, "Credit": amt}]))
def record_borrow(d, desc, amt): return add_journal_entry_from_table(d, desc, pd.DataFrame([{"Account": "Cash", "Debit": amt, "Credit": 0}, {"Account": "Notes Payable", "Debit": 0, "Credit": amt}]))
def record_asset_p(d, desc, amt): return add_journal_entry_from_table(d, desc, pd.DataFrame([{"Account": "Equipment", "Debit": amt, "Credit": 0}, {"Account": "Cash", "Debit": 0, "Credit": amt}]))

# ---------------------------
# 4. Interface Styling
# ---------------------------

css = """
.gradio-container { background-color: #F8FAFC; }
.gr-button-primary { background: #1E3A8A !important; color: white !important; border-radius: 8px !important; }
.main-header { text-align: center; color: #1E3A8A; font-family: 'Inter', sans-serif; font-weight: 800; }
.report-box { border: 1px solid #CBD5E1; padding: 15px; border-radius: 8px; background: white; margin-bottom: 10px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
.transaction-panel { background: #EFF6FF; padding: 20px; border-radius: 12px; border: 1px solid #BFDBFE; }
"""

with gr.Blocks(theme=gr.themes.Soft(), css=css) as demo:
    gr.Markdown("# 📊 Account Automation & Intelligence", elem_classes=["main-header"])

    with gr.Tabs():
        # TAB 1: JOURNAL ENTRIES
        with gr.Tab("📝 Journal Entries"):
            with gr.Row():
                with gr.Column(scale=1):
                    je_date = gr.Textbox(label="Entry Date", value=str(datetime.date.today()))
                    je_desc = gr.Textbox(label="Memo / Description", placeholder="e.g. Initial Investment")
                    gr.Markdown("### 💰 Value Section")
                    je_input_table = gr.Dataframe(
                        headers=["Account", "Debit", "Credit"],
                        datatype=["str", "number", "number"],
                        row_count=2, col_count=(3, "fixed"),
                        label="Double-Entry Table", interactive=True,
                        value=[["Cash", 0, 0], ["Revenue", 0, 0]]
                    )
                    je_btn = gr.Button("📥 Post Transaction", variant="primary")
                with gr.Column(scale=1):
                    je_p = gr.Plot(label="Entry Impact Visualization")
            je_hist = gr.DataFrame(label="Journal Posting History")

        # TAB 2: TRANSACTION MANAGER
        with gr.Tab("🛒 Transaction Manager"):
            with gr.Column(elem_classes=["transaction-panel"]):
                gr.Markdown("### ⚡ Fast-Track Financial Actions")
                with gr.Row():
                    q_date = gr.Textbox(label="Date", value=str(datetime.date.today()))
                    q_desc = gr.Textbox(label="Memo / Description", placeholder="e.g. Sales for March")
                    q_amt = gr.Number(label="Amount ($)", value=0)

                with gr.Row():
                    btn_sale = gr.Button("💰 Record Sale", variant="primary")
                    btn_stock = gr.Button("📈 Issue Equity", variant="primary")
                    btn_funds = gr.Button("🏦 Borrow Capital", variant="primary")
                    btn_ap = gr.Button("🏗️ Buy Fixed Asset", variant="primary")

            gr.Markdown("---")
            with gr.Row():
                tm_gl_view = gr.DataFrame(label="Real-time Ledger Update")
                tm_plot = gr.Plot(label="Transaction Impact")

        # TAB 3: FINANCIAL REPORTING
        with gr.Tab("🏛️ Financial Reporting"):
            gen_report_btn = gr.Button("🔄 Generate Official Statements", variant="primary")
            with gr.Row():
                with gr.Column(elem_classes=["report-box"]):
                    gr.Markdown("#### Income Statement")
                    is_out = gr.DataFrame(interactive=False)
                with gr.Column(elem_classes=["report-box"]):
                    gr.Markdown("#### Stockholders Equity")
                    se_out = gr.DataFrame(interactive=False)
            with gr.Row():
                with gr.Column(elem_classes=["report-box"]):
                    gr.Markdown("#### Balance Sheet")
                    bs_out = gr.DataFrame(interactive=False)
                with gr.Column(elem_classes=["report-box"]):
                    gr.Markdown("#### Cash Flow Statement")
                    cf_out = gr.DataFrame(interactive=False)
            gr.Markdown("#### ⚖️ Trial Balance")
            tb_out = gr.DataFrame(interactive=False)
            rep_plot = gr.Plot()

        # TAB 4: LOAN AMORTIZATION
        with gr.Tab("Loan Amortization"):
            with gr.Row():
                p_in, r_in, m_in, s_in = gr.Number(label="Principal", value=110000), gr.Number(label="Rate", value=0.05), gr.Number(label="Months", value=60), gr.Textbox(label="Date", value="2026-03-04")
                l_btn = gr.Button("Run Analysis", variant="primary")
            l_df, l_plot = gr.DataFrame(), gr.Plot()
            l_btn.click(loan_ui, [p_in, r_in, m_in, s_in], [l_df, l_plot])

        # TAB 5: ASSET DEPRECIATION (RESTORED)
        with gr.Tab("💻 Asset Depreciation"):
            with gr.Row():
                with gr.Column(scale=1):
                    ac_in = gr.Number(label="Asset Cost", value=110000)
                    al_in = gr.Number(label="Useful Life (Months)", value=60)
                    as_in = gr.Textbox(label="Acquisition Date", value="2026-03-04")
                    a_btn = gr.Button("📈 Run Depreciation", variant="primary")
                with gr.Column(scale=2):
                    a_plot = gr.Plot(label="Asset Value Decay Graph")
            a_df = gr.DataFrame(label="Depreciation Schedule", interactive=False)
            a_btn.click(asset_ui, [ac_in, al_in, as_in], [a_df, a_plot])

        # TAB 6: GENERAL LEDGER
        with gr.Tab("📓 General Ledger"):
            gl_disp = gr.DataFrame(label="Master Ledger")
            gl_refresh = gr.Button("🔄 Sync Data")
            gl_plot = gr.Plot()
            gl_refresh.click(get_account_balances, [gl_disp], [gl_disp, gl_plot])

    # Event Wiring
    gen_report_btn.click(generate_financial_reports, None, [is_out, se_out, bs_out, cf_out, tb_out, rep_plot])
    je_btn.click(add_journal_entry_from_table, [je_date, je_desc, je_input_table], [gl_disp, je_hist, je_p])

    # Fast-Track Wiring
    for btn, func in [(btn_sale, record_sale), (btn_stock, record_stock), (btn_funds, record_borrow), (btn_ap, record_asset_p)]:
        btn.click(func, [q_date, q_desc, q_amt], [gl_disp, je_hist, je_p]).then(
            lambda: (None, None, 0), None, [q_date, q_desc, q_amt]
        )

demo.launch(debug=True)
