"""Build workflow coordinator for multi-phase projects."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Phase:
    identifier: str
    name: str
    required_validations: List[str] = field(default_factory=list)


class BuildWorkflowCoordinator:
    """Coordinates build phases and enforces validation checkpoints."""

    PHASES: List[Phase] = [
        Phase("planning", "Master Planning"),
        Phase("shell", "Structural Shell", required_validations=["structure_validation"]),
        Phase("facade", "Facade Detailing"),
        Phase("roof", "Roof Construction"),
        Phase("interior", "Interior Design", required_validations=["lighting_analysis"]),
        Phase("landscape", "Landscape"),
        Phase("redstone", "Redstone & Utilities"),
        Phase(
            "quality",
            "Quality Assurance",
            required_validations=["structure_validation", "lighting_analysis", "symmetry_check"],
        ),
    ]

    def __init__(self, state_path: Path):
        self.state_path = state_path
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, object]:
        if self.state_path.exists():
            try:
                with open(self.state_path, "r", encoding="utf-8") as handle:
                    return json.load(handle)
            except Exception:
                pass
        return {
            "current_phase": self.PHASES[0].identifier,
            "completed_phases": [],
            "validations": {},
        }

    def _save_state(self) -> None:
        with open(self.state_path, "w", encoding="utf-8") as handle:
            json.dump(self.state, handle, indent=2)

    def get_phase(self, identifier: str) -> Optional[Phase]:
        for phase in self.PHASES:
            if phase.identifier == identifier:
                return phase
        return None

    def current_phase(self) -> Phase:
        identifier = self.state.get("current_phase", self.PHASES[0].identifier)
        phase = self.get_phase(identifier)
        return phase or self.PHASES[0]

    def record_validation(self, validation_type: str, payload: Dict[str, object]) -> None:
        validations = self.state.setdefault("validations", {})
        entries = validations.setdefault(validation_type, [])
        entries.append(payload)
        self._save_state()

    def get_status(self) -> Dict[str, object]:
        phase_status = []
        current = self.current_phase().identifier
        completed = set(self.state.get("completed_phases", []))

        for phase in self.PHASES:
            if phase.identifier in completed:
                status = "completed"
            elif phase.identifier == current:
                status = "in_progress"
            else:
                status = "pending"

            phase_status.append(
                {
                    "id": phase.identifier,
                    "name": phase.name,
                    "status": status,
                    "required_validations": phase.required_validations,
                    "completed_validations": {
                        vt: len(self.state.get("validations", {}).get(vt, []))
                        for vt in phase.required_validations
                    },
                }
            )

        return {
            "current_phase": current,
            "phases": phase_status,
            "validations": self.state.get("validations", {}),
        }

    def can_advance(self) -> Dict[str, object]:
        phase = self.current_phase()
        validations = self.state.get("validations", {})
        missing = [
            requirement
            for requirement in phase.required_validations
            if not validations.get(requirement)
        ]
        return {"ok": not missing, "missing": missing, "phase": phase.identifier}

    def advance(self) -> Dict[str, object]:
        check = self.can_advance()
        if not check["ok"]:
            return {
                "advanced": False,
                "reason": "Missing required validations",
                "missing": check["missing"],
                "phase": check["phase"],
            }

        current_phase = self.current_phase()
        completed = self.state.setdefault("completed_phases", [])
        if current_phase.identifier not in completed:
            completed.append(current_phase.identifier)

        current_index = next(
            (
                index
                for index, phase in enumerate(self.PHASES)
                if phase.identifier == current_phase.identifier
            ),
            len(self.PHASES) - 1,
        )

        if current_index + 1 < len(self.PHASES):
            self.state["current_phase"] = self.PHASES[current_index + 1].identifier
            self._save_state()
            return {"advanced": True, "current_phase": self.state["current_phase"]}

        self._save_state()
        return {
            "advanced": False,
            "reason": "Already at final phase",
            "phase": current_phase.identifier,
        }

    def reset(self) -> None:
        self.state = {
            "current_phase": self.PHASES[0].identifier,
            "completed_phases": [],
            "validations": {},
        }
        self._save_state()
