# AI Startup Competition Analysis

A tool for analyzing AI startup trends and competitive landscape.

## Simplified Setup & Usage

This project uses a single script that handles both setup and running the application:

```
python run.py [options]
```

When you run this command:
1. A virtual environment will be automatically created if it doesn't exist
2. Required dependencies will be installed
3. The application will run based on the options you provide

### Options

- No options: Runs the complete pipeline (default)
- `--setup`: Only sets up the virtual environment and installs dependencies
- `--scrape`: Run only the web scrapers to collect data
- `--process`: Process the collected data
- `--analyze`: Run the clustering analysis
- `--dashboard`: Launch the dashboard
- `--all`: Run the complete pipeline

Examples:
```
# Set up dependencies only
python run.py --setup

# Run everything
python run.py

# Just launch the dashboard
python run.py --dashboard
```

## Prerequisites

This project requires:

1. Python 3.8 or higher
2. Microsoft Visual C++ 14.0 or higher (required for scikit-learn)
   - You can download this from [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Install the "Desktop development with C++" workload

## Viewing the Dashboard

The dashboard will be available at: http://localhost:8501
