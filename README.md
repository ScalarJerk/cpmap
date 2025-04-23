# AI Startup Competition Analysis

A tool for analyzing AI startup trends and competitive landscape.

## Setup Instructions

### Prerequisites

This project requires:

1. Python 3.8 or higher
2. Microsoft Visual C++ 14.0 or higher (required for scikit-learn)
   - You can download this from [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Install the "Desktop development with C++" workload

### Installation

Run the setup script:
```
setup.bat
```
   
Follow the prompts to install any required dependencies. When asked if you want to run the application, select 'y' to run it immediately or 'n' to set up the environment only.

## Running the Project

After setup, you can run the project with:

```
python run.py --all
```

Or run specific components:

- Scrape data only: `python run.py --scrape`
- Run analysis only: `python run.py --analyze`
- Launch dashboard only: `python run.py --dashboard`

## Viewing the Dashboard

The dashboard will be available at: http://localhost:8501
