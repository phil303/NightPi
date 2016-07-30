import math

def scalar_product(v1, v2):
    # how much of these two vectors are going in the same direction?
    return sum(a * b for (a, b) in zip(v1, v2))

def vector_length(v):
    return math.sqrt(sum(i**2 for i in v))

def add_vectors(v1, v2):
    return tuple(a + b for (a, b) in zip(v1, v2))

def angle_between_vectors(v1, v2):
    return math.acos(scalar_product(v1, v2) / (vector_length(v1) * vector_length(v2)))

def scale_vector(v, scale):
    return tuple(scale * a for a in v)

def normalize_vector(v):
    length = vector_length(v)
    return tuple(a / length for a in v)

# NOTE
def check_understanding(dec):
    dec = dec * math.pi / 180
    coords = (math.cos(dec), math.sin(dec))
    print("(x, y) is: %s" % (coords, ))

    y_component = scalar_product((0, 1), coords)
    print("y \"commoness\": %s" % y_component)

    scaled = scale_vector(coords, -y_component)
    print("scaled vector is: %s" % (scaled, ))

    added = add_vectors((0, 1), scaled)
    print("added vector is: %s" % (added, ))

    normalized = normalize_vector(added)
    print("normalized is: %s" % (normalized, ))
