import streamlit as st


def init_session_state() -> None:
    if "topics" not in st.session_state:
        st.session_state.topics = None  # List[str] | None
    if "top_topics" not in st.session_state:
        st.session_state.top_topics = None  # List[{"rank": int, "topic": str}] | None
    if "csv_data" not in st.session_state:
        st.session_state.csv_data = None  # str | None
    if "edited_csv_data" not in st.session_state:
        st.session_state.edited_csv_data = None  # str | None
    if "is_csv_edited" not in st.session_state:
        st.session_state.is_csv_edited = False  # bool
    if "csv_version" not in st.session_state:
        st.session_state.csv_version = 0  # int


def safe_rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()
