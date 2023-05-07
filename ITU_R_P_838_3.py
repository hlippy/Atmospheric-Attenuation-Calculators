from math import log10, cos, radians, exp

# Table 1 (from ITU-R P.838-3)
coeffs_k_H = {
    'a_j': [-5.33980, -0.35351, -0.23789, -0.94158],
    'b_j': [-0.10008, 1.26970, 0.86036, 0.64552],
    'c_j': [1.13098, 0.45400, 0.15354, 0.16817],
    'm': -0.18961,
    'c': 0.71147
}

# Table 2 (from ITU-R P.838-3)
coeffs_k_V = {
    'a_j': [-3.80595, -3.44965, -0.39902, 0.50167],
    'b_j': [0.56934, -0.22911, 0.73042, 1.07319],
    'c_j': [0.81061, 0.51059, 0.11899, 0.27195],
    'm': -0.16398,
    'c': 0.63297
}

# Table 3 (from ITU-R P.838-3)
coeffs_alpha_H = {
    'a_j': [-0.14318, 0.29591, 0.32177, -5.37610, 16.1721],
    'b_j': [1.82442, 0.77564, 0.63773, -0.96230, -3.29980],
    'c_j': [-0.55187, 0.19822, 0.13164, 1.47828, 3.43990],
    'm': 0.67849,
    'c': -1.95537
}

# Table 4 (from ITU-R P.838-3)
coeffs_alpha_V = {
    'a_j': [-0.07771, 0.56727, -0.20238, -48.2991, 48.5833],
    'b_j': [2.33840, 0.95545, 1.14520, 0.791669, 0.791459],
    'c_j': [-0.76284, 0.54039, 0.26809, 0.116226, 0.116479],
    'm': -0.053739,
    'c': 0.83433
}

def compute_k_H_or_V(f, coeffs):
    sum = 0.0
    for j in range(4):
        a_j = coeffs['a_j'][j]
        b_j = coeffs['b_j'][j]
        c_j = coeffs['c_j'][j]
        
        sum = sum + (a_j * exp(-((log10(f)-b_j)/c_j)**2))

    m_k = coeffs['m']
    c_k = coeffs['c']

    k = 10**(sum + m_k * log10(f) + c_k)
    
    return(k)

def compute_alpha_H_or_V(f, coeffs):
    sum = 0.0
    for j in range(5):
        a_j = coeffs['a_j'][j]
        b_j = coeffs['b_j'][j]
        c_j = coeffs['c_j'][j]

        sum = sum + (a_j * exp(-((log10(f)-b_j)/c_j)**2))

    m_alpha = coeffs['m']
    c_alpha = coeffs['c']

    alpha = sum + m_alpha * log10(f) + c_alpha
    
    return(alpha)

def determine_tau(polarization):
    # Determine tau from the polarization
    if polarization == 'v':
        tau = 90.0
    elif polarization == 'h':
        tau = 0.0
    else: # circular
        tau = 45.0

    return(tau)

def compute_k(f, theta, polarization, logging):
    tau = determine_tau(polarization)

    k_H = compute_k_H_or_V(f, coeffs_k_H)
    k_V = compute_k_H_or_V(f, coeffs_k_V)

    k = (k_H + k_V + (k_H - k_V) * cos(radians(theta))**2 *\
         cos(radians(2*tau))) / 2

    if logging:
        print('[ITU-R P.838-3] k_H = ' + str(k_H))
        print('[ITU-R P.838-3] k_V = ' + str(k_V))
        print('[ITU-R P.838-3] k = ' + str(k))
        
    return(k, k_H, k_V)

def compute_alpha(f, theta, polarization, k, k_H, k_V, logging):
    tau = determine_tau(polarization)

    alpha_H = compute_alpha_H_or_V(f, coeffs_alpha_H)
    alpha_V = compute_alpha_H_or_V(f, coeffs_alpha_V)
    
    alpha = (k_H*alpha_H + k_V*alpha_V +\
             (k_H*alpha_H - k_V*alpha_V) * cos(radians(theta))**2 *\
             cos(radians(2*tau))) / (2 * k)

    if logging:
        print('[ITU-R P.838-3] alpha_H = ' + str(alpha_H))
        print('[ITU-R P.838-3] alpha_V = ' + str(alpha_V))
        print('[ITU-R P.838-3] alpha = ' + str(alpha))
        
    return(alpha)

def compute_specific_attenuation_coeffs(f, theta, polarization, logging):
    k, k_H, k_V = compute_k(f, theta, polarization, logging)
    alpha = compute_alpha(f, theta, polarization, k, k_H, k_V, logging)

    return(k, alpha)
