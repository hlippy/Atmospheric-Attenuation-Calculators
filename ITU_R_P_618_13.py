from ITU_R_P_837_7 import compute_rainfall_rate
from ITU_R_P_838_3 import compute_specific_attenuation_coeffs 
from ITU_R_P_839_4 import compute_rain_height

from math import sin, cos, atan2, radians, degrees, sqrt, exp, log

base_dir = 'C:\\Users\\willi\\Documents\\nasa-project\\'

keep_going = True
logging = True

#################################################################################
#                               INPUT PARAMETERS                                #
#################################################################################

h_s   = float(input('Enter the height above mean sea level of the GS (km): '))
theta = float(input('Enter the elevation angle (degrees): '))
lat   = float(input('Enter the latitude of the GS: '))
lon   = float(input('Enger the longitude of the GS: '))
f     = float(input('Enter the frequency of the channel (GHz): '))
p     = float(input('Enter the percentage time to be exceeded (e.g. 0.1%): '))
pol   = input('Enter the polarization of the signal (V, H, C): ').lower()

R_e = 8500.0     # effective radius of the Earth

#################################################################################
# STEP 1: Determine the rain height, hR, as given in Recommendation ITU-R P.839 #
#################################################################################

if keep_going:
    sub_dir = 'R-REC-P.839-4-201309-I!!ZIP-E\\'
    h_R = compute_rain_height(base_dir + sub_dir, lat, lon, logging)
    if logging:
        print('[ITU-R P.618-13] h_R = ' + str(h_R) + ' km')
else:
    if logging:
        print('[ITU-R P.618-13] *** Step 1 not executed!')
    

#################################################################################
# STEP 2: For θ >= 5 degrees compute the slant-path length, Ls, below the rain  #
#         height from:                                                          #
#                                                                               #
#         L_s = (h_R - h_s) / sin(θ)                                            #
#                                                                               #
#         For θ < 5 degrees, the following formula is used:                     #
#                                                                               #
#         L_s = 2(h_R - h_s) / ((sin^2(θ) + 2(h_R - h_s) / R_e)^(1/2) + sin(θ)) #
#################################################################################

if keep_going:
    if h_R - h_s <= 0.0:
        A_p = 0.0
        keep_going = False
        if logging:
            print('[ITU-R P.618-13] h_R - h_s <= 0.0, so A_p = 0.0. Done.')
    else:
        if theta >= 5:
            L_s = (h_R - h_s) / sin(radians(theta))
        else:
            L_s = 2 * (h_R - h_s) /\
                  (sqrt(sin(radians(theta))**2 + 2 * (h_R - h_s) / R_e) +\
                   sin(radians(theta)))

        if logging:
            print('[ITU-R P.618-13] L_s = ' + str(L_s) + ' km')
else:
    if logging:
        print('[ITU-R P.618-13] *** Step 2 not executed!')

#################################################################################
# STEP 3: Calculate the horizontal projection, L_G, of the slant-path length    #
#         from:                                                                 #
#                                                                               #
#         L_G = L_s cos(θ)                                                      #
#################################################################################

if keep_going:
    L_G = L_s * cos(radians(theta))
    if logging:
        print('[ITU-R P.618-13] L_G = ' + str(L_G) + ' km')
else:
    if logging:
        print('[ITU-R P.618-13] *** Step 3 not executed!')

#################################################################################
# STEP 4: Obtain the rainfall rate, R_0.01, exceed for 0.01% of an average year #
#         with an integration time of 1 min). If R_0.01 = 0, the predicted rain #
#         attenuation is zero for any time percentage and the following steps   #
#         are not required.                                                     #
#################################################################################

if keep_going:
    q = input('Is rainfall rate (exceeded for 0.01% of an avg year) available? ')
    if q.lower() == 'y':
        R_0_01 = float(input('Enter the value for R_0.01: '))
    else:
        sub_dir = 'R-REC-P.837-7_Maps\\'
        R_0_01 = compute_rainfall_rate(base_dir + sub_dir, p, lat, lon, logging)

    if logging:
        print('[ITU-R P.618-13] R_0.01 = ' + str(R_0_01) + ' mm/hr')
        
    if R_0_01 == 0:
        A_p = 0.0
        keep_going = False
        if logging:
            print('[ITU-R P.618-13] R_0.01 = 0, so A_p = 0.0. Done.')
else:
    if logging:
        print('[ITU-R P.618-13] *** Step 4 not executed!')

#################################################################################
# STEP 5: Obtain the specific attenuation gamma_R, using the frequency-         #
#         dependent coefficients given in Recommendation ITU-R P.838 and the    #
#         rainfall rate, R_0.01, determined from Step 4, by using:              #
#                                                                               #
#         gamma_R = k(R_0.01)^alpha                                             #
#################################################################################

if keep_going:
    k, alpha = compute_specific_attenuation_coeffs(f, theta, pol, logging)
    gamma_R = k * R_0_01**alpha

    if logging:
        print('[ITU-R P.618-13] gamma_R = ' + str(gamma_R) + ' dB/km')
        print('[ITU-R P.618-13]   k = ' + str(k))
        print('[ITU-R P.618-13]   alpha = ' + str(alpha)) 
