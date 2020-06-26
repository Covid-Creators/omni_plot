# http://math.loyola.edu/~loberbro/matlab/html/colorsInMatlab.html
colors_matlab_floats = [
    (0.6350, 0.0780, 0.1840),  # Maroon
    (0.3010, 0.7450, 0.9330),  # Light Blue
    (0.4660, 0.6740, 0.1880),  # Green
    (0.4940, 0.1840, 0.5560),  # Purple
    (0.9290, 0.6940, 0.1250),  # Yellow
    (0.8500, 0.3250, 0.0980),  # Orange
    (0.0000, 0.4470, 0.7410),  # Blue
]

colors_matlab_ints = [(int(r * 255.0), int(g * 255.0), int(b * 255.0)) for (r, g, b) in colors_matlab_floats]
