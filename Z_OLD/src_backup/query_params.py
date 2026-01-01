import streamlit as st

"""Cross-module helpers to safely interact with Streamlit query parameters.

Some Streamlit environments may use older experimental APIs alongside the newer
`st.query_params` stable API; calling both in the same script raises
StreamlitAPIException. These helpers prefer `st.query_params` but gracefully
fallback to `st.experimental_get_query_params`/`st.experimental_set_query_params`
if needed.
"""


def get_query_params():
    try:
        return st.query_params
    except Exception:
        try:
            return st.experimental_get_query_params()
        except Exception:
            return {}


def set_query_params(new_q: dict):
    try:
        st.query_params = new_q
    except Exception:
        try:
            st.experimental_set_query_params(**new_q)
        except Exception:
            pass


def update_query_params(**kwargs):
    try:
        st.query_params.update(kwargs)
    except Exception:
        try:
            st.experimental_set_query_params(**kwargs)
        except Exception:
            pass


def clear_query_params():
    try:
        st.query_params.clear()
    except Exception:
        try:
            st.experimental_set_query_params()
        except Exception:
            pass
