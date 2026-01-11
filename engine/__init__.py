# Engine module
from .recommender import RecommendationEngine as HeroRecommender
from .ai_recommender import AIRecommender, format_data_preview
from .recommendation_engine import RecommendationEngine, get_engine

# Analyzers
from .analyzers import (
    HeroAnalyzer,
    GearAdvisor,
    LineupBuilder,
    ProgressionTracker,
    RequestClassifier
)

__all__ = [
    'RecommendationEngine',
    'get_engine',
    'HeroRecommender',  # Legacy name for old recommender.py
    'AIRecommender',
    'format_data_preview',
    'HeroAnalyzer',
    'GearAdvisor',
    'LineupBuilder',
    'ProgressionTracker',
    'RequestClassifier'
]
