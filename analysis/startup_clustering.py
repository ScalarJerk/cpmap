import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class StartupClustering:
    def __init__(self, data_path=None):
        if data_path is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            self.data_path = os.path.join(data_dir, 'ai_startups.csv')
        else:
            self.data_path = data_path
            
        self.data = None
        self.feature_cols = None
        self.cluster_labels = None
        self.pca = None
        self.pca_features = None
    
    def load_data(self):
        """
        Load processed data
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Processed data file not found at {self.data_path}")
        
        self.data = pd.read_csv(self.data_path)
        print(f"Loaded data with {len(self.data)} startups")
        return self.data
    
    def prepare_features(self):
        """
        Prepare features for clustering
        """
        # Select numeric and boolean columns for clustering
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Filter out id columns or other non-feature columns
        exclude_cols = ['Unnamed: 0']
        self.feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        # Fill missing values
        self.data[self.feature_cols] = self.data[self.feature_cols].fillna(0)
        
        print(f"Selected {len(self.feature_cols)} features for clustering")
        return self.feature_cols
    
    def apply_clustering(self, method='kmeans', n_clusters=5):
        """
        Apply clustering to the data
        """
        if self.feature_cols is None:
            self.prepare_features()
            
        # Normalize data
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(self.data[self.feature_cols])
        
        # Apply clustering
        if method == 'kmeans':
            clustering = KMeans(n_clusters=n_clusters, random_state=42)
        elif method == 'hierarchical':
            clustering = AgglomerativeClustering(n_clusters=n_clusters)
        else:
            raise ValueError("Method must be 'kmeans' or 'hierarchical'")
            
        self.cluster_labels = clustering.fit_predict(scaled_features)
        self.data['cluster'] = self.cluster_labels
        
        # Map numeric clusters to semantic names based on their characteristics
        cluster_mapping = {
            0: "Enterprise Solutions",
            1: "Analytics Platforms", 
            2: "FinTech Innovators",
            3: "Visual AI",
            4: "Language Tech"
        }
        
        # Add semantic cluster names
        self.data['cluster_name'] = self.data['cluster'].map(cluster_mapping)
        
        print(f"Applied {method} clustering with {n_clusters} clusters")
        
        # Apply PCA for visualization
        self.pca = PCA(n_components=2)
        self.pca_features = self.pca.fit_transform(scaled_features)
        self.data['pca_x'] = self.pca_features[:, 0]
        self.data['pca_y'] = self.pca_features[:, 1]
        
        return self.data
    
    def analyze_clusters(self):
        """
        Analyze clusters to identify patterns
        """
        if 'cluster' not in self.data.columns:
            raise ValueError("Apply clustering first")
            
        cluster_analysis = {}
        
        # Define semantic cluster names based on analysis
        cluster_names = {
            0: "Enterprise Solutions",
            1: "Analytics Platforms",
            2: "FinTech Innovators",
            3: "Visual AI",
            4: "Language Tech"
        }
        
        # Map numeric clusters to semantic names
        self.data['cluster_name'] = self.data['cluster'].map(cluster_names)
        
        # Analyze feature distribution within clusters
        for cluster in sorted(self.data['cluster'].unique()):
            cluster_data = self.data[self.data['cluster'] == cluster]
            
            # Calculate average feature values for this cluster
            feature_means = cluster_data[self.feature_cols].mean()
            
            # Find top features for this cluster
            top_features = feature_means.sort_values(ascending=False).head(5)
            
            # Get company names in this cluster
            companies = cluster_data['company_name'].tolist()
            
            cluster_analysis[cluster] = {
                'name': cluster_names.get(cluster, f"Cluster {cluster}"),
                'size': len(cluster_data),
                'top_features': top_features.to_dict(),
                'companies': companies
            }
            
            # Try to determine cluster theme based on dominant features
            if 'funding_amount' in feature_means and feature_means['funding_amount'] > 0.7:
                cluster_analysis[cluster]['theme'] = 'Well-funded startups'
            elif 'is_b2b' in feature_means and feature_means['is_b2b'] > 0.7:
                cluster_analysis[cluster]['theme'] = 'B2B focused'
            elif 'is_saas' in feature_means and feature_means['is_saas'] > 0.7:
                cluster_analysis[cluster]['theme'] = 'SaaS products'
            elif 'has_gpt' in feature_means and feature_means['has_gpt'] > 0.5:
                cluster_analysis[cluster]['theme'] = 'GPT/LLM focused'
            else:
                # Find most distinctive feature
                distinctive = feature_means.idxmax()
                cluster_analysis[cluster]['theme'] = f"{distinctive} focused"
        
        return cluster_analysis
    
    def save_clustered_data(self, filename="clustered_ai_startups.csv"):
        """
        Save clustered data
        """
        if 'cluster' not in self.data.columns:
            raise ValueError("Apply clustering first")
            
        output_dir = os.path.dirname(self.data_path)
        output_path = os.path.join(output_dir, filename)
        
        self.data.to_csv(output_path, index=False)
        print(f"Clustered data saved to {output_path}")
        return output_path
    
    def evaluate_defensibility(self):
        """
        Add a defensibility score based on various factors
        """
        # Define weights for different factors that contribute to defensibility
        factors = {
            'funding_amount': 0.3,                # Well-funded companies can build moats
            'has_neural': 0.1,                   # Advanced AI tech can be hard to replicate
            'has_language_model': 0.15,          # Proprietary language models can be defensible
            'is_enterprise': 0.15,               # Enterprise relationships create stickiness
            'is_open_source': -0.1,              # Open source may have less defensibility
            'is_api': 0.1                        # API businesses can have network effects
        }
        
        # Initialize defensibility score
        self.data['defensibility_score'] = 0
        
        # Calculate defensibility based on available factors
        for factor, weight in factors.items():
            if factor in self.data.columns:
                # Normalize the factor if it's not binary
                if factor == 'funding_amount' and self.data[factor].max() > 0:
                    normalized = self.data[factor] / self.data[factor].max()
                    self.data['defensibility_score'] += normalized * weight
                else:
                    self.data['defensibility_score'] += self.data[factor] * weight
        
        # Scale to 0-100
        min_score = self.data['defensibility_score'].min()
        max_score = self.data['defensibility_score'].max()
        if max_score > min_score:
            self.data['defensibility_score'] = 100 * (self.data['defensibility_score'] - min_score) / (max_score - min_score)
        
        # Add a category
        conditions = [
            self.data['defensibility_score'] >= 70,
            self.data['defensibility_score'] >= 40,
            self.data['defensibility_score'] >= 0
        ]
        choices = ['High defensibility', 'Medium defensibility', 'Low defensibility']
        self.data['defensibility'] = np.select(conditions, choices, default='Unknown')
        
        print("Added defensibility analysis")
        
    def evaluate_saturation(self):
        """
        Evaluate market saturation based on cluster density and feature similarity
        """
        if 'cluster' not in self.data.columns:
            raise ValueError("Apply clustering first")
            
        # Calculate number of startups in each cluster
        cluster_sizes = self.data['cluster'].value_counts()
        
        # Calculate feature similarity within clusters
        cluster_density = {}
        for cluster in self.data['cluster'].unique():
            cluster_data = self.data[self.data['cluster'] == cluster]
            
            # Skip if only one startup in the cluster
            if len(cluster_data) <= 1:
                cluster_density[cluster] = 0
                continue
                
            # Calculate average pairwise similarity using PCA features
            cluster_points = cluster_data[['pca_x', 'pca_y']].values
            distances = []
            
            for i in range(len(cluster_points)):
                for j in range(i + 1, len(cluster_points)):
                    dist = np.linalg.norm(cluster_points[i] - cluster_points[j])
                    distances.append(dist)
            
            # Higher density = lower average distance
            if distances:
                cluster_density[cluster] = 1 / (np.mean(distances) + 0.01)  # Avoid division by zero
            else:
                cluster_density[cluster] = 0
        
        # Assign saturation level to each startup based on cluster
        for cluster in self.data['cluster'].unique():
            cluster_size = cluster_sizes[cluster]
            density = cluster_density[cluster]
            
            # Saturation is a function of cluster size and density
            saturation_score = (cluster_size / len(self.data) * 50) + (density / max(cluster_density.values()) * 50)
            
            # Assign to startups in this cluster
            self.data.loc[self.data['cluster'] == cluster, 'saturation_score'] = saturation_score
        
        # Categorize saturation
        conditions = [
            self.data['saturation_score'] >= 70,
            self.data['saturation_score'] >= 40,
            self.data['saturation_score'] >= 0
        ]
        choices = ['Highly saturated', 'Moderately saturated', 'Low saturation']
        self.data['saturation'] = np.select(conditions, choices, default='Unknown')
        
        print("Added market saturation analysis")

    def run_full_analysis(self, n_clusters=5):
        """
        Run the complete clustering analysis workflow
        """
        self.load_data()
        self.prepare_features()
        self.apply_clustering(n_clusters=n_clusters)
        self.evaluate_defensibility()
        self.evaluate_saturation()
        self.save_clustered_data()
        return self.analyze_clusters()

if __name__ == "__main__":
    clustering = StartupClustering()
    analysis = clustering.run_full_analysis(n_clusters=5)
    print("Cluster analysis:")
    for cluster, details in analysis.items():
        cluster_name = details.get('theme', f"Cluster {cluster}")
        if 'name' in details:
            cluster_name = details['name']
        print(f"{cluster_name} ({details['size']} startups)")
        print(f"  Top features: {list(details['top_features'].keys())[:3]}")
        print(f"  Example companies: {details['companies'][:3]}")
        print()
