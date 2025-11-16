import os
import json
from typing import List
from urllib import request, error

def _call_hf_chat(prompt: str) -> str:
    """
    Call a HuggingFace Inference API text generation model.

    Requires:
      - HF_API_TOKEN
      - HF_MODEL_ID (e.g. mistralai/Mistral-7B-Instruct-v0.3)
    """
    api_token = os.environ.get("HF_API_TOKEN")
    model_id = os.environ.get("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.3")

    if not api_token:
        raise RuntimeError("HF_API_TOKEN not set")

    url = f"https://api-inference.huggingface.co/models/{model_id}"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    body = {
        "inputs": (
            "You are a friendly tutor-matching assistant. "
            "Write short, student-friendly explanations.\n\n"
            + prompt
        ),
        "parameters": {
            "max_new_tokens": 250,
            "temperature": 0.6,
        },
    }

    data = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, headers=headers, method="POST")

    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            j = json.loads(raw)

            # HF often returns a list of { "generated_text": ... }
            if isinstance(j, list) and len(j) > 0 and "generated_text" in j[0]:
                return j[0]["generated_text"]

            # Some models respond differently; try a fallback
            if isinstance(j, dict) and "generated_text" in j:
                return j["generated_text"]

            raise RuntimeError(f"Unexpected HF response format: {j}")
    except error.HTTPError as e:
        raise RuntimeError(
            f"HF HTTP error: {e.code} {e.reason} - "
            f"{e.read().decode('utf-8', errors='ignore')}"
        )
    except Exception as e:
        raise RuntimeError(f"HuggingFace call failed: {e}")


