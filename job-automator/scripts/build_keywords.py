#!/usr/bin/env python3
"""
build_keywords.py — Builds keywords_only.json from master_profile.json.
Uses SHA-256 hash to skip rebuild if source hasn't changed.

Usage: python build_keywords.py
Reads  : <skill>/references/master_profile.json
Writes : <skill>/references/keywords_only.json

Exit codes:
  0 — keywords_only.json is valid and up to date (cache hit or rebuilt)
  1 — error (missing files, parse failure)

Stdout:
  CACHE_HIT   — no rebuild needed
  REBUILT     — rebuilt from updated profile
"""

import json
import sys
import os
import hashlib
import re

# Resolve this skill's own references/ dir from __file__ so the script works
# identically regardless of where the skill dir lives or is renamed to.
_REFS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references")

SKILL_DIR    = _REFS
PROFILE_PATH = os.path.join(SKILL_DIR, "master_profile.json")
OUTPUT_PATH  = os.path.join(SKILL_DIR, "keywords_only.json")


def file_hash(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def is_cache_valid() -> bool:
    if not os.path.exists(OUTPUT_PATH):
        return False
    try:
        cached = json.load(open(OUTPUT_PATH))
        return cached.get("source_hash") == file_hash(PROFILE_PATH)
    except (json.JSONDecodeError, KeyError):
        return False


def extract_keywords(profile: dict) -> list[str]:
    keywords = set()

    # ── 1. Skills section — primary source, already clean and complete ──
    for category, items in profile.get("skills", {}).items():
        for item in items:
            # Split compound entries like "Python, C/C++, CUDA" if any
            for part in re.split(r"[,;]", item):
                kw = part.strip()
                if kw:
                    keywords.add(kw)

    # ── 2. Summary pool — extract noun phrases and technical terms ──
    for key, text in profile.get("summary_pool", {}).items():
        # Grab capitalized multi-word phrases and known tech terms
        terms = re.findall(
            r'\b(?:ROS\s*2?|CUDA\s*C\+\+?|C\+\+|FreeRTOS|TensorRT|PyTorch|'
            r'TensorFlow|OpenCV|YOLO\w*|STM32|MoveIt|RViz|SLURM|MPI|Cython|'
            r'Raspberry\s+Pi|NVIDIA\s+Jetson|bare-metal|bare\s+metal|'
            r'[A-Z][a-zA-Z0-9+#\.]+(?:\s+[A-Z][a-zA-Z0-9+#\.]+)*)\b',
            text
        )
        keywords.update(t.strip() for t in terms if len(t.strip()) > 2)

    # ── 3. Experience and project bullets — technical terms only ──
    STOP_WORDS = {
        "The", "This", "A", "An", "In", "On", "At", "By", "To", "For",
        "With", "From", "And", "Or", "Of", "As", "Is", "Was", "Are",
        "Built", "Used", "Led", "Ran", "Got", "Set", "Put", "Got",
        "Implemented", "Developed", "Designed", "Achieved", "Deployed",
        "Trained", "Created", "Resolved", "Integrated", "Optimized",
        "Validated", "Programmed", "Engineered", "Architected", "Curated",
        "Improved", "Reduced", "Increased", "Produced", "Evaluated",
        "Identified", "Characterized", "Demonstrated", "Performed",
    }

    for section in ["experience", "projects"]:
        for entry in profile.get(section, []):
            for bullet in entry.get("bullets", []):
                # Capitalized technical terms and abbreviations
                terms = re.findall(
                    r'\b[A-Z][a-zA-Z0-9+#\.]+(?:[/-][A-Za-z0-9+#\.]+)*\b'
                    r'|\b[A-Z]{2,}(?:[0-9]+)?\b'
                    r'|\bC\+\+\b|\bC/C\+\+\b',
                    bullet
                )
                for t in terms:
                    if t not in STOP_WORDS and len(t) > 1:
                        keywords.add(t)

                # Specific lowercase tech terms commonly in Justin's domain
                lower = bullet.lower()
                for term in [
                    "python", "bash", "linux", "git", "cmake", "makefile",
                    "pytorch", "tensorflow", "keras", "cuda", "cuda c++",
                    "ros", "ros2", "ros 2", "freertos", "tensorrt",
                    "opencv", "yolo", "yolov8", "mpi", "slurm",
                    "pdflatex", "jupyter", "flask", "websocket",
                    "quantization", "pruning", "fine-tuning", "fine tuning",
                    "transformer", "attention", "tokenizer", "bpe",
                    "uart", "i2c", "spi", "gpio", "adc", "pwm",
                    "bare-metal", "interrupt", "dma", "rtos",
                    "object detection", "visual servoing", "depth estimation",
                    "memory coalescing", "kernel optimization",
                    "structured pruning", "8-bit quantization",
                    "forward kinematics", "inverse kinematics",
                    "pick and place", "motion planning",
                    "safety-critical", "fault detection", "multithreading",
                    "state machine", "gui", "wearable", "haptic", "user study",
                    "data acquisition", "test automation", "sensor integration",
                    "hardware/software integration", "h-bridge", "thermistor",
                    "microcontroller", "cross-platform",
                ]:
                    if term in lower:
                        keywords.add(term)

    # ── 4. Education courses ──
    for edu in profile.get("education", []):
        for course in edu.get("courses", []):
            keywords.add(course.strip())

    # ── 5. Awards — extract tech terms ──
    for award in profile.get("awards", []):
        terms = re.findall(r'\b[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*\b', award)
        keywords.update(t for t in terms if len(t) > 3)

    # Clean and sort
    cleaned = sorted(
        {kw.strip() for kw in keywords if kw.strip() and len(kw.strip()) > 1},
        key=str.lower
    )
    return cleaned


def build(profile_path: str) -> dict:
    profile  = json.load(open(profile_path))
    keywords = extract_keywords(profile)
    info     = profile.get("personal_info", {})

    return {
        "source_hash"     : file_hash(profile_path),
        "name"            : info.get("name", ""),
        "experience_level": "new-grad",
        "full_time_years" : 0,
        "internships"     : 7,
        "strongest_areas" : [
            "CUDA / GPU kernel optimization",
            "Edge AI deployment (Jetson + TensorRT + YOLO)",
            "Embedded C/C++ bare-metal (STM32 Cortex-M4)",
            "ROS2 / Robotics / perception pipelines",
            "ML model optimization (pruning, quantization, ASR)"
        ],
        "all_keywords": keywords,
        "total_keywords"  : len(keywords),
    }


def main():
    if not os.path.exists(PROFILE_PATH):
        print(f"ERROR: master_profile.json not found at {PROFILE_PATH}", file=sys.stderr)
        sys.exit(1)

    if is_cache_valid():
        cached = json.load(open(OUTPUT_PATH))
        print(f"CACHE_HIT ({cached['total_keywords']} keywords)")
        sys.exit(0)

    try:
        data = build(PROFILE_PATH)
        with open(OUTPUT_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print(f"REBUILT ({data['total_keywords']} keywords)")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
