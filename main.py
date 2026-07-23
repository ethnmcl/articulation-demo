import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

MODELS_DIR = Path(__file__).parent / "models"

# Feature schemas (matching what each model was trained on)
SIGNAL_FEATURE_COLS = [
    "word_count",
    "sentence_count",
    "repetition_ratio",
    "avg_new_information_decay",
    "dependency_flag_ratio",
    "undefined_advanced_term_ratio",
    "advanced_terms_used",
]

FORM_FEATURE_COLS = SIGNAL_FEATURE_COLS + [
    "over_explaining_flag",
    "over_explaining_confidence",
    "under_explaining_flag",
    "under_explaining_confidence",
]

models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    models["signal_model"] = joblib.load(MODELS_DIR / "signal_diagnostic_model.pkl")
    models["form_model"] = joblib.load(MODELS_DIR / "form_scorer_model.pkl")
    print("Both models loaded from local disk.")
    yield
    models.clear()


app = FastAPI(title="Articulation Model API", lifespan=lifespan)


class RawSignals(BaseModel):
    word_count: int
    sentence_count: int
    repetition_ratio: float
    avg_new_information_decay: float
    dependency_flag_ratio: float
    undefined_advanced_term_ratio: float
    advanced_terms_used: int


class DiagnosticFlags(BaseModel):
    over_explaining_flag: int
    over_explaining_confidence: float
    under_explaining_flag: int
    under_explaining_confidence: float


class FullFeatureSet(RawSignals, DiagnosticFlags):
    pass


@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": list(models.keys())}


@app.post("/diagnostics")
def predict_diagnostics(payload: RawSignals):
    model = models["signal_model"]
    x = pd.DataFrame([payload.model_dump()])[SIGNAL_FEATURE_COLS]
    probs = model.predict_proba(x)

    return {
        "over_explaining": {
            "flag": bool(probs[0][0][1] > 0.5),
            "confidence": round(float(probs[0][0][1]), 3),
        },
        "under_explaining": {
            "flag": bool(probs[1][0][1] > 0.5),
            "confidence": round(float(probs[1][0][1]), 3),
        },
    }


@app.post("/score")
def predict_score(payload: FullFeatureSet):
    model = models["form_model"]
    x = pd.DataFrame([payload.model_dump()])[FORM_FEATURE_COLS]
    scores = model.predict(x)[0]

    return {
        "vocabulary_score": round(float(scores[0]), 1),
        "clarity_score": round(float(scores[1]), 1),
        "credibility_score": round(float(scores[2]), 1),
    }


@app.post("/full-pipeline")
def full_pipeline(payload: RawSignals):
    diagnostics = predict_diagnostics(payload)

    combined_features = {
        **payload.model_dump(),
        "over_explaining_flag": int(diagnostics["over_explaining"]["flag"]),
        "over_explaining_confidence": diagnostics["over_explaining"]["confidence"],
        "under_explaining_flag": int(diagnostics["under_explaining"]["flag"]),
        "under_explaining_confidence": diagnostics["under_explaining"]["confidence"],
    }
    scores = predict_score(FullFeatureSet(**combined_features))

    return {"diagnostics": diagnostics, "scores": scores}
