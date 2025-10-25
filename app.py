import os
from datetime import datetime

import pandas as pd
import streamlit as st

from db import (
    init_db,
    list_websites,
    add_website,
    update_website,
    import_csv,
    export_csv,
    get_activity,
)


# Initialize DB
init_db()

st.set_page_config(page_title="Link Building Workflow", layout="wide")

st.title("Link Building Workflow Manager")

BASE_DIR = os.path.dirname(__file__)

with st.sidebar:
    st.header("Quick actions")
    # simple per-user identity (used for activity logs)
    user = st.text_input("Your name / user id", value=st.session_state.get('user', ''))
    st.session_state['user'] = user

    upload = st.file_uploader("Upload CSV with websites", type=["csv"])
    if upload is not None:
        # save temp and import
        temp_path = os.path.join(BASE_DIR, "__upload_temp.csv")
        with open(temp_path, "wb") as f:
            import os
            from datetime import datetime

            import pandas as pd
            import streamlit as st

            from db import (
                init_db,
                list_websites,
                add_website,
                update_website,
                import_csv,
                export_csv,
                get_activity,
            )


            # Initialize DB
            init_db()

            st.set_page_config(page_title="Link Building Workflow", layout="wide")

            st.title("Link Building Workflow Manager")

            BASE_DIR = os.path.dirname(__file__)

            with st.sidebar:
                st.header("Quick actions")
                # simple per-user identity (used for activity logs)
                user = st.text_input("Your name / user id", value=st.session_state.get('user', ''))
                st.session_state['user'] = user

                upload = st.file_uploader("Upload CSV with websites", type=["csv"])
                if upload is not None:
                    # save temp and import
                    temp_path = os.path.join(BASE_DIR, "__upload_temp.csv")
                    with open(temp_path, "wb") as f:
                        f.write(upload.getbuffer())
                    added = import_csv(temp_path, source="upload")
                    st.success(f"Imported {added} rows")
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass

                if st.button("Export all to CSV"):
                    out_path = os.path.join(BASE_DIR, "websites_export.csv")
                    n = export_csv(out_path)
                    st.success(f"Exported {n} rows to {out_path}")

                st.markdown("---")
                st.markdown("Filters")
                module_filter = st.selectbox("Module", options=["", "Free", "Outreach", "Exchange", "Pay"])
                status_filter = st.text_input("Status (exact)")
                min_da = st.number_input("Min DA", min_value=0, max_value=100, value=0)
                max_da = st.number_input("Max DA", min_value=0, max_value=100, value=100)


            def websites_to_df(rows):
                data = []
                for r in rows:
                    data.append({
                        'id': r.id,
                        'website': r.website,
                        'contact_name': r.contact_name,
                        'contact_email': r.contact_email,
                        'module': r.module,
                        'traffic': r.traffic,
                        'da': r.da,
                        'status': r.status,
                        'assignee': r.assignee,
                        'notes': (r.notes[:200] + '...') if r.notes and len(r.notes) > 200 else r.notes,
                        'created_at': r.created_at,
                        'updated_at': r.updated_at,
                    })
                return pd.DataFrame(data)


            def refresh_data():
                filters = {'module': module_filter or None, 'status': status_filter or None, 'min_da': min_da, 'max_da': max_da}
                rows = list_websites(filters=filters, limit=5000)
                return rows


            rows = refresh_data()
            df = websites_to_df(rows)


            # helper to safely rerun in different streamlit versions
            def do_rerun():
                # Try to call Streamlit's experimental rerun if available, otherwise
                # force a rerun by changing query params or toggling a session flag.
                rerun_fn = getattr(st, "experimental_rerun", None)
                if callable(rerun_fn):
                    try:
                        rerun_fn()
                        return
                    except Exception:
                        pass

                try:
                    params = st.experimental_get_query_params()
                    params["_refresh"] = datetime.utcnow().isoformat()
                    st.experimental_set_query_params(**params)
                except Exception:
                    st.session_state['_refresh'] = datetime.utcnow().isoformat()

            st.subheader("Website list")
            st.write("Showing results from DB. Use filters in the sidebar.")
            st.dataframe(df)

            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("Add new website")
                with st.form("add_form"):
                    website = st.text_input("Website URL")
                    contact_name = st.text_input("Contact Name")
                    contact_email = st.text_input("Contact Email")
                    module = st.selectbox("Module", ["Free", "Outreach", "Exchange", "Pay"], index=0)
                    traffic = st.number_input("Traffic", min_value=0, value=0)
                    da = st.number_input("Domain Authority (DA)", min_value=0, max_value=100, value=0)
                    status = st.selectbox("Status", ["New", "Contacted", "Follow-up", "Approved", "Draft Sent", "Published", "Rejected", "Archived"], index=0)
                    assignee = st.text_input("Assignee")
                    notes = st.text_area("Notes")
                    submitted = st.form_submit_button("Add website")
                    if submitted:
                        if not website or str(website).strip() == "":
                            st.error("Website is required")
                        else:
                            data = {
                                'website': website.strip(),
                                'contact_name': contact_name.strip() or None,
                                'contact_email': contact_email.strip() or None,
                                'module': module,
                                'traffic': int(traffic) if traffic else None,
                                'da': int(da) if da else None,
                                'status': status,
                                'assignee': assignee.strip() or None,
                                'notes': notes.strip() or None,
                                'source': 'manual',
                            }
                            w = add_website(data, user=st.session_state.get('user'))
                            st.success(f"Added website id={w.id}")
                            do_rerun()

            with col2:
                st.subheader("Edit / Update")
                id_options = df['id'].tolist() if not df.empty else []
                if id_options:
                    selected_id = st.selectbox("Select website id", options=id_options)
                    selected_row = df[df['id'] == selected_id].iloc[0]
                    st.markdown(f"**{selected_row['website']}**")
                    st.write(selected_row.to_dict())

                    with st.form("edit_form"):
                        new_status = st.selectbox("Status", ["New", "Contacted", "Follow-up", "Approved", "Draft Sent", "Published", "Rejected", "Archived"], index=0)
                        add_note = st.text_area("Add note")
                        assign_to = st.text_input("Assign to", value=selected_row.get('assignee') or "")
                        submitted_edit = st.form_submit_button("Save")
                        if submitted_edit:
                            updates = {'status': new_status, 'assignee': assign_to or None}
                            if add_note and add_note.strip():
                                # append to notes
                                existing = selected_row.get('notes') or ''
                                combined = (existing + "\n" + f"[{datetime.utcnow().isoformat()}] {add_note.strip()}") if existing else f"[{datetime.utcnow().isoformat()}] {add_note.strip()}"
                                updates['notes'] = combined
                                updates['action'] = 'note_added'
                            w = update_website(int(selected_id), updates, user=st.session_state.get('user') or 'web-ui')
                            if w:
                                st.success("Updated")
                                do_rerun()
                            else:
                                st.error("Failed to update (maybe removed)")
                else:
                    st.info("No websites to edit. Add one or upload a CSV.")

            st.markdown("---")
            st.subheader("Activity log for a website")
            with st.expander("View activity"):
                activity_id = st.number_input("Website id (enter) to view activity", min_value=0, value=0, step=1)
                if activity_id:
                    logs = get_activity(int(activity_id))
                    if logs:
                        df_logs = pd.DataFrame([{'timestamp': l.timestamp, 'action': l.action, 'note': l.note, 'user': l.user} for l in logs])
                        st.dataframe(df_logs)
                    else:
                        st.info("No activity found for that id")

            st.caption("Database is stored as `websites.db` in the app folder. Use Export to create CSV backups.")
