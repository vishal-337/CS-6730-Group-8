import streamlit as st
import tableauserverclient as TSC

# Set page configuration
st.set_page_config(
    page_title="SCI: Social Connectedness Index",
    page_icon="🌐",
    layout="wide"
)

# Main title
st.title("SCI: Social Connectedness Index")

# Set up connection to Tableau
tableau_auth = TSC.PersonalAccessTokenAuth(
    st.secrets["tableau"]["token_name"],
    st.secrets["tableau"]["personal_access_token"],
    st.secrets["tableau"]["site_id"],
)
server = TSC.Server(st.secrets["tableau"]["server_url"], use_server_version=True)

# Specific workbook ID from the URL
TARGET_WORKBOOK_ID = "2526031"
TARGET_VIEW_NAME = "Dashboard 1"

# Get various data from Tableau
@st.cache_data(ttl=600)
def get_dashboard():
    with server.auth.sign_in(tableau_auth):
        workbooks, pagination_item = server.workbooks.get()
        
        target_workbook = None
        for workbook in workbooks:
            if workbook.id == TARGET_WORKBOOK_ID or workbook.name == "SCI":
                target_workbook = workbook
                break
                
        if target_workbook:
            server.workbooks.populate_views(target_workbook)
            
            dashboard_view = None
            for view in target_workbook.views:
                if view.name == TARGET_VIEW_NAME:
                    dashboard_view = view
                    break
            
            if dashboard_view:
                server.views.populate_image(dashboard_view)
                return dashboard_view.image
            
            elif target_workbook.views:
                view_item = target_workbook.views[0]
                server.views.populate_image(view_item)
                return view_item.image
                
        return None

try:
    dashboard_image = get_dashboard()
    
    if dashboard_image:
        st.image(dashboard_image)
    else:
        st.error("Dashboard not found")
        
except Exception as e:
    st.error(f"Error: {str(e)}")

with st.expander("About SCI"):
    st.write("""
    The Social Connectedness Index (SCI) measures the strength of connectedness between 
    geographic areas as represented by social network friendships.
    """) 