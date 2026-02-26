from functions.core.export import build_export_rows, export_csv_bytes, export_xlsx_bytes


def test_export_bytes():
    rows = build_export_rows(
        selected_skills=[
            {
                "skill_id": "A",
                "skill_name": "Skill A",
                "source": "lightcast",
                "relevance_score": 0.5,
                "reasoning": "r",
                "evidence": ["e1", "e2"],
                "skill_text": "t",
                "Foundational_Criteria": "f",
                "Intermediate_Criteria": "i",
                "Advanced_Criteria": "a",
            }
        ],
        query="q",
        generation_cache_id="cid",
    )
    csv_b = export_csv_bytes(rows)
    xlsx_b = export_xlsx_bytes(rows)
    assert len(csv_b) > 10
    assert len(xlsx_b) > 1000