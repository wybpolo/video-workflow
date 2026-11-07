#!/usr/bin/env python3
"""Check the agent handoff contract; does not compile a timeline or inspect footage."""
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import sys


def positive_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def check(plan, root, structure_only=False):
    errors, warnings = [], []
    if not isinstance(plan, dict):
        return {"structure_pass": False, "errors": ["plan must be an object"], "warnings": []}
    def require(condition, message):
        if not condition:
            errors.append(message)
    require(plan.get('schema') == 'car-video.plan.v1', 'unsupported schema')
    for key in ('job_id', 'topic', 'message'):
        require(isinstance(plan.get(key), str) and bool(plan[key].strip()), f'{key} required')
    try:
        fps = Fraction(str(plan.get('fps', '0')))
        if not 0 < fps <= 240:
            raise ValueError()
    except (ValueError, ZeroDivisionError):
        fps = Fraction(30)
        errors.append('fps must be a positive rational <= 240')
    canvas = plan.get('canvas', {})
    require(isinstance(canvas, dict) and all(positive_int(canvas.get(k)) for k in ('width', 'height')), 'canvas needs positive integer width/height')
    require(positive_int(plan.get('total_frames')), 'total_frames must be a positive integer')
    require(plan.get('renderer') in ('jianying', 'ffmpeg', 'hyperframes'), 'unknown renderer')
    require(isinstance(plan.get('deliverables'), list) and bool(plan['deliverables']), 'deliverables required')
    scope = plan.get('vehicle_scope', {})
    require(isinstance(scope, dict) and scope.get('mode') in ('illustration', 'single_vehicle', 'comparison'), 'vehicle_scope.mode required')
    audio = plan.get('audio', {})
    require(isinstance(audio, dict) and audio.get('status') in ('planned', 'deferred', 'silent', 'complete'), 'audio.status required')
    sources, claims = {}, {}
    for field, destination in (('sources', sources), ('claims', claims)):
        rows = plan.get(field, [])
        if not isinstance(rows, list):
            errors.append(f'{field} must be an array')
            continue
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id']:
                errors.append(f'{field}: object with nonempty id required')
                continue
            require(row['id'] not in destination, f'{field}: duplicate id {row["id"]}')
            destination[row['id']] = row
    for ident, source in sources.items():
        path = source.get('path')
        require(isinstance(path, str) and bool(path), f'{ident}: path required')
        require(source.get('kind') in ('video', 'image'), f'{ident}: kind video/image required')
        if path and isinstance(path, str) and not structure_only:
            p = Path(path)
            require((p if p.is_absolute() else root / p).is_file(), f'{ident}: media missing: {path}')
        if not source.get('origin'):
            warnings.append(f'{ident}: source provenance missing')
        if not source.get('sha256'):
            warnings.append(f'{ident}: hash not recorded')
        if source.get('original_start_sec') is not None:
            require(number(source['original_start_sec']) and source['original_start_sec'] >= 0, f'{ident}: invalid original_start_sec')
        if isinstance(scope, dict) and scope.get('mode') != 'illustration' and source.get('vehicle_verified') is not True:
            warnings.append(f'{ident}: vehicle identity has not been verified')
    for ident, claim in claims.items():
        require(claim.get('kind') in ('illustration', 'observation', 'measurement', 'specification'), f'{ident}: unknown claim kind')
        require(isinstance(claim.get('text'), str) and bool(claim['text']), f'{ident}: claim text required')
        if claim.get('kind') != 'illustration' and not claim.get('evidence'):
            errors.append(f'{ident}: factual claim requires evidence')
        if claim.get('kind') == 'measurement' and not claim.get('unit'):
            warnings.append(f'{ident}: measurement unit not recorded')
    shots = plan.get('shots', [])
    require(isinstance(shots, list) and bool(shots), 'nonempty shots array required')
    cursor, ids = 0, set()
    for shot in shots if isinstance(shots, list) else []:
        if not isinstance(shot, dict):
            errors.append('shot must be an object')
            continue
        ident = shot.get('id')
        if not isinstance(ident, str) or not ident:
            errors.append('shot id required')
            ident = 'unnamed'
        require(ident not in ids, f'duplicate shot id {ident}')
        ids.add(ident)
        start, frames = shot.get('start_frame'), shot.get('frames')
        require(isinstance(start, int) and not isinstance(start, bool) and start == cursor, f'{ident}: start_frame must be {cursor} (main shots are contiguous)')
        require(positive_int(frames), f'{ident}: frames must be a positive integer')
        if positive_int(frames):
            cursor += frames
        require(bool(shot.get('purpose')), f'{ident}: purpose required')
        require(shot.get('render_mode') in ('native', 'pre-render'), f'{ident}: render_mode required')
        for claim_id in shot.get('claim_ids', []):
            require(isinstance(claim_id, str) and claim_id in claims, f'{ident}: unknown claim {claim_id}')
        inputs = shot.get('inputs', [])
        if not isinstance(inputs, list):
            errors.append(f'{ident}: inputs must be an array')
            continue
        for inp in inputs:
            if not isinstance(inp, dict):
                errors.append(f'{ident}: input must be an object')
                continue
            source_id = inp.get('source_id')
            if not isinstance(source_id, str) or source_id not in sources:
                errors.append(f'{ident}: unknown source {source_id}')
                continue
            a, b, speed, hold = (inp.get('in_sec'), inp.get('out_sec'), inp.get('speed', 1), inp.get('hold_last_frames', 0))
            valid = all(number(v) for v in (a, b, speed)) and 0 <= a < b and speed > 0
            require(valid, f'{ident}/{source_id}: invalid source range or speed')
            valid_hold = isinstance(hold, int) and not isinstance(hold, bool) and hold >= 0
            require(valid_hold, f'{ident}/{source_id}: invalid hold_last_frames')
            if valid and valid_hold and positive_int(frames) and sources[source_id].get('kind') == 'video':
                require((b-a)/speed*float(fps)+hold+0.51 >= frames, f'{ident}/{source_id}: selected media too short; declare hold, speed or change range')
            reviewed = sources[source_id].get('reviewed_ranges', [])
            clean = valid and any(isinstance(r, dict) and number(r.get('in_sec')) and number(r.get('out_sec')) and r['in_sec'] <= a and b <= r['out_sec'] for r in reviewed if isinstance(reviewed, list))
            if not clean:
                warnings.append(f'{ident}/{source_id}: no recorded reviewed range covering this selection')
    require(cursor == plan.get('total_frames'), f'shot frames {cursor} != total_frames {plan.get("total_frames")}')
    return {"schema": "car-video.plan-check.v1", "structure_pass": not errors, "media_paths_checked": not structure_only,
            "total_frames": cursor, "fps": str(fps), "duration_sec": cursor / float(fps),
            "errors": errors, "warnings": warnings, "visual_review_performed": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan', type=Path)
    p.add_argument('--structure-only', action='store_true')
    args = p.parse_args()
    try:
        result = check(json.loads(args.plan.read_text(encoding='utf-8-sig')), args.plan.resolve().parent, args.structure_only)
    except (OSError, ValueError, TypeError) as exc:
        result = {"structure_pass": False, "errors": [str(exc)], "visual_review_performed": False}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['structure_pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
