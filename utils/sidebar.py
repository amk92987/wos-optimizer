"""
Sidebar utilities with custom collapse toggle.
Provides icon-only mode since Streamlit doesn't support it natively.
"""

import streamlit as st


COLLAPSED_CSS = """
<style>
[data-testid="stSidebar"] {
    width: 90px !important;
    min-width: 90px !important;
}
[data-testid="stSidebar"] > div:first-child {
    width: 90px !important;
}
/* Hide the logo text when collapsed */
[data-testid="stLogo"] {
    display: none !important;
}
</style>
"""


def init_sidebar_state():
    """Initialize sidebar collapsed state in session."""
    if "sidebar_collapsed" not in st.session_state:
        st.session_state.sidebar_collapsed = False


def toggle_sidebar():
    """Toggle sidebar collapsed state."""
    st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed


def is_collapsed() -> bool:
    """Check if sidebar is in collapsed (icon-only) mode."""
    init_sidebar_state()
    return st.session_state.sidebar_collapsed


def render_toggle_button():
    """Render the collapse/expand toggle button."""
    init_sidebar_state()

    if st.session_state.sidebar_collapsed:
        # Show expand button (arrow right)
        if st.button("▶", key="sidebar_toggle", help="Expand sidebar", use_container_width=True):
            toggle_sidebar()
            st.rerun()
    else:
        # Show collapse button (arrow left)
        if st.button("◀", key="sidebar_toggle", help="Collapse sidebar", use_container_width=True):
            toggle_sidebar()
            st.rerun()


def render_sidebar_content(full_content_func, icons_only_func=None):
    """
    Render sidebar with toggle support.

    Args:
        full_content_func: Function to call when sidebar is expanded
        icons_only_func: Optional function for collapsed state (shows nothing if None)
    """
    with st.sidebar:
        render_toggle_button()

        if is_collapsed():
            if icons_only_func:
                icons_only_func()
            # In collapsed mode, show minimal content
        else:
            full_content_func()
