import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

class DataProcessor:
    def __init__(self, data_dir=None):
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        else:
            self.data_dir = data_dir
        self.startups_data = None
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
    
    def load_data(self, crunchbase_file="ai_startups_data.csv", producthunt_file="ai_producthunt_data.csv", linkedin_file="ai_linkedin_data.csv"):
        """
        Load data from CSV files and merge it
        """
        crunchbase_path = os.path.join(self.data_dir, crunchbase_file)
        producthunt_path = os.path.join(self.data_dir, producthunt_file)
        linkedin_path = os.path.join(self.data_dir, linkedin_file)
        
        # Check if files exist
        crunchbase_exists = os.path.exists(crunchbase_path)
        producthunt_exists = os.path.exists(producthunt_path)
        linkedin_exists = os.path.exists(linkedin_path)
        
        if not (crunchbase_exists or producthunt_exists or linkedin_exists):
            raise FileNotFoundError("No data files found. Please run scrapers first.")
        
        # Load data from available files
        dfs = []
        
        if crunchbase_exists:
            crunchbase_df = pd.read_csv(crunchbase_path)
            crunchbase_df['source'] = 'Crunchbase'
            dfs.append(crunchbase_df)
            print(f"Loaded {len(crunchbase_df)} startups from Crunchbase")
        
        if producthunt_exists:
            producthunt_df = pd.read_csv(producthunt_path)
            producthunt_df['source'] = 'ProductHunt'
            dfs.append(producthunt_df)
            print(f"Loaded {len(producthunt_df)} products from ProductHunt")
            
        if linkedin_exists:
            linkedin_df = pd.read_csv(linkedin_path)
            linkedin_df['source'] = 'LinkedIn'
            dfs.append(linkedin_df)
            print(f"Loaded {len(linkedin_df)} companies from LinkedIn")
        
        # Merge dataframes if we have multiple sources
        if len(dfs) > 1:
            # Try to merge on name or website if available
            self.startups_data = pd.concat(dfs, ignore_index=True)
            
            # More sophisticated deduplication
            if 'website' in self.startups_data.columns:
                # First clean website URLs for better matching
                self.startups_data['website_clean'] = self.startups_data['website'].str.replace(r'^https?://(www\.)?', '', regex=True).str.lower()
                self.startups_data['website_clean'] = self.startups_data['website_clean'].str.rstrip('/')
                
                # Group by website and keep first row with most information
                website_groups = self.startups_data.groupby('website_clean')
                merged_data = []
                
                for _, group in website_groups:
                    if len(group) == 1:
                        merged_data.append(group.iloc[0])
                    else:
                        # Merge information from multiple sources
                        merged_row = {}
                        for col in group.columns:
                            non_null_values = group[col].dropna()
                            if len(non_null_values) > 0:
                                merged_row[col] = non_null_values.iloc[0]
                        merged_data.append(pd.Series(merged_row))
                
                self.startups_data = pd.DataFrame(merged_data)
            else:
                # If no website, deduplicate based on name
                self.startups_data = self.startups_data.drop_duplicates(subset=['name'], keep='first')
        else:
            self.startups_data = dfs[0]
        
        print(f"Loaded {len(self.startups_data)} unique AI startups/products")
        return self.startups_data
    
    def clean_funding_data(self):
        """
        Extract and normalize funding amounts
        """
        if 'funding' not in self.startups_data.columns:
            self.startups_data['funding_amount'] = np.nan
            return
            
        def extract_funding(funding_str):
            if pd.isna(funding_str) or funding_str == 'N/A':
                return np.nan
            
            # Extract numeric value
            amount = re.search(r'(\d+(\.\d+)?)', funding_str)
            if not amount:
                return np.nan
                
            amount = float(amount.group(1))
            
            # Convert to millions
            if 'B' in funding_str:
                amount *= 1000
            elif 'M' in funding_str:
                amount *= 1
            elif 'K' in funding_str:
                amount *= 0.001
                
            return amount
        
        self.startups_data['funding_amount'] = self.startups_data['funding'].apply(extract_funding)
        print("Processed funding data")
    
    def extract_features(self):
        """
        Extract features from company descriptions for analysis
        """
        # Extract AI-related features from descriptions
        ai_features = ['AI', 'ML', 'machine learning', 'neural', 'NLP', 'computer vision',
                      'chatbot', 'language model', 'LLM', 'GPT', 'generative', 'transformer',
                      'deep learning', 'artificial intelligence', 'automation', 'robot', 'cognitive',
                      'predictive', 'analytics', 'big data']
        
        for feature in ai_features:
            feature_col = f'has_{feature.lower().replace(" ", "_")}'
            self.startups_data[feature_col] = self.startups_data['description'].str.contains(
                feature, case=False).astype(int)
        
        # Extract business model indicators
        biz_models = ['B2B', 'B2C', 'SaaS', 'API', 'open-source', 'subscription', 
                     'freemium', 'enterprise', 'marketplace', 'platform', 'infrastructure',
                     'consulting', 'on-premise', 'cloud']
        
        for model in biz_models:
            model_col = f'is_{model.lower()}'
            # Check in description and categories if available
            if 'categories' in self.startups_data.columns:
                self.startups_data[model_col] = (
                    self.startups_data['description'].str.contains(model, case=False) | 
                    self.startups_data['categories'].str.contains(model, case=False, na=False)
                ).astype(int)
            else:
                self.startups_data[model_col] = self.startups_data['description'].str.contains(
                    model, case=False).astype(int)
        
        # Extract GTM motion indicators
        gtm_models = ['product-led', 'sales-led', 'marketing-led', 'community', 
                     'viral', 'content marketing', 'partner', 'channel', 'direct sales']
        
        for gtm in gtm_models:
            gtm_col = f'gtm_{gtm.lower().replace("-", "_").replace(" ", "_")}'
            self.startups_data[gtm_col] = self.startups_data['description'].str.contains(
                gtm, case=False).astype(int)
        
        # Extract common use cases
        use_cases = ['content generation', 'code', 'data analysis', 'automation', 'customer service',
                    'personalization', 'recommendation', 'security', 'healthcare', 'finance',
                    'marketing', 'sales', 'hr', 'legal', 'education']
        
        for case in use_cases:
            case_col = f'use_{case.lower().replace(" ", "_")}'
            self.startups_data[case_col] = self.startups_data['description'].str.contains(
                case, case=False).astype(int)
        
        print("Extracted features from text data")
        
        # Extract keywords using NLP for better categorization
        self.extract_keywords()
        
        return self.startups_data
    
    def extract_keywords(self):
        """
        Extract key terms from descriptions using NLP techniques
        """
        if 'description' not in self.startups_data.columns:
            return
            
        # Prepare stop words
        stop_words = set(stopwords.words('english'))
        
        # Extract top keywords for each startup
        def get_keywords(text, top_n=5):
            if pd.isna(text):
                return []
            
            tokens = word_tokenize(text.lower())
            words = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 2]
            common_words = Counter(words).most_common(top_n)
            return [word for word, _ in common_words]
        
        # Apply keyword extraction
        self.startups_data['keywords'] = self.startups_data['description'].apply(get_keywords)
        
        # Count common keywords across all startups
        all_keywords = []
        for kw_list in self.startups_data['keywords']:
            all_keywords.extend(kw_list)
        
        top_keywords = Counter(all_keywords).most_common(20)
        
        # Add top keywords as features
        for keyword, _ in top_keywords:
            keyword_col = f'kw_{keyword}'
            self.startups_data[keyword_col] = self.startups_data['keywords'].apply(
                lambda x: 1 if keyword in x else 0)
        
        print(f"Extracted top {len(top_keywords)} keywords as features")
    
    def analyze_pricing(self):
        """
        Analyze pricing models when available
        """
        if 'pricing' not in self.startups_data.columns:
            return
            
        # Check for common pricing models
        price_patterns = {
            'has_free_tier': r'Free|free',
            'has_enterprise': r'Enterprise|enterprise|Contact|contact',
            'has_startup_plan': r'Startup|startup|Small business',
            'has_subscription': r'Subscription|subscription|monthly|yearly|annual',
            'has_usage_based': r'Usage|usage|Pay as you|consumption|credits',
            'has_tiered': r'Basic|Pro|Premium|Standard|Plus|Advanced',
            'has_freemium': r'Freemium|freemium|Free.*Premium|free.*paid'
        }
        
        for col, pattern in price_patterns.items():
            self.startups_data[col] = self.startups_data['pricing'].str.contains(
                pattern, na=False).astype(int)
                
        # Extract price points when available
        def extract_price_points(pricing_str):
            if pd.isna(pricing_str):
                return np.nan
                
            price_matches = re.findall(r'\$(\d+(?:\.\d+)?)', pricing_str)
            if price_matches:
                # Return minimum and maximum price points
                prices = [float(p) for p in price_matches]
                return {
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'price_points': len(prices)
                }
            return None
            
        price_data = self.startups_data['pricing'].apply(extract_price_points)
        
        # Add price columns to data
        self.startups_data['min_price'] = price_data.apply(
            lambda x: x['min_price'] if isinstance(x, dict) and 'min_price' in x else np.nan)
        self.startups_data['max_price'] = price_data.apply(
            lambda x: x['max_price'] if isinstance(x, dict) and 'max_price' in x else np.nan)
        self.startups_data['price_tiers'] = price_data.apply(
            lambda x: x['price_points'] if isinstance(x, dict) and 'price_points' in x else np.nan)
            
        print("Analyzed pricing models and extracted price points")
    
    def categorize_company_size(self):
        """
        Categorize companies by size based on employee count
        """
        if 'company_size' not in self.startups_data.columns:
            return
            
        def extract_size_category(size_str):
            if pd.isna(size_str) or size_str == 'N/A':
                return "Unknown"
                
            # Extract numeric values
            numbers = re.findall(r'\d+', str(size_str))
            if not numbers:
                return "Unknown"
                
            # Use maximum number as employee count
            employees = max([int(n) for n in numbers])
            
            # Categorize
            if employees < 10:
                return "Micro (1-9)"
            elif employees < 50:
                return "Small (10-49)"
            elif employees < 250:
                return "Medium (50-249)"
            else:
                return "Large (250+)"
                
        self.startups_data['size_category'] = self.startups_data['company_size'].apply(extract_size_category)
        
        # Create dummy variables for size categories
        size_dummies = pd.get_dummies(self.startups_data['size_category'], prefix='size')
        self.startups_data = pd.concat([self.startups_data, size_dummies], axis=1)
        
        print("Categorized companies by size")

    def process_data(self):
        """
        Run all processing steps
        """
        self.clean_funding_data()
        self.extract_features()
        self.analyze_pricing()
        self.categorize_company_size()
        
        # Create GTM motion category
        gtm_columns = [col for col in self.startups_data.columns if col.startswith('gtm_')]
        if gtm_columns:
            self.startups_data['gtm_motion'] = self.startups_data[gtm_columns].idxmax(axis=1)
            self.startups_data['gtm_motion'] = self.startups_data['gtm_motion'].str.replace('gtm_', '')
        
        # Create use case category
        use_case_columns = [col for col in self.startups_data.columns if col.startswith('use_')]
        if use_case_columns:
            self.startups_data['primary_use_case'] = self.startups_data[use_case_columns].idxmax(axis=1)
            self.startups_data['primary_use_case'] = self.startups_data['primary_use_case'].str.replace('use_', '')
        
        # Create business model category
        biz_model_columns = [col for col in self.startups_data.columns if col.startswith('is_')]
        if biz_model_columns:
            self.startups_data['business_model'] = self.startups_data[biz_model_columns].idxmax(axis=1)
            self.startups_data['business_model'] = self.startups_data['business_model'].str.replace('is_', '')
        
        return self.startups_data
    
    def save_processed_data(self, filename="ai_startups.csv"):
        """
        Save processed data to CSV
        """
        if self.startups_data is None:
            print("No data to save")
            return
            
        output_path = os.path.join(self.data_dir, filename)
        self.startups_data.to_csv(output_path, index=False)
        print(f"Processed data saved to {output_path}")
        return output_path

if __name__ == "__main__":
    processor = DataProcessor()
    processor.load_data()
    processor.process_data()
    processor.save_processed_data()
