# src/models.py

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    annotator_code: str
    role: str  # 'REVIEWER' hoặc 'ADMIN'
    active: bool = True

@dataclass
class Record:
    record_id: str
    text_annotation: str
    guideline_version: str
    batch_id: str
    data_role: str = 'PRODUCTION'

@dataclass
class LLMPrediction:
    record_id: str
    run_id: str
    model_slot: str
    model_id: str
    predicted_eligibility: str
    predicted_c: Optional[str] = None
    predicted_s: Optional[str] = None
    predicted_a: Optional[str] = None
    uncertain: bool = False

@dataclass
class HumanAnnotation:
    assignment_id: int
    record_id: str
    annotator_code: str
    eligibility: str  # 'KEEP' hoặc 'REMOVE'
    c_label: Optional[str] = None
    s_label: Optional[str] = None
    a_label: Optional[str] = None
    remove_reason: Optional[str] = None
    uncertain: str = 'NO'
    is_draft: bool = True