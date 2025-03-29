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
token_name = st.secrets["tableau"]["token_name"]
token_value = st.secrets["tableau"]["personal_access_token"]
workbook_name = "SCI"
view_name = "Dashboard 1"

# Format for trusted authentication
# :embed=yes&:toolbar=no adds parameters to avoid login and customize display
trusted_tableau_url = f"{server_url}/t/{site_id}/views/{workbook_name}/{view_name.replace(' ', '')}?:embed=yes&:toolbar=yes&:tabs=no&:token_type=personal_access_token&:token_name={token_name}&:token_value={token_value}"

# Use iframe for simpler embedding with authentication tokens in URL
tableau_embed_html = f"""
<div style='width: 100%; height: 800px;'>
    <iframe src="{trusted_tableau_url}" 
            frameborder="0" 
            width="100%" 
            height="100%" 
            allowfullscreen>
    </iframe>
</div>
"""

components.html(tableau_embed_html, height=800)

with st.expander("About SCI"):
    st.write("""
    The Social Connectedness Index (SCI) measures the strength of connectedness between 
    geographic areas as represented by social network friendships.
    """) 