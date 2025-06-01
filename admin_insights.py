import streamlit as st

def show_admin_insights():
    st.header("📊 Poll Results Overview")
    for poll in st.session_state.polls:
        st.subheader(poll["question"])
        total = sum(poll["votes"].values())
        for option, count in poll["votes"].items():
            percent = (count / total * 100) if total else 0
            st.write(f"- {option}: {count} votes ({percent:.2f}%)")

    st.header("👀 Notification View Tracker")
    for idx, notif in enumerate(st.session_state.notifications):
        viewers = st.session_state.notif_views.get(idx, set())
        st.subheader(f"{notif['timestamp']} - {notif['text']}")
        if viewers:
            st.write(f"Viewed by ({len(viewers)}): {', '.join(viewers)}")
        else:
            st.write("No views yet.")
