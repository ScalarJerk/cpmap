import pandas as pd
import os
from pathlib import Path

def update_cluster_names():
    """
    Update the clustered_ai_startups.csv file with semantic cluster names
    """
    # Define file paths
    data_dir = Path(__file__).parent / 'data'
    clustered_file = data_dir / 'clustered_ai_startups.csv'
    
    if not clustered_file.exists():
        print(f"Error: {clustered_file} not found.")
        return False
    
    # Read the clustered data
    print(f"Reading {clustered_file}...")
    df = pd.read_csv(clustered_file)
    
    if 'cluster' not in df.columns:
        print("Error: No 'cluster' column found in the data.")
        return False
    
    # Define semantic cluster names based on analysis of the data
    cluster_names = {
        0: "Enterprise-Ready Solutions",
        1: "Data-Driven Services", 
        2: "Financial Tech Innovators",
        3: "Visual Recognition Specialists",
        4: "Creative AI Tools"
    }
    
    # Add semantic cluster names
    df['cluster_name'] = df['cluster'].map(cluster_names)
    
    # Save updated file
    print(f"Writing updated data to {clustered_file}...")
    df.to_csv(clustered_file, index=False)
    
    print("Successfully updated cluster names!")
    print("\nCluster meanings:")
    for cluster_id, name in cluster_names.items():
        companies = df[df['cluster'] == cluster_id]['company_name'].tolist()[:3]
        print(f"- Cluster {cluster_id}: {name}")
        print(f"  Example companies: {', '.join(companies)}")
    
    return True

if __name__ == "__main__":
    update_cluster_names()
