def rg_linear_gradient(a, b, x):
    r = ((b - x) * 0xff) // (b - a)
    g = 0xff - r
    return (r << 16) | (g << 8)
