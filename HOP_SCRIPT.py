import rhinoscriptsyntax as rs
import Rhino.Geometry as rg

# INPUTS (GhPython):
# x     = Polyline (or list of points)
# y     = Search Length (gap threshold)
# z     = Push value (vertical offset, negative for down)
# delay = Integer (steps to wait from detected gap)
# w     = Width factor (1.0 = gap size, >1.0 = cut corners)

# SETTINGS
min_gap = 10.0
hop_indices = set()
delay=u
if x and y is not None and z is not None and delay is not None and w is not None:
    pts = list(x)

    # --- PASS 1: FIND HOP TRIGGERS ---
    for i in range(len(pts) - 1):
        p1 = pts[i]
        p2 = pts[i + 1]
        dist = p1.DistanceTo(p2)

        # Logic: gap between min_gap and y, going downward
        if dist > min_gap and dist < y and p1.Z > p2.Z:
            # Make delay depend on hop width so wide hops start earlier
            extra_shift = int(round(max(0.0, (w - 1.0) * 0.5)))
            effective_delay = max(0, int(delay) - extra_shift)

            target_index = i + effective_delay
            if target_index < len(pts) - 1:
                hop_indices.add(target_index)

    # --- PASS 2: REBUILD PATH WITH HOPS ---
    new_points = []
    i = 0

    while i < len(pts):
        # If we are at the last point, add and stop
        if i == len(pts) - 1:
            new_points.append(pts[i])
            break

        # Check if this index should start a hop
        if i in hop_indices:
            current_pt = pts[i]
            next_pt = pts[i + 1]

            # Peak point is in the middle, offset in Z by z
            mid = (current_pt + next_pt) / 2.0
            peak_pt = mid + rg.Vector3d(0.0, 0.0, z)

            if w <= 1.0:
                # CASE A: Narrow jump inside the gap, keep corners
                segment_vec = next_pt - current_pt
                t1 = 0.5 - (w / 2.0)
                t2 = 0.5 + (w / 2.0)

                start_jump = current_pt + (segment_vec * t1)
                end_jump = current_pt + (segment_vec * t2)

                new_points.append(current_pt)
                new_points.append(start_jump)
                new_points.append(peak_pt)
                new_points.append(end_jump)

                # Next loop iteration will handle next_pt
                i += 1

            else:
                # CASE B: Wide jump, cut corners but do not backtrack

                gap_len = current_pt.DistanceTo(next_pt)
                half_extra = 0.5 * (w - 1.0) * gap_len

                # Start of jump, pull back along previous segment, clamped
                if i > 0:
                    prev_pt = pts[i - 1]
                    vec_back = current_pt - prev_pt
                    prev_len = vec_back.Length

                    if prev_len > 0:
                        vec_back.Unitize()
                        start_offset = min(half_extra, prev_len * 0.99)
                        start_jump = current_pt - (vec_back * start_offset)
                    else:
                        start_jump = current_pt
                else:
                    start_jump = current_pt

                # End of jump, push forward along next segment, clamped
                if i + 2 < len(pts):
                    next_next_pt = pts[i + 2]
                    vec_fwd = next_next_pt - next_pt
                    next_len = vec_fwd.Length

                    if next_len > 0:
                        vec_fwd.Unitize()
                        end_offset = min(half_extra, next_len * 0.99)
                        end_jump = next_pt + (vec_fwd * end_offset)
                    else:
                        end_jump = next_pt
                else:
                    end_jump = next_pt

                # Add hop points, replacing current_pt and next_pt
                new_points.append(start_jump)
                new_points.append(peak_pt)
                new_points.append(end_jump)

                # Consume current_pt and next_pt
                i += 2

        else:
            # Normal point, just keep it
            new_points.append(pts[i])
            i += 1

    a = new_points

else:
    a = []