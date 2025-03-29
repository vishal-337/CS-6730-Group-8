import streamlit as st
import streamlit.components.v1 as components

# Set page configuration
st.set_page_config(
    page_title="SCI: Social Connectedness Index",
    page_icon="🌐",
    layout="wide"
)

# Main title
st.title("SCI: Social Connectedness Index")

server_url = st.secrets["tableau"]["server_url"].rstrip("/")
site_id = st.secrets["tableau"]["site_id"]
workbook_name = "SCI"
view_name = "Dashboard 1"

# Format: https://server/t/site/views/workbook/view
tableau_url = f"{server_url}/t/{site_id}/views/{workbook_name}/{view_name.replace(' ', '')}"

tableau_embed_html = f"""
<div style='width: 100%; height: 800px;'>
    <script type='text/javascript' src='https://public.tableau.com/javascripts/api/tableau-2.min.js'></script>
    <div id='vizContainer' style='width: 100%; height: 100%;'></div>
    <script type='text/javascript'>
        function initViz() {{
            const containerDiv = document.getElementById('vizContainer');
            const vizUrl = '{tableau_url}';
            const options = {{
                hideTabs: true,
                hideToolbar: false,
                width: '100%',
                height: '100%'
            }};
            
            new tableau.Viz(containerDiv, vizUrl, options);
        }}
        
        document.addEventListener('DOMContentLoaded', initViz);
    </script>
</div>
"""

components.html(tableau_embed_html, height=800)

with st.expander("About SCI"):
    st.write("""
    The Social Connectedness Index (SCI) measures the strength of connectedness between 
    geographic areas as represented by social network friendships.
    """) 