from app.cross_encoder import rerank_with_cross_encoder

def test_rerank_with_cross_encoder():
    query = "python developer entry level"
    jobs = [
        {"description": "Senior Python developer with 5+ years experience."},
        {"description": "Entry level Python developer, new grads welcome."},
        {"description": "Java developer, any level."},
    ]
    results = rerank_with_cross_encoder(query, jobs, top_k=2)
    assert len(results) == 2
    assert results[0][1]["description"].lower().find("entry level") != -1
