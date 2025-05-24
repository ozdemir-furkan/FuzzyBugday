import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# Girişler
nem = ctrl.Antecedent(np.arange(0, 101, 1), 'nem')
azot = ctrl.Antecedent(np.arange(0, 101, 1), 'azot')  # 0-100 ppm arası
yagis = ctrl.Antecedent(np.arange(0, 201, 1), 'yagis')
gunes = ctrl.Antecedent(np.arange(0, 13, 1), 'gunes')
ekim = ctrl.Antecedent(np.arange(0, 11, 1), 'ekim')

# Çıkışlar
verim = ctrl.Consequent(np.arange(0, 1001, 1), 'verim')
gubre = ctrl.Consequent(np.arange(0, 11, 1), 'gubre')

# --- Girdi üyelik fonksiyonları ---
nem['az'] = fuzz.trimf(nem.universe, [0, 0, 50])
nem['orta'] = fuzz.trimf(nem.universe, [30, 50, 70])
nem['yuksek'] = fuzz.trimf(nem.universe, [50, 100, 100])

azot['az'] = fuzz.trimf(azot.universe, [0, 0, 50])
azot['orta'] = fuzz.trimf(azot.universe, [30, 50, 70])
azot['yuksek'] = fuzz.trimf(azot.universe, [50, 100, 100])

yagis['az'] = fuzz.trimf(yagis.universe, [0, 0, 100])
yagis['orta'] = fuzz.trimf(yagis.universe, [50, 100, 150])
yagis['cok'] = fuzz.trimf(yagis.universe, [100, 200, 200])

gunes['az'] = fuzz.trimf(gunes.universe, [0, 0, 6])
gunes['orta'] = fuzz.trimf(gunes.universe, [4, 6, 8])
gunes['cok'] = fuzz.trimf(gunes.universe, [6, 12, 12])

ekim['kotu'] = fuzz.trimf(ekim.universe, [0, 0, 5])
ekim['orta'] = fuzz.trimf(ekim.universe, [3, 5, 7])
ekim['iyi'] = fuzz.trimf(ekim.universe, [5, 10, 10])

# --- Çıkış üyelik fonksiyonları ---
verim['cok_az'] = fuzz.trimf(verim.universe, [0, 0, 200])
verim['az'] = fuzz.trimf(verim.universe, [100, 250, 400])
verim['normal'] = fuzz.trimf(verim.universe, [300, 500, 700])
verim['fazla'] = fuzz.trimf(verim.universe, [600, 800, 900])
verim['cok_fazla'] = fuzz.trimf(verim.universe, [800, 1000, 1000])

gubre['gereksiz'] = fuzz.trimf(gubre.universe, [0, 0, 2])
gubre['az_gerekli'] = fuzz.trimf(gubre.universe, [1, 3, 5])
gubre['orta'] = fuzz.trimf(gubre.universe, [4, 5, 6])
gubre['gerekli'] = fuzz.trimf(gubre.universe, [5, 7, 9])
gubre['cok_gerekli'] = fuzz.trimf(gubre.universe, [8, 10, 10])

