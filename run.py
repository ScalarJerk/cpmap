import os
import sys
import argparse
import subprocess
import platform
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = ['requests', 'pandas', 'streamlit', 'scikit-learn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("\n⚠️ Missing dependencies detected: " + ", ".join(missing_packages))
        install = input("Do you want to install them now? (y/n): ")
        if install.lower() == 'y':
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencies installed successfully!")
        else:
            print("⚠️ Some features may not work without required dependencies.")
            return False
    return True

def get_python_executable():
    """Get the path to the Python executable in the virtual environment"""
    project_dir = Path(__file__).parent
    venv_dir = project_dir / "venv"
    
    if not venv_dir.exists():
        print("Virtual environment not found. Please run setup_venv.py first.")
        sys.exit(1)
    
    if platform.system() == "Windows":
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        python_path = venv_dir / "bin" / "python"
    
    if not python_path.exists():
        print(f"Python executable not found at {python_path}")
        print("Please run setup_venv.py to create the virtual environment.")
        sys.exit(1)
    
    return str(python_path)

def run_script(script_path, description):
    """Run a Python script and display its output"""
    # Get the Python executable from the virtual environment
    python_executable = get_python_executable()
    
    print(f"\n{'='*80}\n{description}\n{'='*80}")
    try:
        result = subprocess.run([python_executable, script_path], check=True)
        if result.returncode == 0:
            print(f"\n✅ {description} completed successfully")
            return True
        else:
            print(f"\n❌ {description} failed with exit code {result.returncode}")
            return False
    except Exception as e:
        print(f"\n❌ {description} failed: {str(e)}")
        return False

def main():
    # Define the project directory
    project_dir = Path(__file__).parent
    
    parser = argparse.ArgumentParser(description="Run the AI Startup Competitive Positioning Map pipeline")
    parser.add_argument("--scrape", action="store_true", help="Run the web scrapers")
    parser.add_argument("--process", action="store_true", help="Process the collected data")
    parser.add_argument("--analyze", action="store_true", help="Run the clustering analysis")
    parser.add_argument("--dashboard", action="store_true", help="Launch the dashboard")
    parser.add_argument("--all", action="store_true", help="Run the complete pipeline")
    
    args = parser.parse_args()
    
    # If no options specified, show help
    if not (args.scrape or args.process or args.analyze or args.dashboard or args.all):
        parser.print_help()
        return
    
    # Check dependencies before running any scripts
    if not check_dependencies():
        return
    
    # Run the requested steps
    steps_success = []
    
    if args.scrape or args.all:
        # Run the web scrapers
        crunchbase_success = run_script(
            os.path.join(project_dir, "scraper", "crunchbase_scraper.py"),
            "Scraping AI startups from Crunchbase"
        )
        producthunt_success = run_script(
            os.path.join(project_dir, "scraper", "producthunt_scraper.py"),
            "Scraping AI products from Product Hunt"
        )
        steps_success.append(crunchbase_success or producthunt_success)
    
    if args.process or args.all:
        # Process the collected data
        process_success = run_script(
            os.path.join(project_dir, "analysis", "data_processor.py"),
            "Processing AI startup data"
        )
        steps_success.append(process_success)
    
    if args.analyze or args.all:
        # Run the clustering analysis
        analyze_success = run_script(
            os.path.join(project_dir, "analysis", "startup_clustering.py"),
            "Running clustering analysis"
        )
        steps_success.append(analyze_success)
    
    if args.dashboard or args.all:
        # Launch the dashboard
        dashboard_path = os.path.join(project_dir, "dashboard", "app.py")
        python_executable = get_python_executable()
        print(f"\n{'='*80}\nLaunching Streamlit Dashboard\n{'='*80}")
        print(f"Starting dashboard at: {dashboard_path}")
        print("To view the dashboard, open your browser at http://localhost:8501")
        print("Press Ctrl+C to stop the dashboard")
        try:
            subprocess.run([python_executable, "-m", "streamlit", "run", dashboard_path], check=True)
        except KeyboardInterrupt:
            print("\nDashboard stopped")
        except Exception as e:
            print(f"\n❌ Error launching dashboard: {str(e)}")
            steps_success.append(False)
    
    # Summary
    if steps_success and all(steps_success):
        print("\n✅ All requested steps completed successfully!")
    elif steps_success:
        print("\n⚠️ Some steps failed. Check the output above for details.")
    
    if args.all:
        print("\nTo view the dashboard again, run: python run.py --dashboard")

if __name__ == "__main__":
    main()
