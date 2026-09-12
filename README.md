# Netflix Movie Analysis
https://netflix-movie-analysis-app.streamlit.app

Interactive Streamlit dashboard for exploring movie popularity, audience ratings, genres, and release-year patterns.

## Architecture

```mermaid
flowchart TD
    A[Streamlit app.py] --> B[mymoviedb (1).csv]
    B --> C[Parse dates and numeric fields]
    C --> D[Create release year]
    C --> E[Create rating categories]
    C --> F[Split and explode genres]
    D --> G[Sidebar filters]
    E --> G
    F --> G
    G --> H[Filtered movie dataset]
    H --> I[KPIs]
    H --> J[Release-year trend]
    H --> K[Rating distribution]
    H --> L[Genre distribution]
    H --> M[Popularity and genre tables]
    H --> N[Filtered CSV download]
```

## Project Structure

```text
Netflix Data Analysis Project/
|-- app.py                         # Streamlit dashboard
|-- mymoviedb (1).csv             # Movie metadata dataset
|-- movie data analysis.ipynb     # Original exploratory analysis
|-- netflix_movie_analysis_questions.pdf
`-- README.md                      # Architecture and setup documentation
```

## Data Flow

1. `app.py` loads the nearby CSV using a path relative to the application file.
2. The CSV is parsed with Pandas' Python engine because the source contains long movie descriptions.
3. `Release_Date` is converted to a datetime value and used to create `Release Year`.
4. `Vote_Average`, `Popularity`, and `Vote_Count` are converted to numeric values.
5. Ratings are grouped into four categories:
   - `not_popular`
   - `below_avg`
   - `average`
   - `popular`
6. Comma-separated genres are split into lists and exploded for genre-level aggregation.
7. Sidebar selections filter the dataset before all KPIs and charts are calculated.

## Dashboard Features

- Release-year range filter
- Rating-category filter
- Genre filter
- Minimum vote-count filter
- Movie count and average rating KPIs
- Average popularity and most popular movie KPI
- Movies released by year
- Audience rating-category distribution
- Genre distribution
- Popularity leaders table
- Genre performance table
- Filtered movie catalogue preview
- Downloadable filtered CSV

## Original Analysis

The accompanying notebook performs descriptive exploratory analysis, including:

- Most frequent genre
- Genre with the highest vote count
- Most and least popular movies
- Year with the most movies
- Genre and rating-category visualizations

There is no forecasting, classification, or machine-learning model in this project.

## Run Locally

From the project repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install streamlit pandas seaborn matplotlib
python -m streamlit run "Netflix Data Analysis Project\app.py"
```

The dashboard opens at `http://localhost:8501` unless that port is already in use.

## Deployment

For Streamlit deployment, use `app.py` as the main file and keep `mymoviedb (1).csv` in the same directory. The application does not require external APIs or credentials.
