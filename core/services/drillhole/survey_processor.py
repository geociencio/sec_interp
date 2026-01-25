from __future__ import annotations

"""Processing logic for Drillhole Surveys."""


class SurveyProcessor:
    """Handles survey data processing."""

    def determine_final_depth(
        self, given_depth: float, survey_data: list[tuple], intervals: list[tuple]
    ) -> float:
        """Determine final depth from given depth, surveys and intervals."""
        max_s_depth = max([s[0] for s in survey_data]) if survey_data else 0.0
        max_i_depth = max([i[1] for i in intervals]) if intervals else 0.0
        return max(given_depth, max_s_depth, max_i_depth)
