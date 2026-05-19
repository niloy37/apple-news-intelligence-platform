"""Pandera data quality schemas for batch validation jobs."""

from __future__ import annotations


def article_schema():
    from pandera import Column, DataFrameSchema, Check

    return DataFrameSchema(
        {
            "url": Column(str, nullable=False, unique=True),
            "headline": Column(str, Check.str_length(min_value=1), nullable=False),
            "publisher": Column(str, Check.str_length(min_value=1), nullable=False),
            "published_at": Column(nullable=False),
            "language": Column(str, nullable=False),
        }
    )


def social_post_schema():
    from pandera import Column, DataFrameSchema, Check

    return DataFrameSchema(
        {
            "post_id": Column(str, nullable=False, unique=True),
            "platform": Column(str, nullable=False),
            "text": Column(str, Check.str_length(min_value=1), nullable=False),
            "created_at": Column(nullable=False),
            "sentiment_score": Column(float, Check.in_range(-1, 1), nullable=True),
        }
    )
