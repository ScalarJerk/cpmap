import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from pathlib import Path

# Add the project directory to the path so we can import our modules
project_dir = Path(__file__).parent.parent
sys.path.append(str(project_dir))

from analysis.startup_clustering import StartupClustering
from analysis.data_processor import DataProcessor

# Set page config
st.set_page_config(
    page_title="AI Startup Competitive Positioning Map",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("AI Startup Competitive Positioning Map")
st.markdown("""
This dashboard provides a competitive analysis of AI startups based on their features, business models, and funding.
The data is collected from Crunchbase and Product Hunt.

**TL;DR:**  
- The AI startup landscape can be grouped into five main categories:
    - **Enterprise Solutions**: Well-funded, mature companies offering scalable products for large organizations.
    - **Analytics Platforms**: Startups specializing in data-driven services, forecasting, and business intelligence.
    - **FinTech Innovators**: Fast-growing companies applying AI to financial services and technology.
    - **Visual AI**: Specialists in computer vision, security, and retail automation.
    - **Language Tech**: Startups focused on NLP, generative AI, and content creation tools.
- **Defensibility**: Only a small subset of startups demonstrate high defensibility, typically those with proprietary technology, enterprise focus, or significant funding.
- **Market Saturation**: Most clusters are moderately to highly saturated, with the exception of some enterprise and visual AI niches that remain less crowded and may offer first-mover advantages.
- **Funding Distribution**: Funding is concentrated in enterprise and fintech clusters, while creative and language tech startups tend to be earlier stage.
- **Opportunities**: Investors seeking differentiated bets should look for high-defensibility startups in less saturated clusters, especially in enterprise and visual AI segments.
""")

# Define file paths
data_dir = os.path.join(project_dir, 'data')
processed_file = os.path.join(data_dir, 'ai_startups.csv')
clustered_file = os.path.join(data_dir, 'clustered_ai_startups.csv')

# Check if we need to run the analysis or load existing data
@st.cache_data
def load_or_process_data():
    if os.path.exists(clustered_file):
        df = pd.read_csv(clustered_file)
        return df
    elif os.path.exists(processed_file):
        clustering = StartupClustering(processed_file)
        clustering.run_full_analysis()
        return pd.read_csv(clustered_file)
    else:
        st.error("No data available. Please run the scrapers and data processing scripts first.")
        return None

# Load data
df = load_or_process_data()

if df is not None:
    # Sidebar for filters
    st.sidebar.header("Filters")
    
    # Filter by cluster if available
    if 'cluster_name' in df.columns:
        clusters = sorted(df['cluster_name'].unique())
        selected_clusters = st.sidebar.multiselect(
            "Select AI Categories",
            options=clusters,
            default=clusters
        )
    else:
        clusters = sorted(df['cluster'].unique())
        selected_clusters = st.sidebar.multiselect(
            "Select Clusters",
            options=clusters,
            default=clusters
        )
    
    # Filter by defensibility
    if 'defensibility' in df.columns:
        defensibility_options = sorted(df['defensibility'].unique())
        selected_defensibility = st.sidebar.multiselect(
            "Filter by Defensibility",
            options=defensibility_options,
            default=defensibility_options
        )
    else:
        selected_defensibility = None
    
    # Filter by saturation
    if 'saturation' in df.columns:
        saturation_options = sorted(df['saturation'].unique())
        selected_saturation = st.sidebar.multiselect(
            "Filter by Market Saturation",
            options=saturation_options,
            default=saturation_options
        )
    else:
        selected_saturation = None
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_clusters:
        if 'cluster_name' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['cluster_name'].isin(selected_clusters)]
        else:
            filtered_df = filtered_df[filtered_df['cluster'].isin(selected_clusters)]
    
    if selected_defensibility:
        filtered_df = filtered_df[filtered_df['defensibility'].isin(selected_defensibility)]
    
    if selected_saturation:
        filtered_df = filtered_df[filtered_df['saturation'].isin(selected_saturation)]
    
    # Display the number of startups after filtering
    st.sidebar.markdown(f"**{len(filtered_df)} startups** match the filters")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Positioning Map", "Defensibility Analysis", "Market Saturation", "Data Table"])
    
    with tab1:
        st.header("AI Startup Positioning Map")
        st.markdown(
            "This map visualizes the competitive landscape of AI startups, grouping them by similarity in features and business models. "
            "Clusters represent distinct market segments, and proximity indicates how closely startups compete."
        )
        
        # Check if we have the PCA coordinates from clustering
        if 'pca_x' in filtered_df.columns and 'pca_y' in filtered_df.columns:
            # Create the scatter plot
            color_column = "cluster_name" if "cluster_name" in filtered_df.columns else "cluster"
            # Custom hover template for easy reading
            fig = px.scatter(
                filtered_df,
                x="pca_x",
                y="pca_y",
                color=color_column,
                size="funding_amount",
                hover_name="company_name",
                hover_data={
                    "industry_focus": True,
                    "location": True,
                    "funding_amount": ":,",
                    "employee_count": True,
                    "defensibility": True,
                    "saturation": True,
                    "pca_x": False,
                    "pca_y": False,
                    "cluster_name": False,
                    "cluster": False
                },
                color_discrete_sequence=px.colors.qualitative.G10,
                title="Startup Clustering - PCA Projection",
                height=700
            )
            fig.update_traces(
                hovertemplate=
                "<b>%{hovertext}</b><br>" +
                "What do they do? %{customdata[0]}<br>" +
                "Where? %{customdata[1]}<br>" +
                "Money raised: $%{customdata[2]:,}<br>" +
                "Team size: %{customdata[3]} people<br>" +
                "Defensibility: %{customdata[4]}<br>" +
                "Market: %{customdata[5]}<br>" +
                "<extra></extra>"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **How to read this chart:**
            - Each point represents an AI startup
            - Colors indicate different clusters/segments
            - Size indicates funding amount (when available)
            - Proximity represents similarity in features and business model
            """)
        else:
            st.warning("Positioning map requires PCA coordinates from clustering analysis. Run the clustering analysis first.")
    
    with tab2:
        st.header("Defensibility Analysis")
        st.markdown(
            "This chart highlights which AI startups have the strongest competitive moats, based on factors like funding, technology, and business model. "
            "Higher defensibility scores suggest a greater ability to withstand competition and maintain market position."
        )
        
        if 'defensibility_score' in filtered_df.columns:
            # Create two columns
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Sort by defensibility score
                defensibility_df = filtered_df.sort_values('defensibility_score', ascending=False).head(20)
                
                # Create bar chart
                fig = px.bar(
                    defensibility_df,
                    x="defensibility_score",
                    y="company_name",
                    color="defensibility",
                    title="Defensibility Score by Startup",
                    height=600,
                    hover_data={
                        "defensibility_score": ":.2f"  # Format score with 2 decimal places
                    }
                )
                # Update hover template - removed the category line
                fig.update_traces(
                    hovertemplate=
                    "<b>%{y}</b><br>" +
                    "Defensibility Score: %{x:.2f}<br>" +
                    "<extra></extra>"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Create pie chart of defensibility categories
                fig = px.pie(
                    filtered_df,
                    names='defensibility',
                    title="Defensibility Distribution",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("""
                **About Defensibility Score:**
                
                The defensibility score evaluates how protected a startup's business model is from competitors.
                
                Factors considered:
                - Funding level
                - Enterprise focus
                - Proprietary technology
                - Network effects
                - Switching costs
                """)
        else:
            st.warning("Defensibility analysis not available. Run the clustering analysis first.")
    
    with tab3:
        st.header("Market Saturation Analysis")
        st.markdown(
            "This section shows how crowded each AI segment is, combining the number of competitors and their similarity. "
            "Highly saturated clusters may face intense competition, while low saturation indicates potential opportunities."
        )
        
        if 'saturation_score' in filtered_df.columns and ('cluster' in filtered_df.columns or 'cluster_name' in filtered_df.columns):
            # Create two columns
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Calculate average saturation by cluster
                group_col = 'cluster_name' if 'cluster_name' in filtered_df.columns else 'cluster'
                cluster_saturation = filtered_df.groupby(group_col)['saturation_score'].mean().reset_index()
                cluster_saturation['cluster_size'] = filtered_df.groupby(group_col).size().values
                
                # Create bar chart
                fig = px.bar(
                    cluster_saturation,
                    x=group_col,
                    y='saturation_score',
                    color='saturation_score',
                    color_continuous_scale='Reds',
                    title="Market Saturation by AI Category",
                    height=500,
                    text='cluster_size',
                    hover_data={
                        group_col: True,
                        "saturation_score": ":.2f",
                        "cluster_size": True
                    }
                )
                fig.update_traces(
                    hovertemplate=
                    "<b>%{x}</b><br>" +
                    "Saturation Score: %{y:.2f}<br>" +
                    "Number of Startups: %{text}<br>" +
                    "<extra></extra>"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Create heatmap showing relationship between defensibility and saturation
                if 'defensibility' in filtered_df.columns and 'saturation' in filtered_df.columns:
                    heatmap_data = pd.crosstab(filtered_df['defensibility'], filtered_df['saturation'])
                    
                    fig = px.imshow(
                        heatmap_data,
                        title="Defensibility vs Saturation",
                        height=400,
                        color_continuous_scale='Blues',
                        text_auto=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("""
                **About Market Saturation:**
                
                Market saturation indicates how crowded a particular segment is.
                
                High saturation suggests:
                - Many competitors with similar features
                - Potential price pressure
                - Need for stronger differentiation
                
                Low saturation may indicate:
                - Emerging opportunities
                - Niche markets
                - Potential for first-mover advantage
                """)
        else:
            st.warning("Market saturation analysis not available. Run the clustering analysis first.")
    
    with tab4:
        st.header("AI Startups Data Table")
        st.markdown(
            "This table provides a detailed view of the startups, including their cluster assignment, defensibility, and market saturation. "
            "Use it to explore individual companies and compare their competitive positioning."
        )

        # Prepare columns for display: show startup name, then funding, then others
        # Use friendly column names for display
        col_map = {
            "company_name": "Startup Name",
            "name": "Startup Name",
            "description": "Description",
            "funding_amount": "Funding Amount",
            "cluster_name": "Cluster",
            "defensibility": "Defensibility",
            "saturation": "Market Saturation"
        }
        # Build the list of columns to display in order
        display_cols = []
        # Prefer 'company_name', fallback to 'name'
        if 'company_name' in filtered_df.columns:
            display_cols.append('company_name')
        elif 'name' in filtered_df.columns:
            display_cols.append('name')
        # Add description if present
        if 'description' in filtered_df.columns:
            display_cols.append('description')
        # Funding
        if 'funding_amount' in filtered_df.columns:
            display_cols.append('funding_amount')
        # Cluster (prefer cluster_name)
        if 'cluster_name' in filtered_df.columns:
            display_cols.append('cluster_name')
        elif 'cluster' in filtered_df.columns:
            display_cols.append('cluster')
        # Defensibility
        if 'defensibility' in filtered_df.columns:
            display_cols.append('defensibility')
        # Saturation
        if 'saturation' in filtered_df.columns:
            display_cols.append('saturation')

        # Only keep columns that exist
        display_cols = [col for col in display_cols if col in filtered_df.columns]

        # Rename columns for display
        display_df = filtered_df[display_cols].rename(columns=col_map)

        st.dataframe(display_df, use_container_width=True)

        # Option to download the data (keep original column names for CSV)
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="ai_startups_analysis.csv",
            mime="text/csv"
        )

else:
    # Instructions for running the data collection and processing
    st.header("Data Collection Required")
    st.markdown("""
    No data is available yet. To populate this dashboard:
    
    1. Run the web scrapers:
    ```
    python scraper/crunchbase_scraper.py
    python scraper/producthunt_scraper.py
    ```
    
    2. Process the collected data:
    ```
    python analysis/data_processor.py
    ```
    
    3. Run the clustering analysis:
    ```
    python analysis/startup_clustering.py
    ```
    
    4. Refresh this dashboard to see the results.
    """)
