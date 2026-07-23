# Articulation Model API (self-contained, free)

Both models are baked directly into the Docker image — no Hugging Face
downloads, no HF_TOKEN, no external calls at runtime. Render just builds
and runs this.

## Project structure
```
articulation-api-v2/
├── Dockerfile
├── requirements.txt
├── .dockerignore
└── app/
    ├── main.py
    └── models/
        ├── signal_diagnostic_model.pkl
        └── form_scorer_model.pkl
```

## Deploy on Render

1. Push this whole folder to a GitHub repo (including the `.pkl` files in `app/models/`).
2. In Render: **New → Web Service**, connect the repo.
3. Render auto-detects the `Dockerfile` and builds it. No environment variables needed.
4. Deploy. You get a public URL like `https://your-service.onrender.com`.

## Endpoints

- `GET /health`
- `POST /diagnostics` — Model 1 only (7 raw signal features in)
- `POST /score` — Model 2 only (11 features in: 7 raw + 4 diagnostic)
- `POST /full-pipeline` — chains both automatically (7 raw features in, full result out)

### Example
```bash
curl -X POST https://your-service.onrender.com/full-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "word_count": 224,
    "sentence_count": 11,
    "repetition_ratio": 0.76,
    "avg_new_information_decay": 0.453,
    "dependency_flag_ratio": 0.273,
    "undefined_advanced_term_ratio": 0.183,
    "advanced_terms_used": 3
  }'
```

## Note on file size

GitHub blocks files over 100MB by default. Both `.pkl` files here are well
under that (form_scorer ~1MB, signal_diagnostic ~0.3MB), so a normal `git add`
+ `git push` works fine — no Git LFS needed.