# --- Kurallar ---
rules = [
    # Temel verim kuralları
    ctrl.Rule(nem['az'] & azot['az'], verim['cok_az']),
    ctrl.Rule(nem['az'] & azot['orta'], verim['az']),
    ctrl.Rule(nem['az'] & azot['yuksek'], verim['normal']),
    
    ctrl.Rule(nem['orta'] & azot['az'], verim['az']),
    ctrl.Rule(nem['orta'] & azot['orta'], verim['normal']),
    ctrl.Rule(nem['orta'] & azot['yuksek'], verim['fazla']),
    
    ctrl.Rule(nem['yuksek'] & azot['az'], verim['normal']),
    ctrl.Rule(nem['yuksek'] & azot['orta'], verim['fazla']),
    ctrl.Rule(nem['yuksek'] & azot['yuksek'], verim['cok_fazla']),
    
    # Yağış etkileri
    ctrl.Rule(yagis['az'] & nem['az'], verim['cok_az']),
    ctrl.Rule(yagis['orta'] & nem['orta'], verim['normal']),
    ctrl.Rule(yagis['cok'] & nem['yuksek'], verim['fazla']),
    
    # Güneş etkileri
    ctrl.Rule(gunes['az'] & nem['yuksek'], verim['normal']),
    ctrl.Rule(gunes['orta'] & nem['orta'], verim['normal']),
    ctrl.Rule(gunes['cok'] & nem['az'], verim['az']),
    
    # Ekim zamanı etkileri
    ctrl.Rule(ekim['kotu'], verim['az']),
    ctrl.Rule(ekim['orta'], verim['normal']),
    ctrl.Rule(ekim['iyi'], verim['fazla']),
    
    # İdeal koşullar
    ctrl.Rule(nem['orta'] & azot['yuksek'] & yagis['orta'] & gunes['orta'] & ekim['iyi'], verim['cok_fazla']),
    
    # Gübre kuralları - Yeniden düzenlendi
    ctrl.Rule(azot['az'], gubre['cok_gerekli']),
    ctrl.Rule(azot['orta'] & verim['cok_az'], gubre['cok_gerekli']),
    ctrl.Rule(azot['orta'] & verim['az'], gubre['gerekli']),
    ctrl.Rule(azot['orta'] & verim['normal'], gubre['orta']),
    ctrl.Rule(azot['orta'] & (verim['fazla'] | verim['cok_fazla']), gubre['az_gerekli']),
    ctrl.Rule(azot['yuksek'] & (verim['cok_az'] | verim['az']), gubre['gerekli']),
    ctrl.Rule(azot['yuksek'] & verim['normal'], gubre['az_gerekli']),
    ctrl.Rule(azot['yuksek'] & (verim['fazla'] | verim['cok_fazla']), gubre['gereksiz']),
    
    # Nem ve yağış durumuna göre gübre ihtiyacı
    ctrl.Rule(nem['yuksek'] & yagis['cok'], gubre['gereksiz']),
    ctrl.Rule(nem['az'] & yagis['az'], gubre['cok_gerekli']),
    
    # Nem-azot kombinasyonları için gübre kuralları
    ctrl.Rule(nem['orta'] & azot['az'], gubre['gerekli']),
    ctrl.Rule(nem['orta'] & azot['orta'], gubre['orta']),
    ctrl.Rule(nem['orta'] & azot['yuksek'], gubre['az_gerekli']),
    
    ctrl.Rule(nem['yuksek'] & azot['az'], gubre['gerekli']),
    ctrl.Rule(nem['yuksek'] & azot['orta'], gubre['az_gerekli']),
    ctrl.Rule(nem['yuksek'] & azot['yuksek'], gubre['gereksiz'])
]

# Kontrol sistemini oluştur
verim_ctrl = ctrl.ControlSystem(rules)
verim_sim = ctrl.ControlSystemSimulation(verim_ctrl)

def plot_membership_functions():
    """Üyelik fonksiyonlarını görselleştir"""
    
    plt.close('all')  # Önceki tüm grafikleri kapat
    
    # Değişkenlerin aralık ve etiketlerini tanımla
    variables = [
        (nem, 'Toprak Nemi (%)', 
         {'az': '0-30\nAz', 'orta': '30-70\nOrta', 'yuksek': '70-100\nYüksek'}),
        
        (azot, 'Azot Seviyesi (ppm)',
         {'az': '0-30\nAz', 'orta': '30-70\nOrta', 'yuksek': '70-100\nYüksek'}),
        
        (yagis, 'Yağış Miktarı (mm)',
         {'az': '0-50\nAz', 'orta': '50-150\nOrta', 'cok': '150-200\nÇok'}),
        
        (gunes, 'Güneşlenme Süresi (saat)',
         {'az': '0-4\nAz', 'orta': '4-8\nOrta', 'cok': '8-12\nÇok'}),
        
        (ekim, 'Ekim Zamanı Uygunluğu',
         {'kotu': '0-3\nKötü', 'orta': '3-7\nOrta', 'iyi': '7-10\nİyi'}),
        
        (verim, 'Verim Tahmini (kg/da)',
         {'cok_az': '0-200\nÇok Az', 'az': '200-400\nAz', 'normal': '400-600\nNormal',
          'fazla': '600-800\nFazla', 'cok_fazla': '800-1000\nÇok Fazla'}),
         
        (gubre, 'Gübre İhtiyacı',
         {'gereksiz': '0-2\nGereksiz', 'az_gerekli': '2-4\nAz Gerekli', 'orta': '4-6\nOrta',
          'gerekli': '6-8\nGerekli', 'cok_gerekli': '8-10\nÇok Gerekli'})
    ]
    
    # Her bir değişken için ayrı grafik çiz
    for i, (var, title, labels) in enumerate(variables):
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Üyelik fonksiyonlarını manuel olarak çiz
        x = np.linspace(var.universe.min(), var.universe.max(), 1000)
        for term_name, mf in var.terms.items():
            y = fuzz.interp_membership(var.universe, mf.mf, x)
            ax.plot(x, y, label=labels[term_name].split('\n')[1])
        
        # Grafik ayarları
        ax.set_title(title)
        ax.set_xlabel(title)
        ax.set_ylabel('Üyelik Derecesi')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True)
        plt.tight_layout()
        
        # Pencere başlığını ayarla
        plt.get_current_fig_manager().set_window_title(title)
        
        # Grafiği kaydet
        plt.savefig(f'membership_{i+1}.png', bbox_inches='tight', dpi=300)
    
    # Grafikleri göster
    plt.show(block=False)

