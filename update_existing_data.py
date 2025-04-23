import pandas as pd
import os
from pathlib import Path

def update_cluster_names():
    """
    Update existing clustered data with semantic cluster names
    """
    # Define paths
    data_dir = Path(__file__).parent / 'data'
    clustered_file = data_dir / 'clustered_ai_startups.csv'
    
    if not clustered_file.exists():
        print(f"Error: {clustered_file} not found.")
        return False
    
    print(f"Reading {clustered_file}...")
    df = pd.read_csv(clustered_file)
    
    if 'cluster' not in df.columns:
        print("Error: No 'cluster' column found in the data.")
        return False
    
    # Define semantic cluster names based on characteristics in the data
    cluster_mapping = {
        0: "Enterprise Solutions",  # High funding, manufacturing, larger companies
        1: "Analytics Platforms",   # Business services, forecasting, data products
        2: "FinTech Innovators",    # Finance, high growth rate, recommendation systems
        3: "Visual AI",             # Computer vision, retail, visual tech
        4: "Language Tech"          # NLP, generative AI, content creation
    }
    
    # Add semantic cluster names
    df['cluster_name'] = df['cluster'].map(cluster_mapping)
    
    # Save updated file
    print(f"Writing updated data to {clustered_file}...")
    df.to_csv(clustered_file, index=False)
    
    # Show examples from each cluster
    print("\nCluster examples:")
    for cluster_id, name in cluster_mapping.items():
        companies = df[df['cluster'] == cluster_id]['company_name'].tolist()[:3]
        industries = df[df['cluster'] == cluster_id]['industry_focus'].tolist()[:3]
        print(f"{name} examples: {', '.join(companies)}")
        print(f"  Industries: {', '.join(industries)}")
    
    print("\nUpdated cluster names successfully!")
    return True

if __name__ == "__main__":
    update_cluster_names()