else:
    if logging:
        print('[ITU-R P.618-13] *** Step 5 not executed!')

#################################################################################
# STEP 6: Calculate the horizontal reduction factor, r_0_01, for 0.01% of the   #
#         time:                                                                 #
#                                                                               #
#         r_0.01 = 1 / (1 + 0.78 * sqrt((L_G*gamma_R/f) - 0.38*(1-e^(-2*L_G)))  #
#################################################################################

if keep_going:
    r_0_01 = 1.0 /\
             (1.0 + 0.78 * sqrt(L_G * gamma_R / f) - 0.38*(1 - exp(-2.0 * L_G)))

    if logging:
        print('[ITU-R P.618-13] r_0.01 = ' + str(r_0_01) + ' mm/hr')
else:
    if logging:
        print('[ITU-R P.618-13] *** Step 6 not executed!')

#################################################################################
# STEP 7: Calculate the vertical adjustment factor, v_0.01, for 0.01% of the    #
#         time:                                                                 #
#                                                                               #
#         nu_0.01 = 1 / (1 + sqrt(sin(theta)) *                                 #
#                       (31 * (1 - e^-(theta/(1+chi)) *                         #
#                       sqrt(L_R*gamma_R)/f^2 - 0.45)                           #
#################################################################################

if keep_going:
    zeta = degrees(atan2(h_R - h_s, L_G * r_0_01))

    if zeta > theta:
        L_R = L_G * r_0_01 / cos(radians(theta))
    else:
        L_R = (h_R - h_s) / sin(radians(theta))

    if abs(lat) < 36.0:
        chi = 36.0 - abs(lat)
    else:
        chi = 0.0

    nu_0_01 = 1.0 /\
              (1.0 + sqrt(sin(radians(theta))) *\
              (31.0 * (1.0 - exp(-(theta / (1.0 + chi)))) *\
              sqrt(L_R * gamma_R)/f**2 - 0.45))

    if logging:
        print('[ITU-R P.618-13] nu_0.01 = ' + str(nu_0_01))
        print('[ITU-R P.618-13]   zeta = ' + str(zeta) + ' degrees')
        print('[ITU-R P.618-13]   L_R = ' + str(L_R) + ' km')
        print('[ITU-R P.618-13]   chi = ' + str(chi) + ' degrees')
else:
    if logging:
        print('[ITU-R P.618-13] *** Step 7 not executed!')

#################################################################################
# STEP 8: The effective path length is:                                         #
#                                                                               #
#         L_E = L_R * nu_0.01                                                   #
#################################################################################

if keep_going:
    L_E = L_R * nu_0_01

    if logging:
        print('[ITU-R P.618-13] L_E = ' + str(L_E) + ' km')
else:
    if logging:
        print('[ITU-R P.618-13] *** Step 8 not executed!')

#################################################################################
# STEP 9: The predicted attenuation exceeded for 0.01% of an average year is    #
#         obtained from:                                                        #
#                                                                               #
#         A_0.01 = gamma_R * L_E                                                #
#################################################################################

if keep_going:
    A_0_01 = gamma_R * L_E

    if logging:
        print('[ITU-R P.618-13] A_0.01 = ' + str(A_0_01) + ' dB')
else:
    if logging:
        print('[ITU-R P.618-13] *** Step 9 not executed!')

#################################################################################
# STEP 10: The estimated attenuation to be exceeded for other percentages of an #
#          average year, in the range 0.001% to 5%, is determined from the      #
#          attenuation to be exceeded for 0.01% for an average year:            #
#                                                                               #
#          If p >= 1% or |lat| >= 36 degrees:                                   #
#                beta = 0                                                       #
#          If p < 1% and |lat| < 36 degrees and theta >= 25 degrees:            #
#                beta = -0.005 * (|lat| - 36)                                   #
#          Otherwise:                                                           #
#                beta = -0.005 * (|lat| - 36) + 1.8 - 4.25 * sin(theta)         #
#                                                                               #
#          A_p = A_0.01 * (p / 0.01) ^ X                                        #
#            X = -(0.655+0.033*ln(p) - 0.045*ln(A_0.01) - beta*(1-p)*sin(theta))#
#################################################################################

if keep_going:
    if p >= 1.0 or abs(lat) >= 36.0:
        beta = 0.0
    elif p < 1.0 and abs(lat) < 36.0 and theta >= 25.0:
        beta = -0.005 * (abs(lat) - 36.0)
    else:
        beta = -0.005 * (abs(lat) - 36.0) + 1.8 - 4.25 * sin(radians(theta))

    A_p = A_0_01 * (p / 0.01)**\
          -(0.655+0.033*log(p)-0.045*log(A_0_01)-beta*(1-p)*sin(radians(theta)))

    if logging:
        print('[ITU-R P.618-13] A_p = ' + str(A_p) + ' dB')
        print('[ITU-R P.618-13]   beta = ' + str(beta))
else:
    if logging:
        print('[ITU-R P.618-13] *** Step 10 not executed!')
