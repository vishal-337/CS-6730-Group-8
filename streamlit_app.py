import streamlit as st
import tableauserverclient as TSC
import streamlit.components.v1 as components

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

st.subheader("COVID Data")
covid_tableau_html = """
<div class='tableauPlaceholder' id='viz1743210082495' style='position: relative'><noscript><a href='#'><img alt='Daily cases&#47; Month ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;6H&#47;6HTWTQ2C9&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='path' value='shared&#47;6HTWTQ2C9' /> <param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;6H&#47;6HTWTQ2C9&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>
<script type='text/javascript'>
    var divElement = document.getElementById('viz1743210082495');
    var vizElement = divElement.getElementsByTagName('object')[0];
    vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';
    var scriptElement = document.createElement('script');
    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
    vizElement.parentNode.insertBefore(scriptElement, vizElement);
</script>
"""
components.html(covid_tableau_html, height=600)

with st.expander("About SCI"):
    st.write("""
    The Social Connectedness Index (SCI) measures the strength of connectedness between 
    geographic areas as represented by social network friendships.
    """) 