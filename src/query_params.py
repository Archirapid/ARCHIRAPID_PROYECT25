import streamlit as st

"""Cross-module helpers to safely interact with Streamlit query parameters.

Updated to use the stable st.query_params API.
"""


def get_query_params():
    """Get current query parameters."""
    return st.query_params


def set_query_params(new_q: dict):
    """Set query parameters."""
    st.query_params.update(new_q)


def update_query_params(**kwargs):
    """Update query parameters with new values."""
    st.query_params.update(kwargs)


def clear_query_params():
    """Clear all query parameters."""
    st.query_params.clear()
