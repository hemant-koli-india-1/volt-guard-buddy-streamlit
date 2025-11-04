import streamlit as st
import pandas as pd
from datetime import datetime

from utils.battery_functions import (
    add_battery,
    delete_battery,
    filter_inventory,
    handover_status,
    read_batteries,
    scan_battery,
    status_color,
    update_voltage,
)
from utils.stakeholder_functions import (
    add_stakeholder,
    delete_stakeholder,
    read_stakeholders,
    update_stakeholder,
)


st.set_page_config(page_title="Volt Guard Buddy", layout="wide")

# --- Global Styles (lightweight CSS to match provided wireframe look) ---
st.markdown(
    """
    <style>
      .vg-container {padding: 8px 16px;}
      .vg-card {background: #fff; border: 1px solid #EEF0F2; border-radius: 10px; padding: 16px;}
      .vg-muted {color: #667085; font-size: 13px;}
      .vg-title {font-size: 26px; font-weight: 800; margin: 4px 0 10px 0;}
      .vg-kpi {text-align:center; border: 1px solid #EEF0F2; border-radius: 10px; padding: 16px;}
      .vg-kpi .num {font-size: 28px; font-weight: 800;}
      .vg-tabs {background: #F7F8FA; border:1px solid #EEF0F2; border-radius: 8px; padding: 6px;}
      .vg-badge {padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; display:inline-block}
      .badge-green {background:#ECFDF3; color:#027A48; border:1px solid #A6F4C5}
      .badge-yellow {background:#FFFAEB; color:#B54708; border:1px solid #FEDF89}
      .badge-red {background:#FEF3F2; color:#B42318; border:1px solid #FECDCA}
      .badge-gray {background:#F2F4F7; color:#344054; border:1px solid #EAECF0}
      .vg-section-title {font-size:18px; font-weight:800; margin-bottom:8px}
      .vg-actions button {width:100%}
      .vg-divider {height: 1px; background:#EEF0F2; margin: 10px 0}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown(
    "<div class='vg-container'><div class='vg-title'>🔋 Battery Management System</div><div class='vg-muted'>Monitor battery voltage, track maintenance schedules, and automate stakeholder notifications</div></div>",
    unsafe_allow_html=True,
)

# --- Dashboard KPIs ---
def compute_dashboard():
    b_df = read_batteries()
    if b_df is None or b_df.empty:
        return 0, 0, 0, 0
    vol = pd.to_numeric(b_df["current_voltage"], errors="coerce")
    total = len(b_df)
    active = (b_df["status"].astype(str).str.lower() == "active").sum()
    low = (vol.between(10.5, 11, inclusive="left")).sum()
    need = (vol < 10.5).sum()
    return int(total), int(active), int(low), int(need)

total_k, active_k, low_k, need_k = compute_dashboard()
colk1, colk2, colk3, colk4 = st.columns(4)
with colk1:
    st.markdown(
        f"<div class='vg-kpi'><div class='num'>{total_k}</div><div class='vg-muted'>Total Batteries</div></div>",
        unsafe_allow_html=True,
    )
with colk2:
    st.markdown(
        f"<div class='vg-kpi'><div class='num'>{active_k}</div><div class='vg-muted'>Active</div></div>",
        unsafe_allow_html=True,
    )
with colk3:
    st.markdown(
        f"<div class='vg-kpi'><div class='num'>{low_k}</div><div class='vg-muted'>Low Voltage</div></div>",
        unsafe_allow_html=True,
    )
with colk4:
    st.markdown(
        f"<div class='vg-kpi'><div class='num'>{need_k}</div><div class='vg-muted'>Need Charging</div></div>",
        unsafe_allow_html=True,
    )


tab_scanner, tab_inventory, tab_stakeholders, tab_reports = st.tabs(
    ["Scanner", "Inventory", "Stakeholders", "Reports"]
)


with tab_scanner:
    st.header("Scanner")
    identifier = st.text_input("Enter Product Number or Battery ID", key="scanner_input")
    col1, col2 = st.columns([1, 1])
    with col1:
        scan_clicked = st.button("Scan / Find Battery")
    with col2:
        add_clicked = st.button("Add New Battery")

    if scan_clicked and identifier.strip():
        found = scan_battery(identifier.strip())
        if found is not None:
            st.success(
                f"Found Battery ID {found['id']} | Product {found['product_number']} | Voltage {found['current_voltage']} | Last Check {found['last_checked_date']}"
            )
        else:
            st.warning("Battery not found. You can add it using 'Add New Battery'.")
    elif scan_clicked:
        st.error("Please enter a value to scan.")

    with st.expander("Add Battery"):
        pn = st.text_input("Product Number", key="add_pn")
        pm = st.text_input("Packing Month (YYYY-MM)", key="add_pm")
        iv = st.number_input("Initial Voltage (optional)", key="add_iv", step=0.1, format="%.2f")
        if add_clicked:
            if not pn.strip():
                st.error("Product Number is required.")
            else:
                added = add_battery(pn.strip(), pm.strip() or None, float(iv) if iv else None)
                st.success(f"Added Battery ID {added['id']} for product {added['product_number']}")


with tab_inventory:
    st.markdown("<div class='vg-section-title'>Battery Inventory</div>", unsafe_allow_html=True)
    # Filters & Export
    fc1, fc2, fc3, fc4, fc5 = st.columns([2, 1, 1, 1, 1])
    with fc1:
        f_product = st.text_input("Filter: Product Number contains")
    with fc2:
        f_status = st.selectbox("Status", options=["", "active", "SPD", "production"], index=0)
    with fc3:
        f_vmin = st.number_input("Min Voltage", value=0.0, step=0.1)
    with fc4:
        f_vmax = st.number_input("Max Voltage", value=100.0, step=0.1)
    with fc5:
        # Export button
        bdf_export = read_batteries()
        if bdf_export is None:
            bdf_export = pd.DataFrame()
        st.download_button(
            label="Export CSV",
            data=bdf_export.to_csv(index=False).encode("utf-8"),
            file_name="battery_inventory.csv",
            mime="text/csv",
        )

    inv_df = filter_inventory(
        product_query=f_product or None,
        status=f_status or None,
        voltage_min=f_vmin if f_vmin > 0 else None,
        voltage_max=f_vmax if f_vmax < 100 else None,
    )

    # Metrics
    colm1, colm2, colm3, colm4 = st.columns(4)
    with colm1:
        st.metric("Total", len(inv_df))
    with colm2:
        st.metric("Red (<10.5V)", (pd.to_numeric(inv_df["current_voltage"], errors="coerce") < 10.5).sum())
    with colm3:
        st.metric(
            "Yellow (10.5-11V)",
            (
                (pd.to_numeric(inv_df["current_voltage"], errors="coerce") >= 10.5)
                & (pd.to_numeric(inv_df["current_voltage"], errors="coerce") < 11)
            ).sum(),
        )
    with colm4:
        st.metric("Green (>=11V)", (pd.to_numeric(inv_df["current_voltage"], errors="coerce") >= 11).sum())

    # Render with style badges and days since check
    def _badge(v: float | None) -> str:
        c = status_color(v if v is not None else None)
        label = (
            "Active"
            if c == "green"
            else ("Low" if c == "yellow" else ("Critical" if c == "red" else "Unknown"))
        )
        klass = {"green": "badge-green", "yellow": "badge-yellow", "red": "badge-red", "gray": "badge-gray"}.get(
            c, "badge-gray"
        )
        return f"<span class='vg-badge {klass}'>{label}</span>"

    df_show = inv_df.copy()
    # Days since last check
    if not df_show.empty:
        df_show["days_since_check"] = (
            pd.Timestamp.now() - pd.to_datetime(df_show["last_checked_date"], errors="coerce")
        ).dt.days
        df_show["status_badge"] = [
            _badge(v if pd.notna(v) else None)
            for v in pd.to_numeric(df_show["current_voltage"], errors="coerce")
        ]

        # Order and rename
        df_show = df_show[
            [
                "product_number",
                "current_voltage",
                "status_badge",
                "last_checked_date",
                "days_since_check",
                "id",
            ]
        ].rename(
            columns={
                "product_number": "Product Number",
                "current_voltage": "Voltage (V)",
                "status_badge": "Status",
                "last_checked_date": "Last Checked",
                "days_since_check": "Days Since Check",
                "id": "ID",
            }
        )

        # Display with HTML for badges
        st.write(
            df_show.to_html(escape=False, index=False),
            unsafe_allow_html=True,
        )
    else:
        st.info("No batteries found.")

    st.subheader("Row Actions")
    row_id = st.number_input("Select Battery ID", step=1, min_value=0)
    ac1, ac2, ac3 = st.columns([1, 1, 1])
    with ac1:
        open_update = st.toggle("Open Update Voltage Form")
    with ac2:
        open_delete = st.toggle("Open Delete Confirmation")
    with ac3:
        open_handover = st.toggle("Open Handover")

    if open_update:
        st.markdown("<div class='vg-card'>", unsafe_allow_html=True)
        st.markdown("<div class='vg-section-title'>Update Battery</div>", unsafe_allow_html=True)
        last_df = read_batteries()
        last_row = last_df.loc[last_df["id"] == int(row_id)] if not last_df.empty else pd.DataFrame()
        last_v = None
        if not last_row.empty:
            last_v = pd.to_numeric(last_row.iloc[0]["current_voltage"], errors="coerce")
            st.markdown(
                f"<div class='vg-muted'>Last Reading: <b>{'' if pd.isna(last_v) else f'{last_v:.2f}V'}</b></div>",
                unsafe_allow_html=True,
            )
        with st.form("update_voltage_form"):
            uv = st.number_input("Current Reading (V)", step=0.1, format="%.2f")
            # live status preview
            badge_html = {
                "red": "<span class='vg-badge badge-red'>Critical - Will be rejected</span>",
                "yellow": "<span class='vg-badge badge-yellow'>Low - Needs attention</span>",
                "green": "<span class='vg-badge badge-green'>Full</span>",
                "gray": "<span class='vg-badge badge-gray'>Unknown</span>",
            }[status_color(float(uv))]
            st.markdown(badge_html, unsafe_allow_html=True)
            uvd = st.number_input("Voltage During Check (optional)", step=0.1, format="%.2f")
            uby = st.text_input("Checked By")
            notes = st.text_area("Notes")
            sub = st.form_submit_button("Update Battery")
            if sub:
                try:
                    update_voltage(
                        int(row_id),
                        float(uv),
                        uby.strip(),
                        notes.strip() or None,
                        float(uvd) if uvd else None,
                    )
                    st.success(f"Updated battery {int(row_id)} to {float(uv):.2f}V")
                except Exception as e:
                    st.error(str(e))
        st.markdown("</div>", unsafe_allow_html=True)


    if open_delete:
        st.warning("This will permanently delete the battery record.")
        coldd1, coldd2 = st.columns([1, 1])
        with coldd1:
            confirm = st.checkbox("Confirm delete")
        with coldd2:
            if st.button("Delete"):
                if confirm and row_id:
                    if delete_battery(int(row_id)):
                        st.success("Deleted.")
                    else:
                        st.error("Battery not found.")
                else:
                    st.error("Please confirm and provide a valid ID.")

    if open_handover:
        colh1, colh2 = st.columns([1, 1])
        with colh1:
            if st.button("Hand Over to SPD"):
                try:
                    res = handover_status(int(row_id), "SPD")
                    st.success("Status updated to SPD")
                except Exception as e:
                    st.error(str(e))
        with colh2:
            if st.button("Hand Over to Production"):
                try:
                    res = handover_status(int(row_id), "production")
                    st.success("Status updated to production")
                except Exception as e:
                    st.error(str(e))


with tab_stakeholders:
    st.markdown("<div class='vg-section-title'>Email Stakeholders</div>", unsafe_allow_html=True)
    stk_df = read_stakeholders()

    with st.form("add_stakeholder_form"):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            name = st.text_input("Name")
        with c2:
            email = st.text_input("Email")
        with c3:
            sub = st.form_submit_button("+ Add Stakeholder")
        if sub:
            if not name.strip() or not email.strip():
                st.error("Name and Email required.")
            else:
                added = add_stakeholder(name.strip(), email.strip())
                st.success(f"Added stakeholder {added['name']}")

    if stk_df is not None and not stk_df.empty:
        st.table(stk_df.rename(columns={"name": "Name", "email": "Email", "id": "ID"}))
    else:
        st.info("No stakeholders added yet.")

    st.markdown("<div class='vg-divider'></div>", unsafe_allow_html=True)
    st.subheader("Manage Stakeholder")
    stk_id = st.number_input("Stakeholder ID", step=1, min_value=0)
    cse1, cse2 = st.columns([1, 1])
    with cse1:
        with st.form("edit_stakeholder_form"):
            new_name = st.text_input("New Name (optional)")
            new_email = st.text_input("New Email (optional)")
            subm = st.form_submit_button("Update")
            if subm:
                try:
                    update_stakeholder(int(stk_id), new_name.strip() or None, new_email.strip() or None)
                    st.success("Stakeholder updated.")
                except Exception as e:
                    st.error(str(e))
    with cse2:
        st.warning("This will remove the stakeholder.")
        confirm_s = st.checkbox("Confirm remove")
        if st.button("Delete Stakeholder"):
            if confirm_s and stk_id:
                ok = delete_stakeholder(int(stk_id))
                st.success("Deleted." if ok else "Not found.")
            else:
                st.error("Please confirm and provide a valid ID.")


with tab_reports:
    st.header("Reports")
    b_df = read_batteries()
    stk_df = read_stakeholders()
    if b_df is not None and not b_df.empty:
        critical = b_df[pd.to_numeric(b_df["current_voltage"], errors="coerce") < 10.5]
        st.subheader("Critical (<10.5V)")
        st.dataframe(critical, use_container_width=True)
    else:
        st.info("No batteries found.")

    btn_disabled = stk_df.empty if stk_df is not None else True
    if st.button("Send Email Report (Simulated)", disabled=btn_disabled):
        if btn_disabled:
            st.error("No stakeholders available. Add stakeholders first.")
        else:
            st.success("Email report would be sent here (SMTP not configured).")


