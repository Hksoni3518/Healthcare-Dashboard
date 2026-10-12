# Healthcare Intelligence Dashboard

A modern healthcare analytics dashboard built with Python and Streamlit. It brings together patient demographics, clinical conditions, admissions, and billing insights into a single interactive reporting interface.

## Overview

This project helps healthcare teams explore operational and clinical performance across multiple dimensions, including:

- Patient admission trends and demographics
- Medical condition distribution
- Age-group and gender analysis
- Insurance and billing summaries
- Revenue and average billing insights
- Date-based filtering for reporting periods

The dashboard is designed to provide a clean, presentation-ready view for healthcare administrators, analysts, and stakeholders.

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- HTML/CSS for custom dashboard styling

## Project Structure

```text
Healthcare project/
├── main.py                 # Streamlit app entry point
├── style.html             # Custom dark dashboard styling
├── Healthcare report.csv  # Healthcare dataset used for analytics
├── requirements.txt       # Python package dependencies
├── README.md              # Project documentation
└── myvenv/                # Local virtual environment (if present)
```

## Features

- Interactive sidebar filters for date range, medical condition, admission type, insurance provider, gender, and age group
- KPI cards for billing totals, admissions, average billing, and stay duration
- Patient intelligence charts for age distribution, gender mix, blood type information, and condition breakdown
- Financial intelligence charts for revenue by condition and billing performance
- Responsive design with a dark healthcare-themed interface

## Prerequisites

- Python 3.10 or newer
- pip package manager

## Installation

1. Open a terminal in the project folder.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the Application

From the project directory, start the dashboard with:

```bash
streamlit run main.py
```

Then open the local Streamlit URL shown in the terminal (typically http://localhost:8501).

## Data

The application reads the dataset file `Healthcare report.csv`. Ensure this file remains in the project root directory so the dashboard loads correctly.

## Notes

- The dashboard styling is loaded from `style.html` and applied using Streamlit markdown rendering.
- The app uses a date-driven filtering system to compare the current reporting period against the previous period.
- If you already have a local virtual environment such as `myvenv`, you may activate it instead of creating a new one.

## License

This project is provided for educational and demonstration purposes. Update the license terms to match your organization’s policy before production deployment.
