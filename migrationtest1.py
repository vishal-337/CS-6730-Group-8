import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback


df = pd.read_csv('/Users/hamadeid/Desktop/datavisrepo/CS-6730-Group-8/migration_with_sci.tsv', sep='\t')
data = df

# Create a dictionary for state abbreviations to full names
state_abbrev = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'District of Columbia',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois',
    'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana',
    'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
    'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon',
    'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
    'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia',
    'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}

# Create a reverse mapping (full name to abbreviation)
full_to_abbrev = {v: k for k, v in state_abbrev.items()}

# Create the Dash app
app = Dash(__name__)

# Initial figure with all states having default colors
def create_base_map():
    fig = px.choropleth(
        locations=list(state_abbrev.keys()),
        locationmode="USA-states",
        scope="usa",
        color=[1] * len(state_abbrev),  # Uniform color for all states
        color_continuous_scale=[[0, 'lightgrey'], [1, 'lightgrey']],
        labels={'color': 'Migration'}
    )
    fig.update_layout(
        title="Click on a state to see migration patterns",
        geo=dict(
            lakecolor='rgb(255, 255, 255)',
            showlakes=True,
            showland=True,
            landcolor='rgb(242, 242, 242)',
        ),
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    return fig

# App layout
app.layout = html.Div([
    html.H1("US State-to-State Migration Map", 
            style={'textAlign': 'center', 'margin-bottom': '20px'}),
    html.P("Click on any state to see migration numbers to other states",
           style={'textAlign': 'center'}),
    dcc.Graph(
        id='migration-map',
        figure=create_base_map(),  # Initialize with a base map
        style={'width': '100%', 'height': '80vh'}
    ),
    html.Div(id='selected-state', 
             style={'margin-top': '20px', 'font-weight': 'bold', 'textAlign': 'center'})
])

# Callback for updating the map based on click events
@callback(
    [Output('migration-map', 'figure'),
     Output('selected-state', 'children')],
    [Input('migration-map', 'clickData')]
)
def update_map(click_data):
    if click_data is None:
        return create_base_map(), "Click on a state to see migration patterns"
    
    # Get the clicked state abbreviation
    clicked_state_abbrev = click_data['points'][0]['location']
    clicked_state = state_abbrev.get(clicked_state_abbrev)
    
    if clicked_state is None:
        return create_base_map(), f"State data not available for {clicked_state_abbrev}"
    
    # For the demo, generate sample migration values for all states from the clicked state
    # In a real implementation, you would pull this from your complete dataset
    sample_data = []
    max_migration = 20000  # For scaling colors
    
    for abbrev, full_name in state_abbrev.items():
        # Skip the state itself
        if full_name == clicked_state:
            continue
            
        # Check if we have actual data for this pair
        state_pair = df[(df['Origin'] == clicked_state) & (df['Destination'] == full_name)]
        
        if len(state_pair) > 0:
            migration_value = state_pair['Migration #'].values[0]
        else:
            # Generate a placeholder value for demo purposes
            # In your real implementation, use your actual data
            migration_value = 100  # Default value
            
        sample_data.append({
            'state_abbrev': abbrev,
            'state_name': full_name,
            'migration': migration_value
        })
    
    # Create a DataFrame for the choropleth
    sample_df = pd.DataFrame(sample_data)
    
    # Create the updated map
    fig = px.choropleth(
        sample_df,
        locations='state_abbrev',
        locationmode="USA-states",
        scope="usa",
        color='migration',
        color_continuous_scale="Viridis",  # Different color scale for migration
        range_color=[0, max_migration],
        labels={'migration': 'Migration'},
        hover_name='state_name',
        hover_data={
            'state_abbrev': False, 
            'migration': True
        }
    )
    
    # Highlight the selected state in red
    fig.add_trace(
        go.Choropleth(
            locations=[clicked_state_abbrev],
            z=[1],
            locationmode="USA-states",
            colorscale=[[0, 'rgb(255, 0, 0)'], [1, 'rgb(255, 0, 0)']],
            showscale=False,
            hoverinfo='text',
            text=clicked_state
        )
    )
    
    fig.update_layout(
        title_text=f'Migration from {clicked_state} to other states',
        geo=dict(
            lakecolor='rgb(255, 255, 255)',
            showlakes=True,
            showland=True,
            landcolor='rgb(242, 242, 242)',
        ),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig, f"Selected State: {clicked_state}"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)