def plot_results(input_values, output_values):
    """Girdi ve çıktı değerlerini görselleştir"""
    
    # Verim sonucu - Figure 16 olarak ayarla
    fig_verim = plt.figure(16, figsize=(10, 6))
    ax_verim = fig_verim.add_subplot(111)
    
    # Verim üyelik fonksiyonlarını çiz
    x_verim = np.arange(0, 1001, 1)
    ax_verim.plot(x_verim, fuzz.trimf(x_verim, [0, 0, 200]), 'b', label='Çok Az')
    ax_verim.plot(x_verim, fuzz.trimf(x_verim, [100, 250, 400]), 'orange', label='Az')
    ax_verim.plot(x_verim, fuzz.trimf(x_verim, [300, 500, 700]), 'g', label='Normal')
    ax_verim.plot(x_verim, fuzz.trimf(x_verim, [600, 800, 900]), 'r', label='Fazla')
    ax_verim.plot(x_verim, fuzz.trimf(x_verim, [800, 1000, 1000]), 'purple', label='Çok Fazla')
    
    # Verim değerini noktalı çizgi olarak göster
    verim_value = output_values['verim']
    ax_verim.vlines(x=verim_value, ymin=0, ymax=1, colors='r', linestyles=':',
                    label=f"Tahmini Verim: {verim_value:.1f} kg/da\n({get_verim_category(verim_value)})")
    
    # Verim etiketlerini ayarla
    ax_verim.set_xlabel('Verim (kg/da)')
    ax_verim.set_ylabel('Üyelik Derecesi')
    ax_verim.set_title('Verim Tahmini')
    ax_verim.legend(loc='upper left')
    ax_verim.grid(True)
    plt.figure(16)
    plt.tight_layout()
    
    # Gübre sonucu - Figure 18 olarak ayarla
    fig_gubre = plt.figure(18, figsize=(10, 6))
    ax_gubre = fig_gubre.add_subplot(111)
    
    # Gübre üyelik fonksiyonlarını çiz
    x_gubre = np.arange(0, 11, 0.1)
    ax_gubre.plot(x_gubre, fuzz.trimf(x_gubre, [0, 0, 2]), 'b', label='Gereksiz')
    ax_gubre.plot(x_gubre, fuzz.trimf(x_gubre, [1, 3, 5]), 'orange', label='Az Gerekli')
    ax_gubre.plot(x_gubre, fuzz.trimf(x_gubre, [4, 5, 6]), 'g', label='Orta')
    ax_gubre.plot(x_gubre, fuzz.trimf(x_gubre, [5, 7, 9]), 'r', label='Gerekli')
    ax_gubre.plot(x_gubre, fuzz.trimf(x_gubre, [8, 10, 10]), 'purple', label='Çok Gerekli')
    
    # Gübre değerini noktalı çizgi olarak göster
    gubre_value = output_values['gubre']
    ax_gubre.vlines(x=gubre_value, ymin=0, ymax=1, colors='r', linestyles=':',
                    label=f"Gübre İhtiyacı: {gubre_value:.1f}/10")
    
    # Gübre etiketlerini ayarla
    ax_gubre.set_xlabel('Gübre İhtiyacı')
    ax_gubre.set_ylabel('Üyelik Derecesi')
    ax_gubre.set_title('Gübre İhtiyacı')
    ax_gubre.legend(loc='upper left')
    ax_gubre.grid(True)
    
    # X eksenini 0-10 arasında sınırla
    ax_gubre.set_xlim(0, 10)
    
    plt.figure(18)
    plt.tight_layout()

def get_verim_category(verim_value):
    """Verim değerinin hangi kategoriye düştüğünü belirle"""
    membership_degrees = {}
    
    for term in verim.terms:
        degree = fuzz.interp_membership(verim.universe, verim[term].mf, verim_value)
        membership_degrees[term] = degree
    
    # En yüksek üyelik derecesine sahip kategoriyi bul
    max_category = max(membership_degrees.items(), key=lambda x: x[1])[0]
    
    # Kategori isimlerini Türkçeleştir
    category_names = {
        'cok_az': 'Çok Az',
        'az': 'Az',
        'normal': 'Normal',
        'fazla': 'Fazla',
        'cok_fazla': 'Çok Fazla'
    }
    
    return category_names[max_category]