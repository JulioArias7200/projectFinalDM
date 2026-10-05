"""Validate and publish the current persona candidate using JSON persistence."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.proprosessing.final_validation_sampling import DEFAULT_CANDIDATE, validate
from data.proprosessing.version_registry import publish_validated_candidate


def main(candidate_dir: Path = DEFAULT_CANDIDATE, actor: str = "project_owner") -> Path:
    _, _, _, validation, _ = validate(candidate_dir)
    if validation["validation_status"] != "passed":
        raise RuntimeError("Publicación cancelada: falló uno o más controles censales.")
    return publish_validated_candidate(candidate_dir, validation, actor=actor)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--actor", default="project_owner")
    args = parser.parse_args()
    print(main(args.candidate, args.actor))
