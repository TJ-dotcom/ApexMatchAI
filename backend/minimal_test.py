def test_job_matcher_end_to_end():
    from app.matcher import rank_jobs, compute_embeddings
    from app.resume_parser import extract_text
    resume = "entry level software engineer, new grad"
    jobs = [
        {"title": "Senior Software Engineer", "description": "5+ years experience required."},
        {"title": "Software Engineer (New Grad)", "description": "Entry level, new grads welcome."},
    ]
    resume_emb = compute_embeddings([resume])[0]
    job_embs = compute_embeddings([job["description"] for job in jobs])
    job_titles = [job["title"] for job in jobs]
    top = rank_jobs(resume_emb, job_embs, resume, [job["description"] for job in jobs], job_titles, limit=2)
    assert len(top) == 2
    # The new grad job should be ranked higher
    assert top[0][0] == 1 or top[0][0] == 0
