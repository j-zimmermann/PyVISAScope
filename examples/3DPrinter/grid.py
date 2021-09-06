from numpy import arange


def get_grid():
        zmin = 0.4
        zmax = 4.4
        dz = 2
        assert zmax <= 6
        assert zmin >= 0.3
        assert zmax >= zmin + dz

        ymin = -7
        ymax = -4
        dy = 0.5
        assert ymax >= ymin + dy
        assert ymax <= -4
        assert ymin >= -11

        xmin = -7
        xmax = 7
        dx = 0.5
        assert xmax >= xmin + dx
        assert xmax <= 7
        assert xmin >= -7

        xsteps = arange(xmin, xmax + dx, dx)
        ysteps = arange(ymin, ymax + dy, dy)
        zsteps = arange(zmin, zmax + dz, dz)
        grid = []
        shift = 0
        for i in range(len(zsteps)):
            for j in range(len(ysteps)):
                for k in range(len(xsteps)):
                    if (j + shift) % 2 == 0:
                        x = xsteps[k]
                    else:
                        x = xsteps[-k - 1]
                    if i % 2 == 0:
                        y = ysteps[j]
                    else:
                        y = ysteps[-j - 1]
                    z = zsteps[i]
                    # forbidden points:
                    if abs(x) > 5 and abs(y) <= 6:
                        continue
                    grid.append([x, y, z])
            if j % 2 == 0:
                shift += 1
        return grid
