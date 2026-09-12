from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent / "mymoviedb (1).csv"
RATING_ORDER = ["not_popular", "below_avg", "average", "popular"]

st.set_page_config(
    page_title="Netflix Movie Analysis",
    page_icon="🎬",
    layout="wide",
)


@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH, engine="python")
    data["Release_Date"] = pd.to_datetime(data["Release_Date"], errors="coerce")
    data["Release Year"] = data["Release_Date"].dt.year
    data["Vote_Average"] = pd.to_numeric(data["Vote_Average"], errors="coerce")
    data["Popularity"] = pd.to_numeric(data["Popularity"], errors="coerce")
    data["Vote_Count"] = pd.to_numeric(data["Vote_Count"], errors="coerce")
    data["Rating Category"] = pd.cut(
        data["Vote_Average"],
        bins=[-float("inf"), 5, 6.5, 7.5, float("inf")],
        labels=RATING_ORDER,
    ).astype(str)
    data["Genre List"] = data["Genre"].fillna("Unknown").str.split(", ")
    data = data.dropna(subset=["Title", "Release_Date", "Popularity", "Vote_Average"])
    return data


def format_number(value):
    return f"{value:,.0f}"


data = load_data()

st.title("Netflix Movie Analysis")
st.caption("Explore movie popularity, audience ratings, genres, and release patterns.")

with st.sidebar:
    st.header("Filters")
    min_year = int(data["Release Year"].min())
    max_year = int(data["Release Year"].max())
    selected_years = st.slider("Release year", min_year, max_year, (min_year, max_year))
    rating_categories = st.multiselect(
        "Rating categories", RATING_ORDER, default=RATING_ORDER
    )
    genre_options = sorted(
        {genre for genres in data["Genre List"] for genre in genres if genre}
    )
    selected_genres = st.multiselect("Genres", genre_options)
    min_votes = st.number_input("Minimum vote count", min_value=0, value=0, step=100)

filtered = data[
    data["Release Year"].between(selected_years[0], selected_years[1])
    & data["Rating Category"].isin(rating_categories)
    & (data["Vote_Count"] >= min_votes)
].copy()

if selected_genres:
    filtered = filtered[
        filtered["Genre List"].apply(
            lambda genres: any(genre in genres for genre in selected_genres)
        )
    ]

if filtered.empty:
    st.warning("No movies match the selected filters.")
    st.stop()

movie_count = filtered["Title"].nunique()
average_rating = filtered["Vote_Average"].mean()
average_popularity = filtered["Popularity"].mean()
top_movie = filtered.loc[filtered["Popularity"].idxmax(), "Title"]

metric_columns = st.columns(4)
metric_columns[0].metric("Movies", format_number(movie_count))
metric_columns[1].metric("Average rating", f"{average_rating:.2f}/10")
metric_columns[2].metric("Average popularity", f"{average_popularity:,.1f}")
metric_columns[3].metric("Most popular movie", top_movie)

st.divider()

expanded_genres = filtered[["Title", "Popularity", "Vote_Count", "Genre List"]].explode(
    "Genre List"
)
genre_summary = (
    expanded_genres.groupby("Genre List", as_index=False)
    .agg(
        Movies=("Title", "nunique"),
        Votes=("Vote_Count", "sum"),
        Popularity=("Popularity", "mean"),
    )
    .sort_values("Movies", ascending=False)
)
year_summary = (
    filtered.groupby("Release Year", as_index=False)
    .agg(Movies=("Title", "nunique"), Popularity=("Popularity", "mean"))
    .sort_values("Release Year")
)
rating_summary = (
    filtered["Rating Category"]
    .value_counts()
    .reindex(RATING_ORDER, fill_value=0)
    .rename_axis("Rating Category")
    .reset_index(name="Movies")
)

trend_column, rating_column = st.columns(2)
with trend_column:
    st.subheader("Movies by Release Year")
    year_figure, year_axis = plt.subplots(figsize=(8, 4))
    year_axis.plot(
        year_summary["Release Year"],
        year_summary["Movies"],
        color="#e50914",
        marker="o",
        linewidth=2,
    )
    year_axis.set_xlabel("Release year")
    year_axis.set_ylabel("Number of movies")
    year_axis.grid(axis="y", alpha=0.25)
    st.pyplot(year_figure, use_container_width=True)
    plt.close(year_figure)

with rating_column:
    st.subheader("Audience Rating Categories")
    rating_figure, rating_axis = plt.subplots(figsize=(8, 4))
    sns.barplot(
        data=rating_summary,
        x="Rating Category",
        y="Movies",
        order=RATING_ORDER,
        color="#e50914",
        ax=rating_axis,
    )
    rating_axis.set_xlabel("")
    rating_axis.set_ylabel("Number of movies")
    rating_axis.tick_params(axis="x", rotation=20)
    rating_axis.grid(axis="y", alpha=0.25)
    st.pyplot(rating_figure, use_container_width=True)
    plt.close(rating_figure)

st.subheader("Genre Distribution")
genre_figure, genre_axis = plt.subplots(figsize=(12, 5))
top_genres = genre_summary.head(15).sort_values("Movies")
genre_axis.barh(top_genres["Genre List"], top_genres["Movies"], color="#b20710")
genre_axis.set_xlabel("Movies")
genre_axis.grid(axis="x", alpha=0.25)
st.pyplot(genre_figure, use_container_width=True)
plt.close(genre_figure)

leader_column, genre_metric_column = st.columns(2)
with leader_column:
    st.subheader("Popularity Leaders")
    leaders = filtered.nlargest(10, "Popularity")[
        ["Title", "Popularity", "Vote_Average", "Release Year"]
    ]
    st.dataframe(
        leaders.style.format({"Popularity": "{:,.1f}", "Vote_Average": "{:.1f}"}),
        use_container_width=True,
        hide_index=True,
    )

with genre_metric_column:
    st.subheader("Genre Performance")
    st.dataframe(
        genre_summary.head(10).style.format(
            {"Votes": "{:,.0f}", "Popularity": "{:,.1f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

with st.expander("Filtered movie catalogue"):
    catalogue_columns = [
        "Title",
        "Release_Date",
        "Genre",
        "Popularity",
        "Vote_Count",
        "Vote_Average",
        "Original_Language",
    ]
    st.download_button(
        "Download filtered CSV",
        filtered[catalogue_columns].to_csv(index=False).encode("utf-8"),
        "filtered_netflix_movies.csv",
        "text/csv",
    )
    st.dataframe(
        filtered[catalogue_columns]
        .sort_values("Popularity", ascending=False)
        .head(100),
        use_container_width=True,
        hide_index=True,
    )
