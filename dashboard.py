import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
import random
from datetime import datetime, timedelta

# Step 1: Generate sample data (replace with your real data loading)
def generate_sample_data(num_rows=10000):
    categories = ['Electronics', 'Clothing', 'Books', 'Groceries', 'Furniture']
    regions = ['North', 'South', 'East', 'West']
    start_date = datetime(2023, 1, 1)
    
    data = {
        'Date': [start_date + timedelta(days=random.randint(0, 365)) for _ in range(num_rows)],
        'Category': [random.choice(categories) for _ in range(num_rows)],
        'Region': [random.choice(regions) for _ in range(num_rows)],
        'Sales': [random.uniform(10, 1000) for _ in range(num_rows)]
    }
    return pd.DataFrame(data)

df = generate_sample_data()

# Step 2: Pre-aggregate data for faster queries
# Aggregate by Category and Region
agg_category_region = df.groupby(['Category', 'Region']).agg(
    Total_Sales=('Sales', 'sum'),
    Avg_Sales=('Sales', 'mean'),
    Transaction_Count=('Sales', 'count')
).reset_index()

# Aggregate by Month for time series
df['Month'] = df['Date'].dt.to_period('M')
agg_monthly = df.groupby('Month').agg(
    Total_Sales=('Sales', 'sum')
).reset_index()
agg_monthly['Month'] = agg_monthly['Month'].astype(str)  # For plotting

# Step 3: Initialize Dash app
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Interactive BI Dashboard: Sales Analytics"),
    
    html.Div([
        html.Label("Filter by Category:"),
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': cat, 'value': cat} for cat in sorted(df['Category'].unique())] + [{'label': 'All', 'value': 'All'}],
            value='All'
        ),
        
        html.Label("Filter by Region:"),
        dcc.Dropdown(
            id='region-dropdown',
            options=[{'label': reg, 'value': reg} for reg in sorted(df['Region'].unique())] + [{'label': 'All', 'value': 'All'}],
            value='All'
        ),
    ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
    
    html.Div([
        dcc.Graph(id='sales-bar-chart'),
        dcc.Graph(id='monthly-line-chart'),
        dash_table.DataTable(
            id='agg-table',
            columns=[{"name": i, "id": i} for i in agg_category_region.columns],
            data=agg_category_region.to_dict('records'),
            page_size=10
        )
    ], style={'width': '70%', 'display': 'inline-block'})
])

# Callbacks for interactivity (using aggregated data for speed)
@app.callback(
    [Output('sales-bar-chart', 'figure'),
     Output('monthly-line-chart', 'figure'),
     Output('agg-table', 'data')],
    [Input('category-dropdown', 'value'),
     Input('region-dropdown', 'value')]
)
def update_dashboard(selected_category, selected_region):
    # Filter aggregated data (fast since it's pre-aggregated)
    filtered_agg_cr = agg_category_region.copy()
    if selected_category != 'All':
        filtered_agg_cr = filtered_agg_cr[filtered_agg_cr['Category'] == selected_category]
    if selected_region != 'All':
        filtered_agg_cr = filtered_agg_cr[filtered_agg_cr['Region'] == selected_region]
    
    # Bar chart: Total Sales by Category/Region
    bar_fig = px.bar(
        filtered_agg_cr,
        x='Category',
        y='Total_Sales',
        color='Region',
        title='Total Sales by Category and Region'
    )
    
    # Line chart: Monthly Sales (from monthly aggregate, unaffected by category/region filters for simplicity)
    line_fig = px.line(
        agg_monthly,
        x='Month',
        y='Total_Sales',
        title='Monthly Sales Trend'
    )
    
    # Table data
    table_data = filtered_agg_cr.to_dict('records')
    
    return bar_fig, line_fig, table_data

# Run the app
if __name__ == '__main__':
    app.run(debug=True)