"""
jitna_validator.py

Validates that a text or dict conforms to the JITNA v3 packet schema.
Used in CI, dataset validation, and inference quality gates.

Schema defined in: delentia-os/rct_control_plane/jitna_protocol_v3.py
"""

import json
import re
import uuid
from dataclasses import dataclass, field
from typing import Any

# ── JITNA v3 constants ────────────────────────────────────────────────────────

SCHEMA_VERSION   = "3.0"
VALID_PRIORITIES = {1, 2, 3, 4, 5}
VALID_MSG_TYPES  = {
    "INTENT_REQUEST", "INTENT_RESPONSE", "NEGOTIATION", "CONFIRMATION",
    "STATUS_UPDATE", "ERROR", "HEARTBEAT", "STREAM_CHUNK", "STREAM_END",
}
VALID_STATUSES = {
    "CREATED", "SENT", "RECEIVED", "PROCESSING", "COMPLETED", "FAILED",
}
ISO8601_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"  # basic date-time
    r"(\.\d+)?"                                 # optional fractional seconds
    r"(Z|[+-]\d{2}:\d{2})?$"                   # optional timezone
)
REQUIRED_FIELDS = {
    "packet_id", "source_agent_id", "target_agent_id",
    "message_type", "payload", "timestamp", "schema_version",
    "priority", "metadata", "status", "hop_trace", "ttl", "compressed",
}


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.valid = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


class JITNAValidator:
    """
    Validates JITNA v3 packets.

    Usage:
        validator = JITNAValidator()
        result = validator.validate(packet_dict)
        if not result.valid:
            print(result.errors)
    """

    def validate(self, packet: dict[str, Any]) -> ValidationResult:
        result = ValidationResult(valid=True)
        self._check_required_fields(packet, result)
        if result.valid:
            self._check_schema_version(packet, result)
            self._check_message_type(packet, result)
            self._check_priority(packet, result)
            self._check_status(packet, result)
            self._check_timestamp(packet, result)
            self._check_payload(packet, result)
            self._check_packet_id(packet, result)
            self._check_hop_trace(packet, result)
            self._check_ttl(packet, result)
            self._check_v3_fields(packet, result)
        return result

    def validate_json(self, text: str) -> ValidationResult:
        """Validate a JSON string — parses first, then validates structure."""
        result = ValidationResult(valid=True)
        try:
            packet = json.loads(text)
        except json.JSONDecodeError as e:
            result.add_error(f"JSON parse error: {e}")
            return result
        if not isinstance(packet, dict):
            result.add_error("Packet must be a JSON object")
            return result
        return self.validate(packet)

    # ── Internal checkers ─────────────────────────────────────────────────────

    def _check_required_fields(self, p: dict, r: ValidationResult) -> None:
        missing = REQUIRED_FIELDS - set(p.keys())
        for f in sorted(missing):
            r.add_error(f"Missing required field: '{f}'")

    def _check_schema_version(self, p: dict, r: ValidationResult) -> None:
        if p.get("schema_version") != SCHEMA_VERSION:
            r.add_error(
                f"schema_version must be '{SCHEMA_VERSION}', got '{p.get('schema_version')}'"
            )

    def _check_message_type(self, p: dict, r: ValidationResult) -> None:
        if p.get("message_type") not in VALID_MSG_TYPES:
            r.add_error(
                f"Invalid message_type '{p.get('message_type')}'. "
                f"Valid: {sorted(VALID_MSG_TYPES)}"
            )

    def _check_priority(self, p: dict, r: ValidationResult) -> None:
        pri = p.get("priority")
        if pri not in VALID_PRIORITIES:
            r.add_error(f"priority must be 1–5, got {pri!r}")

    def _check_status(self, p: dict, r: ValidationResult) -> None:
        if p.get("status") not in VALID_STATUSES:
            r.add_error(
                f"Invalid status '{p.get('status')}'. Valid: {sorted(VALID_STATUSES)}"
            )

    def _check_timestamp(self, p: dict, r: ValidationResult) -> None:
        ts = p.get("timestamp", "")
        if not isinstance(ts, str) or not ISO8601_RE.match(ts):
            r.add_error(f"timestamp must be ISO 8601 UTC string, got '{ts}'")

    def _check_payload(self, p: dict, r: ValidationResult) -> None:
        payload = p.get("payload")
        if not isinstance(payload, dict):
            r.add_error(f"payload must be a dict, got {type(payload).__name__}")
        elif len(payload) == 0:
            r.add_warning("payload is empty — ensure this is intentional")

    def _check_packet_id(self, p: dict, r: ValidationResult) -> None:
        pid = p.get("packet_id", "")
        if not isinstance(pid, str) or not pid:
            r.add_error("packet_id must be a non-empty string")
            return
        try:
            uuid.UUID(pid)
        except ValueError:
            r.add_warning(f"packet_id '{pid}' is not a standard UUID — acceptable but non-standard")

    def _check_hop_trace(self, p: dict, r: ValidationResult) -> None:
        ht = p.get("hop_trace")
        if not isinstance(ht, list):
            r.add_error(f"hop_trace must be a list, got {type(ht).__name__}")
        elif not all(isinstance(h, str) for h in ht):
            r.add_error("hop_trace must be a list of strings")

    def _check_ttl(self, p: dict, r: ValidationResult) -> None:
        ttl = p.get("ttl")
        if not isinstance(ttl, int) or ttl < 0:
            r.add_error(f"ttl must be a non-negative integer, got {ttl!r}")
        elif ttl == 0:
            r.add_warning("ttl=0 — packet will be dropped immediately at next hop")

    def _check_v3_fields(self, p: dict, r: ValidationResult) -> None:
        """Check v3-specific fields (compressed, hop_trace, ttl already checked)."""
        if not isinstance(p.get("compressed"), bool):
            r.add_error(f"compressed must be bool, got {type(p.get('compressed')).__name__}")


# Convenience function
def validate_jitna_packet(packet: dict | str) -> ValidationResult:
    """Validate a JITNA v3 packet (dict or JSON string)."""
    v = JITNAValidator()
    if isinstance(packet, str):
        return v.validate_json(packet)
    return v.validate(packet)
