import Rhino.Geometry as rg

# INPUTS: x=path, y=gap threshold, z=hop height, delay=steps, w=width factor

# SETTINGS
min_gap = 10.0


def offset_along(anchor, direction, amount):
    """Slide 'amount' distance from anchor along a direction vector.
    Returns the anchor unchanged if the direction has no length."""
    length = direction.Length
    if length == 0:
        return anchor
    direction.Unitize()
    clamped = min(amount, length * 0.99)   # never overshoot the segment
    return anchor + (direction * clamped)


# Only run if every input is present and the path has real segments
if x and y is not None and z is not None and delay is not None and w is not None:
    pts = list(x)

    if len(pts) < 2:
        a = pts                     # nothing to hop over
    else:
        # --- PASS 1: FIND HOP TRIGGERS ---
        hop_indices = set()
        extra_shift = int(round(max(0.0, (w - 1.0) * 0.5)))
        effective_delay = max(0, int(delay) - extra_shift)

        for i in range(len(pts) - 1):
            p1, p2 = pts[i], pts[i + 1]
            dist = p1.DistanceTo(p2)

            # gap between min_gap and y, going downward
            if min_gap < dist < y and p1.Z > p2.Z:
                target = i + effective_delay
                if target < len(pts) - 1:
                    hop_indices.add(target)

        # --- PASS 2: REBUILD PATH WITH HOPS ---
        new_points = []
        i = 0
        while i < len(pts):
            if i == len(pts) - 1:
                new_points.append(pts[i])
                break

            if i in hop_indices:
                current_pt, next_pt = pts[i], pts[i + 1]
                mid = (current_pt + next_pt) / 2.0
                peak_pt = mid + rg.Vector3d(0.0, 0.0, z)

                if w <= 1.0:
                    # CASE A: narrow hop, keep the corners
                    seg = next_pt - current_pt
                    start_jump = current_pt + (seg * (0.5 - w / 2.0))
                    end_jump   = current_pt + (seg * (0.5 + w / 2.0))
                    new_points += [current_pt, start_jump, peak_pt, end_jump]
                    i += 1
                else:
                    # CASE B: wide hop, cut corners (uses the helper twice)
                    half_extra = 0.5 * (w - 1.0) * current_pt.DistanceTo(next_pt)
                    start_jump = current_pt
                    end_jump = next_pt
                    if i > 0:
                        start_jump = offset_along(current_pt, current_pt - pts[i - 1], half_extra)
                    if i + 2 < len(pts):
                        end_jump = offset_along(next_pt, pts[i + 2] - next_pt, half_extra)
                    new_points += [start_jump, peak_pt, end_jump]
                    i += 2
            else:
                new_points.append(pts[i])
                i += 1

        a = new_points
else:
    a = []