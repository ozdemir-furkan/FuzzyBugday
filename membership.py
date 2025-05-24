import numpy as np
import skfuzzy as fuzz

# Girdi aralıkları
# Toprak nemi: 0–100 (%)
# Azot oranı: 0–50 (ppm)
# Yağış miktarı: 0–200 (mm)
# Güneşlenme süresi: 0–12 (saat)
# Ekim zamanı uygunluğu: 0–10 (skor)

def get_input_memberships():
    x_nem = np.arange(0, 101, 1)
    x_azot = np.arange(0, 51, 1)
    x_yagis = np.arange(0, 201, 1)
    x_gunes = np.arange(0, 13, 1)
    x_ekim = np.arange(0, 11, 1)

    # Nem üyelik fonksiyonları
    nem_az = fuzz.trimf(x_nem, [0, 0, 50])
    nem_orta = fuzz.trimf(x_nem, [30, 50, 70])
    nem_yuksek = fuzz.trimf(x_nem, [50, 100, 100])

    # Azot üyelik fonksiyonları
    azot_az = fuzz.trimf(x_azot, [0, 0, 25])
    azot_orta = fuzz.trimf(x_azot, [15, 25, 35])
    azot_yuksek = fuzz.trimf(x_azot, [25, 50, 50])

    # Yağış üyelik fonksiyonları
    yagis_az = fuzz.trimf(x_yagis, [0, 0, 100])
    yagis_orta = fuzz.trimf(x_yagis, [50, 100, 150])
    yagis_cok = fuzz.trimf(x_yagis, [100, 200, 200])

    # Güneşlenme süresi
    gunes_az = fuzz.trimf(x_gunes, [0, 0, 6])
    gunes_orta = fuzz.trimf(x_gunes, [4, 6, 8])
    gunes_cok = fuzz.trimf(x_gunes, [6, 12, 12])

    # Ekim zamanı
    ekim_kotu = fuzz.trimf(x_ekim, [0, 0, 5])
    ekim_orta = fuzz.trimf(x_ekim, [3, 5, 7])
    ekim_iyi = fuzz.trimf(x_ekim, [5, 10, 10])

    return {
        'nem': (x_nem, [nem_az, nem_orta, nem_yuksek]),
        'azot': (x_azot, [azot_az, azot_orta, azot_yuksek]),
        'yagis': (x_yagis, [yagis_az, yagis_orta, yagis_cok]),
        'gunes': (x_gunes, [gunes_az, gunes_orta, gunes_cok]),
        'ekim': (x_ekim, [ekim_kotu, ekim_orta, ekim_iyi])
    }