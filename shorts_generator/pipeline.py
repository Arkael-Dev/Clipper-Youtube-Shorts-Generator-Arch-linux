"""End-to-end orchestrator.

Two modes:
  * mode="api"   (default) — MuAPI does download / transcribe / LLM / autocrop.
                              Fast, no local deps, pay-per-call.
  * mode="local"            — yt-dlp + faster-whisper + OpenAI or Gemini + ffmpeg/opencv.
                              Self-hosted, LLM_PROVIDER selects OpenAI or Gemini.
"""
from typing import Dict, List, Optional

from .clipper import crop_highlights
from .downloader import download_youtube
from .highlights import call_muapi_llm, get_highlights
from .transcriber import transcribe

SHORT_MIN_DURATION = 20.0
SHORT_MAX_DURATION = 90.0


def _normalize_highlight_duration(
    highlight: Dict,
    transcript: Dict,
) -> Optional[Dict]:
    """Keep generated Shorts inside a strict 20-90 second range."""
    try:
        start = float(highlight["start_time"])
        end = float(highlight["end_time"])
    except (KeyError, TypeError, ValueError):
        return None

    if end <= start:
        return None

    duration = end - start

    # Never allow a generated clip to exceed 90 seconds.
    if duration > SHORT_MAX_DURATION:
        end = start + SHORT_MAX_DURATION
        duration = SHORT_MAX_DURATION

    segments = transcript.get("segments", [])

    if segments:
        # Find transcript boundaries after the requested start.
        valid_ends = sorted(
            {
                float(seg["end"])
                for seg in segments
                if start < float(seg.get("end", 0)) <= start + SHORT_MAX_DURATION
            }
        )

        if valid_ends:
            # If Ollama returned a clip shorter than 20 seconds,
            # automatically extend it to at least 20 seconds.
            target_end = max(end, start + SHORT_MIN_DURATION)

            extended = [
                value for value in valid_ends
                if value >= target_end
            ]

            if extended:
                end = min(extended[0], start + SHORT_MAX_DURATION)
            else:
                # Use the furthest available transcript boundary,
                # still respecting the 90-second maximum.
                end = valid_ends[-1]

            duration = end - start

    # Final safety check.
    if duration < SHORT_MIN_DURATION:
        return None

    if duration > SHORT_MAX_DURATION:
        end = start + SHORT_MAX_DURATION
        duration = SHORT_MAX_DURATION

    result = dict(highlight)
    result["start_time"] = round(start, 3)
    result["end_time"] = round(end, 3)
    return result


def _prepare_short_candidates(
    highlights: List[Dict],
    transcript: Dict,
    limit: int,
) -> List[Dict]:
    """Validate and hard-limit LLM highlights for Shorts."""
    prepared = []

    for highlight in highlights:
        normalized = _normalize_highlight_duration(highlight, transcript)
        if normalized is not None:
            prepared.append(normalized)

    prepared.sort(
        key=lambda h: int(h.get("score", 0)),
        reverse=True,
    )

    return prepared[:limit]


def _run_local(
    youtube_url: str,
    num_clips: int,
    aspect_ratio: str,
    download_format: str,
    language: Optional[str],
) -> Dict:
    from .local.clipper import crop_highlights_local
    from .local.downloader import download_youtube_local
    from .local.llm import call_local_llm
    from .local.transcriber import transcribe_local

    source_path = download_youtube_local(youtube_url, fmt=download_format)

    transcript = transcribe_local(source_path, language=language)
    if not transcript["segments"]:
        raise RuntimeError(
            "Whisper produced no segments. The video may have no detectable speech."
        )

    highlights_result = get_highlights(transcript, num_clips=num_clips, llm_fn=call_local_llm)
    all_highlights: List[Dict] = highlights_result.get("highlights", [])
    if not all_highlights:
        raise RuntimeError("Highlight generator returned zero clips.")

    top = _prepare_short_candidates(
        all_highlights,
        transcript,
        num_clips,
    )

    if not top:
        raise RuntimeError(
            "No valid Shorts candidates between 20 and 90 seconds."
        )

    print(
        f"[pipeline/local] cropping {len(top)} of "
        f"{len(all_highlights)} candidates",
        flush=True,
    )

    shorts = crop_highlights_local(
        source_path,
        top,
        aspect_ratio=aspect_ratio,
        transcript=transcript,
    )

    return {
        "mode": "local",
        "source_video_url": source_path,
        "transcript": transcript,
        "highlights": all_highlights,
        "shorts": shorts,
    }


def _run_api(
    youtube_url: str,
    num_clips: int,
    aspect_ratio: str,
    download_format: str,
    language: Optional[str],
) -> Dict:
    source_url = download_youtube(youtube_url, fmt=download_format)

    transcript = transcribe(source_url, language=language)
    if not transcript["segments"]:
        raise RuntimeError(
            "Whisper produced no segments. The video may have no detectable speech."
        )

    highlights_result = get_highlights(transcript, num_clips=num_clips, llm_fn=call_muapi_llm)
    all_highlights: List[Dict] = highlights_result.get("highlights", [])
    if not all_highlights:
        raise RuntimeError("Highlight generator returned zero clips.")

    top = _prepare_short_candidates(
        all_highlights,
        transcript,
        num_clips,
    )

    if not top:
        raise RuntimeError(
            "No valid Shorts candidates between 20 and 90 seconds."
        )

    print(
        f"[pipeline] cropping {len(top)} of "
        f"{len(all_highlights)} candidates",
        flush=True,
    )

    shorts = crop_highlights(source_url, top, aspect_ratio=aspect_ratio)

    return {
        "mode": "api",
        "source_video_url": source_url,
        "transcript": transcript,
        "highlights": all_highlights,
        "shorts": shorts,
    }


def generate_shorts(
    youtube_url: str,
    num_clips: int = 3,
    aspect_ratio: str = "9:16",
    download_format: str = "720",
    language: Optional[str] = None,
    mode: str = "api",
) -> Dict:
    """Run the full pipeline and return a structured result.

    Args:
        youtube_url: source URL.
        num_clips: how many shorts to render.
        aspect_ratio: e.g. "9:16", "1:1".
        download_format: source resolution ("360" / "480" / "720" / "1080").
        language: ISO-639-1 to force Whisper language detection.
        mode: "api" (default, MuAPI) or "local" (yt-dlp + faster-whisper +
            OpenAI or Gemini + ffmpeg).

    Returns:
        {
          "mode": "api" | "local",
          "source_video_url": str,   # hosted URL (api) or local path (local)
          "transcript": {...},
          "highlights": [...],       # all candidates ranked
          "shorts": [...],           # top `num_clips` with clip_url / local path
        }
    """
    mode = (mode or "api").lower()
    if mode == "local":
        return _run_local(youtube_url, num_clips, aspect_ratio, download_format, language)
    if mode == "api":
        return _run_api(youtube_url, num_clips, aspect_ratio, download_format, language)
    raise ValueError(f"Unknown mode: {mode!r}. Use 'api' or 'local'.")
