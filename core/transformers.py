from core.schemas import (
    AnalyzerOutput, InsightsInput, InsightsOutput, ReportInput
)
from typing import Optional


def analyzer_to_insights(
    analysis: AnalyzerOutput,
    period: str,
    user_goal: Optional[str] = None
) -> InsightsInput:
    return InsightsInput(
        analysis=analysis,
        period=period,
        user_goal=user_goal
    )


def insights_to_report(
    insights: InsightsOutput,
    analysis: AnalyzerOutput,
    period: str
) -> ReportInput:
    return ReportInput(
        insights=insights,
        analysis=analysis,
        period=period
    )
