from sqlalchemy.dialects import postgresql

from data_collection.fetch_reddit_data import authenticate_reddit, fetch_threads
from data_transformation.clean_data import clean_dataframe
from data_transformation.normalize_fields import normalize_timestamp
from sentiment_analysis.sentiment_vader import add_vader_sentiment
from data_storage.database_handler import save_dataframe_to_db
from visualization.visualize_sentiment import plot_sentiment_distribution, plot_sentiment_over_time

import pandas as pd

# Define configuration for analysis
config = {
    "subreddits": ["politics", "conservative", "liberal"],
    "keywords": ["election", "congress", "president"],
    "db_table": "american_politics_sentiment"
}

def main():
    # Authenticate Reddit
    reddit = authenticate_reddit()

    # Fetch threads from specified subreddits
    threads = []
    for subreddit in config["subreddits"]:
        threads += fetch_threads(reddit, subreddit, keywords=config["keywords"], limit=10)

    # Convert collected threads to a DataFrame
    threads_df = pd.DataFrame(threads)

    # Clean the text data
    cleaned_df = clean_dataframe(threads_df, text_columns=["title", "selftext"])

    # Normalize timestamps
    normalized_df = normalize_timestamp(cleaned_df, time_column="created_utc")

    # Perform sentiment analysis using VADER
    sentiment_df = add_vader_sentiment(normalized_df, text_columns=["title", "selftext"])

    # Save results to the database
    save_dataframe_to_db(sentiment_df, table_name=config["db_table"], engine=postgresql)

    # Visualize sentiment distribution
    plot_sentiment_distribution(sentiment_df)

    # Visualize sentiment trends over time
    plot_sentiment_over_time(sentiment_df, time_column="created_utc")

if __name__ == "__main__":
    main()