def _read_prompt_template():
    try:
        here = os.path.dirname(__file__)
        path = os.path.join(here, "ai_prompt.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        # fallback simple template
        return (
            "{STUDENT_NAME}, based on your interests in {STUDENT_PREFERENCES} and your location in {STUDENT_CITY}, "
            "Tutor {TUTOR_NAME} is a good match. They teach {TUTOR_SUBJECTS}, have a rating of {TUTOR_RATING}, "
            "and their rate is ${TUTOR_HOURLY_RATE}.\n\nWhy this match: {MATCH_REASONS}"
        )


def _call_azure_openai_chat(prompt: str) -> str:
    """
    Call Azure OpenAI Chat Completions API (chat/completions). Expects the following env vars to be set:
      - AZURE_OPENAI_ENDPOINT (e.g. https://your-resource.openai.azure.com)
      - AZURE_OPENAI_KEY
      - AZURE_OPENAI_DEPLOYMENT (the deployment name for a chat model)

    Returns the assistant text content on success.
    """
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    key = os.environ.get("AZURE_OPENAI_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-10-01")

    if not endpoint or not key or not deployment:
        raise RuntimeError("Azure OpenAI environment variables not configured (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT)")

    url = endpoint.rstrip("/") + f"/openai/deployments/{deployment}/chat/completions?api-version={api_version}"

    headers = {
        "Content-Type": "application/json",
        "api-key": key,
    }

    body = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that produces short, student-friendly explanations."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 400,
        "temperature": 0.6,
    }

    data = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
            j = json.loads(raw)
            # Azure chat response contains choices[0].message.content
            if "choices" in j and len(j["choices"]) > 0:
                msg = j["choices"][0].get("message")
                if msg and "content" in msg:
                    return msg["content"]
                # older deployments may place text in 'text'
                return j["choices"][0].get("text", "")
            raise RuntimeError("No choices in OpenAI response")
    except error.HTTPError as e:
        raise RuntimeError(f"Azure OpenAI HTTP error: {e.code} {e.reason} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        raise RuntimeError(f"Azure OpenAI call failed: {e}")


def _deterministic_explanation(student, tutor) -> str:
    # compute match reasons
    reasons = []
    try:
        prefs = [s.strip() for s in (student.preferred_subjects or "").split(",") if s.strip()]
    except Exception:
        prefs = []

    tutor_subjects = [s.name for s in getattr(tutor, "subjects", [])]
    overlap = list(set(prefs) & set(tutor_subjects)) if prefs else []
    if overlap:
        reasons.append(f"Matches your subjects: {', '.join(overlap)}")
    if getattr(student, "city", None) and getattr(tutor, "city", None) and student.city.lower() == tutor.city.lower():
        reasons.append(f"Located in the same city ({tutor.city})")
    if getattr(student, "max_hourly_rate", None) is not None and tutor.hourly_rate is not None:
        if tutor.hourly_rate <= student.max_hourly_rate:
            reasons.append(f"Within your budget (${tutor.hourly_rate}/hr)")
        else:
            reasons.append(f"Slightly above your budget (${tutor.hourly_rate}/hr)")
    if getattr(tutor, "overall_rating", None) and tutor.overall_rating >= 4.2:
        reasons.append(f"Highly rated ({tutor.overall_rating:.1f}★)")

    if not reasons:
        reasons = ["Good general fit based on available profile data"]

    # NOTE: placeholders are wrapped in {}, and we REPLACE the whole token including braces
    template = (
        "{STUDENT_NAME}, based on your interests in {STUDENT_PREFERENCES} and your location in {STUDENT_CITY}, "
        "Tutor {TUTOR_NAME} looks like a strong match. They teach {TUTOR_SUBJECTS}, have an average rating of "
        "{TUTOR_RATING}, and their hourly rate of ${TUTOR_HOURLY_RATE} is a good fit for your profile.\n\n"
        "Why this match: {MATCH_REASONS}"
    )

    filled = template
    filled = filled.replace("{STUDENT_NAME}", getattr(student, "name", "Student"))
    filled = filled.replace("{STUDENT_PREFERENCES}", ", ".join(prefs) if prefs else "your selected subjects")
    filled = filled.replace("{STUDENT_CITY}", getattr(student, "city", "your area") or "your area")
    filled = filled.replace("{TUTOR_NAME}", getattr(tutor, "name", "Tutor"))
    filled = filled.replace("{TUTOR_SUBJECTS}", ", ".join(tutor_subjects) if tutor_subjects else "their subjects")
    filled = filled.replace("{TUTOR_HOURLY_RATE}", f"{getattr(tutor, 'hourly_rate', 'N/A')}")
    filled = filled.replace("{TUTOR_RATING}", f"{getattr(tutor, 'overall_rating', 'N/A')}")
    filled = filled.replace("{MATCH_REASONS}", "; ".join(reasons[:3]))

    return filled.strip()

def explain_recommendations(student, tutors: List) -> List[str]:
    """
    Try to use a hosted open-source model via HuggingFace to generate
    short explanations for each tutor. If anything fails, fall back to
    the deterministic explanation for each tutor.
    """
    if not tutors:
        return []

    # Build a compact JSON description for the prompt
    try:
        rows = []
        for t in tutors:
            rows.append({
                "tutor_id": getattr(t, "id", None),
                "name": getattr(t, "name", None),
                "subjects": [s.name for s in getattr(t, "subjects", [])],
                "hourly_rate": getattr(t, "hourly_rate", None),
                "rating": getattr(t, "overall_rating", None),
            })

        student_info = {
            "id": getattr(student, "id", None),
            "name": getattr(student, "name", None),
            "preferences": getattr(student, "preferred_subjects", None),
            "city": getattr(student, "city", None),
            "max_hourly_rate": getattr(student, "max_hourly_rate", None),
        }

        prompt_lines = [
            "You will receive a student and a list of tutors.",
            "Return a JSON array. Each element must have:",
            "- tutor_id (matching the tutor_id from input)",
            "- explanation (2 short sentences, friendly, explaining why this tutor fits the student).",
            "Do NOT include anything other than the JSON array.\n",
            "Student:",
            json.dumps(student_info),
            "Tutors:",
            json.dumps([{"tutor_id": r["tutor_id"], **r} for r in rows]),
        ]
        prompt = "\n".join(prompt_lines)

        # Try HF
        try:
            text = _call_hf_chat(prompt)
            cleaned = text.strip()
            # try to find first '[' in case model added some prefix
            idx = cleaned.find("[")
            if idx != -1:
                cleaned = cleaned[idx:]
            parsed = json.loads(cleaned)

            id_to_ex = {}
            for item in parsed:
                tid = item.get("tutor_id")
                ex = item.get("explanation")
                if tid is not None and ex:
                    id_to_ex[int(tid)] = ex

            return [
                id_to_ex.get(getattr(t, "id", None), _deterministic_explanation(student, t))
                for t in tutors
            ]
        except Exception:
            # any failure -> deterministic fallback
            return [_deterministic_explanation(student, t) for t in tutors]

    except Exception:
        # final safety net
        return [_deterministic_explanation(student, t) for t in tutors]
