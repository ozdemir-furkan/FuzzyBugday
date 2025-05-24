import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, 
                           QPushButton, QGroupBox, QFrame, QGridLayout, QSizePolicy,
                           QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from fuzzy_rules import verim_sim, plot_membership_functions, plot_results
import numpy as np
import skfuzzy as fuzz

class ModernSpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QSpinBox {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                padding: 5px;
                min-width: 80px;
                font-size: 12pt;
            }
            QSpinBox:hover {
                border: 2px solid #3498db;
            }
            QSpinBox:focus {
                border: 2px solid #2980b9;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background-color: #f8f9fa;
                border: none;
                border-radius: 3px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e9ecef;
            }
        """)

class ModernButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12pt;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
        """)

class BugdayVerimApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buğday Verim Tahmini")
        self.setGeometry(100, 100, 1800, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 1em;
                font-weight: bold;
                background-color: white;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2980b9;
                font-size: 14pt;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 11pt;
            }
            QFrame {
                border-radius: 8px;
            }
        """)
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Sol panel container
        left_container = QWidget()
        left_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(20)
        
        # Giriş değerleri paneli
        input_panel = QGroupBox("Giriş Değerleri")
        input_layout = QVBoxLayout()
        
        # Giriş alanları için grid
        input_grid = QGridLayout()
        input_grid.setSpacing(15)
        
        # Giriş alanları
        self.inputs = {}
        
        # Nem girişi
        nem_label = QLabel("Toprak Nemi:")
        nem_unit = QLabel("(%)")
        nem_unit.setStyleSheet("color: #666; font-weight: normal;")
        self.inputs['nem'] = ModernSpinBox()
        self.inputs['nem'].setRange(0, 100)
        nem_range = QLabel("Aralık: 0-100")
        nem_range.setStyleSheet("color: #666; font-weight: normal; font-style: italic;")
        input_grid.addWidget(nem_label, 0, 0)
        input_grid.addWidget(self.inputs['nem'], 0, 1)
        input_grid.addWidget(nem_unit, 0, 2)
        input_grid.addWidget(nem_range, 0, 3)
        
        # Azot girişi
        azot_label = QLabel("Azot Seviyesi:")
        azot_unit = QLabel("(ppm)")
        azot_unit.setStyleSheet("color: #666; font-weight: normal;")
        self.inputs['azot'] = ModernSpinBox()
        self.inputs['azot'].setRange(0, 100)
        azot_range = QLabel("Aralık: 0-100")
        azot_range.setStyleSheet("color: #666; font-weight: normal; font-style: italic;")
        input_grid.addWidget(azot_label, 1, 0)
        input_grid.addWidget(self.inputs['azot'], 1, 1)
        input_grid.addWidget(azot_unit, 1, 2)
        input_grid.addWidget(azot_range, 1, 3)
        
        # Yağış girişi
        yagis_label = QLabel("Yağış Miktarı:")
        yagis_unit = QLabel("(mm)")
        yagis_unit.setStyleSheet("color: #666; font-weight: normal;")
        self.inputs['yagis'] = ModernSpinBox()
        self.inputs['yagis'].setRange(0, 200)
        yagis_range = QLabel("Aralık: 0-200")
        yagis_range.setStyleSheet("color: #666; font-weight: normal; font-style: italic;")
        input_grid.addWidget(yagis_label, 2, 0)
        input_grid.addWidget(self.inputs['yagis'], 2, 1)
        input_grid.addWidget(yagis_unit, 2, 2)
        input_grid.addWidget(yagis_range, 2, 3)
        
        # Güneşlenme girişi
        gunes_label = QLabel("Güneşlenme Süresi:")
        gunes_unit = QLabel("(saat)")
        gunes_unit.setStyleSheet("color: #666; font-weight: normal;")
        self.inputs['gunes'] = ModernSpinBox()
        self.inputs['gunes'].setRange(0, 12)
        gunes_range = QLabel("Aralık: 0-12")
        gunes_range.setStyleSheet("color: #666; font-weight: normal; font-style: italic;")
        input_grid.addWidget(gunes_label, 3, 0)
        input_grid.addWidget(self.inputs['gunes'], 3, 1)
        input_grid.addWidget(gunes_unit, 3, 2)
        input_grid.addWidget(gunes_range, 3, 3)
        
        # Ekim zamanı girişi
        ekim_label = QLabel("Ekim Zamanı Uygunluğu:")
        ekim_unit = QLabel("(puan)")
        ekim_unit.setStyleSheet("color: #666; font-weight: normal;")
        self.inputs['ekim'] = ModernSpinBox()
        self.inputs['ekim'].setRange(0, 10)
        ekim_range = QLabel("Aralık: 0-10")
        ekim_range.setStyleSheet("color: #666; font-weight: normal; font-style: italic;")
        input_grid.addWidget(ekim_label, 4, 0)
        input_grid.addWidget(self.inputs['ekim'], 4, 1)
        input_grid.addWidget(ekim_unit, 4, 2)
        input_grid.addWidget(ekim_range, 4, 3)
        
        input_layout.addLayout(input_grid)
        
        # Butonlar için container
        button_container = QVBoxLayout()
        button_container.setSpacing(10)
        
        # Hesapla butonu
        calc_button = ModernButton("Hesapla")
        calc_button.clicked.connect(self.calculate)
        button_container.addWidget(calc_button)
        
        # Üyelik fonksiyonları butonu
        mf_button = ModernButton("Üyelik Fonksiyonlarını Göster")
        mf_button.clicked.connect(self.show_membership_functions)
        button_container.addWidget(mf_button)
        
        input_layout.addLayout(button_container)
        input_panel.setLayout(input_layout)
        left_layout.addWidget(input_panel)
        
        # Sonuçlar paneli
        results_panel = QGroupBox("Sonuçlar")
        results_layout = QVBoxLayout()
        
        # Verim sonucu
        verim_frame = QFrame()
        verim_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        verim_layout = QVBoxLayout(verim_frame)
        
        self.verim_label = QLabel("Tahmini Verim: -")
        self.verim_label.setStyleSheet("font-size: 13pt;")
        self.verim_category = QLabel("Verim Kategorisi: -")
        self.verim_category.setStyleSheet("font-size: 12pt;")
        
        verim_layout.addWidget(self.verim_label)
        verim_layout.addWidget(self.verim_category)
        results_layout.addWidget(verim_frame)
        
        # Gübre sonucu
        gubre_frame = QFrame()
        gubre_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        gubre_layout = QVBoxLayout(gubre_frame)
        
        self.gubre_label = QLabel("Gübre İhtiyacı: -")
        self.gubre_label.setStyleSheet("font-size: 13pt;")
        self.gubre_category = QLabel("Gübre Kategorisi: -")
        self.gubre_category.setStyleSheet("font-size: 12pt;")
        
        gubre_layout.addWidget(self.gubre_label)
        gubre_layout.addWidget(self.gubre_category)
        results_layout.addWidget(gubre_frame)
        
        results_panel.setLayout(results_layout)
        left_layout.addWidget(results_panel)
        
        main_layout.addWidget(left_container)
        
        # Sağ panel - Grafikler
        right_panel = QGroupBox("Grafikler")
        right_layout = QVBoxLayout()
        
        # Tab widget oluştur
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #3498db;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #f8f9fa;
                border: 2px solid #3498db;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: none;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)
        
        # Sonuçlar tab'ı
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        
        # Verim grafiği için canvas
        self.verim_figure = plt.figure(figsize=(8, 5))
        self.verim_canvas = FigureCanvas(self.verim_figure)
        results_layout.addWidget(self.verim_canvas)
        
        # Gübre grafiği için canvas
        self.gubre_figure = plt.figure(figsize=(8, 5))
        self.gubre_canvas = FigureCanvas(self.gubre_figure)
        results_layout.addWidget(self.gubre_canvas)
        
        # Üyelik fonksiyonları tab'ı
        membership_tab = QWidget()
        membership_layout = QVBoxLayout(membership_tab)
        
        # Üyelik fonksiyonları için tek bir figure oluştur
        self.membership_figure = plt.figure(figsize=(12, 10))
        self.membership_canvas = FigureCanvas(self.membership_figure)
        membership_layout.addWidget(self.membership_canvas)
        
        # Tab'ları ekle
        self.tab_widget.addTab(results_tab, "Sonuç Grafikleri")
        self.tab_widget.addTab(membership_tab, "Üyelik Fonksiyonları")
        
        right_layout.addWidget(self.tab_widget)
        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel)
        
        # Panel oranlarını ayarla
        main_layout.setStretch(0, 4)  # Sol panel
        main_layout.setStretch(1, 6)  # Sağ panel
    
    def calculate(self):
        # Giriş değerlerini al
        input_values = {
            'nem': self.inputs['nem'].value(),
            'azot': self.inputs['azot'].value(),
            'yagis': self.inputs['yagis'].value(),
            'gunes': self.inputs['gunes'].value(),
            'ekim': self.inputs['ekim'].value()
        }
        
        # Bulanık çıkarım sistemini çalıştır
        for key, value in input_values.items():
            verim_sim.input[key] = value
        
        verim_sim.compute()
        
        # Sonuçları al
        output_values = {
            'verim': verim_sim.output['verim'],
            'gubre': verim_sim.output['gubre']
        }
        
        # Sonuçları göster
        self.verim_label.setText(f"Tahmini Verim: {output_values['verim']:.1f} kg/da")
        self.gubre_label.setText(f"Gübre İhtiyacı: {output_values['gubre']:.1f}/10")
        
        # Verim kategorisini belirle
        verim_value = output_values['verim']
        if verim_value < 200:
            verim_category = "Çok Düşük"
            color = "#e74c3c"  # Kırmızı
        elif verim_value < 400:
            verim_category = "Düşük"
            color = "#e67e22"  # Turuncu
        elif verim_value < 600:
            verim_category = "Normal"
            color = "#f1c40f"  # Sarı
        elif verim_value < 800:
            verim_category = "Yüksek"
            color = "#2ecc71"  # Yeşil
        else:
            verim_category = "Çok Yüksek"
            color = "#27ae60"  # Koyu yeşil
        
        self.verim_category.setText(f"Verim Kategorisi: {verim_category}")
        self.verim_category.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Gübre kategorisini belirle
        gubre_value = output_values['gubre']
        if gubre_value < 2:
            gubre_category = "Gereksiz"
            gubre_color = "#27ae60"  # Koyu yeşil
        elif gubre_value < 4:
            gubre_category = "Az Gerekli"
            gubre_color = "#2ecc71"  # Yeşil
        elif gubre_value < 6:
            gubre_category = "Orta Düzeyde Gerekli"
            gubre_color = "#f1c40f"  # Sarı
        elif gubre_value < 8:
            gubre_category = "Gerekli"
            gubre_color = "#e67e22"  # Turuncu
        else:
            gubre_category = "Çok Gerekli"
            gubre_color = "#e74c3c"  # Kırmızı
        
        self.gubre_category.setText(f"Gübre Kategorisi: {gubre_category}")
        self.gubre_category.setStyleSheet(f"color: {gubre_color}; font-weight: bold;")
        
        # Grafikleri temizle
        self.verim_figure.clear()
        self.gubre_figure.clear()
        
        # Verim grafiği
        ax_verim = self.verim_figure.add_subplot(111)
        x_verim = np.arange(0, 1001, 1)
        ax_verim.plot(x_verim, fuzz.trimf(x_verim, [0, 0, 200]), 'b', label='Çok Az')
        ax_verim.plot(x_verim, fuzz.trimf(x_verim, [100, 250, 400]), 'orange', label='Az')
        ax_verim.plot(x_verim, fuzz.trimf(x_verim, [300, 500, 700]), 'g', label='Normal')
        ax_verim.plot(x_verim, fuzz.trimf(x_verim, [600, 800, 900]), 'r', label='Fazla')
        ax_verim.plot(x_verim, fuzz.trimf(x_verim, [800, 1000, 1000]), 'purple', label='Çok Fazla')
        ax_verim.vlines(x=verim_value, ymin=0, ymax=1, colors='r', linestyles=':',
                       label=f"Tahmini Verim: {verim_value:.1f} kg/da")
        ax_verim.set_xlabel('Verim (kg/da)')
        ax_verim.set_ylabel('Üyelik Derecesi')
        ax_verim.set_title('Verim Tahmini')
        ax_verim.legend(loc='upper left')
        ax_verim.grid(True)
        self.verim_figure.tight_layout()
        
        # Gübre grafiği
        ax_gubre = self.gubre_figure.add_subplot(111)
        x_gubre = np.arange(0, 11, 0.1)
        ax_gubre.plot(x_gubre, fuzz.trimf(x_gubre, [0, 0, 2]), 'b', label='Gereksiz')
        ax_gubre.plot(x_gubre, fuzz.trimf(x_gubre, [1, 3, 5]), 'orange', label='Az Gerekli')
        ax_gubre.plot(x_gubre, fuzz.trimf(x_gubre, [4, 5, 6]), 'g', label='Orta')
        ax_gubre.plot(x_gubre, fuzz.trimf(x_gubre, [5, 7, 9]), 'r', label='Gerekli')
        ax_gubre.plot(x_gubre, fuzz.trimf(x_gubre, [8, 10, 10]), 'purple', label='Çok Gerekli')
        ax_gubre.vlines(x=gubre_value, ymin=0, ymax=1, colors='r', linestyles=':',
                       label=f"Gübre İhtiyacı: {gubre_value:.1f}/10")
        ax_gubre.set_xlabel('Gübre İhtiyacı')
        ax_gubre.set_ylabel('Üyelik Derecesi')
        ax_gubre.set_title('Gübre İhtiyacı')
        ax_gubre.legend(loc='upper left')
        ax_gubre.grid(True)
        ax_gubre.set_xlim(0, 10)
        self.gubre_figure.tight_layout()
        
        # Canvas'ları güncelle
        self.verim_canvas.draw()
        self.gubre_canvas.draw()
        
        # Sonuç grafiklerini kaydet
        try:
            import os
            if not os.path.exists('images'):
                os.makedirs('images')
            
            # Verim grafiğini kaydet
            self.verim_figure.savefig('images/verim_sonuc.png', 
                                    bbox_inches='tight', 
                                    dpi=300,
                                    facecolor='white',
                                    edgecolor='none')
            
            # Gübre grafiğini kaydet
            self.gubre_figure.savefig('images/gubre_sonuc.png',
                                    bbox_inches='tight',
                                    dpi=300,
                                    facecolor='white',
                                    edgecolor='none')
        except Exception as e:
            print(f"Grafik kaydedilirken hata oluştu: {e}")
    
    def show_membership_functions(self):
        """Üyelik fonksiyonlarını tab içinde göster ve kaydet"""
        # Figure'ı temizle
        self.membership_figure.clear()
        
        # images klasörünü kontrol et ve oluştur
        import os
        if not os.path.exists('images'):
            os.makedirs('images')
        
        # Değişkenlerin aralık ve etiketlerini tanımla
        variables = [
            ('nem', 'Toprak Nemi (%)', 
             [(0, 0, 50, 'Az'),
              (30, 50, 70, 'Orta'),
              (50, 100, 100, 'Yüksek')]),
            
            ('azot', 'Azot Seviyesi (ppm)', 
             [(0, 0, 50, 'Az'),
              (30, 50, 70, 'Orta'),
              (50, 100, 100, 'Yüksek')]),
            
            ('yagis', 'Yağış Miktarı (mm)', 
             [(0, 0, 100, 'Az'),
              (50, 100, 150, 'Orta'),
              (100, 200, 200, 'Çok')]),
            
            ('gunes', 'Güneşlenme Süresi (saat)', 
             [(0, 0, 6, 'Az'),
              (4, 6, 8, 'Orta'),
              (6, 12, 12, 'Çok')]),
            
            ('ekim', 'Ekim Zamanı Uygunluğu', 
             [(0, 0, 5, 'Kötü'),
              (3, 5, 7, 'Orta'),
              (5, 10, 10, 'İyi')]),
            
            ('verim', 'Verim Tahmini (kg/da)', 
             [(0, 0, 200, 'Çok Az'),
              (100, 250, 400, 'Az'),
              (300, 500, 700, 'Normal'),
              (600, 800, 900, 'Fazla'),
              (800, 1000, 1000, 'Çok Fazla')]),
            
            ('gubre', 'Gübre İhtiyacı', 
             [(0, 0, 2, 'Gereksiz'),
              (1, 3, 5, 'Az Gerekli'),
              (4, 5, 6, 'Orta'),
              (5, 7, 9, 'Gerekli'),
              (8, 10, 10, 'Çok Gerekli')])
        ]
        
        # Her bir değişken için subplot oluştur ve kaydet
        for i, (name, title, mfs) in enumerate(variables, 1):
            # Ana figure için subplot
            ax = self.membership_figure.add_subplot(4, 2, i)
            
            # Ayrı bir figure oluştur (kaydetmek için)
            save_fig = plt.figure(figsize=(10, 6))
            save_ax = save_fig.add_subplot(111)
            
            # Her bir üyelik fonksiyonunu çiz
            for a, b, c, label in mfs:
                if name == 'gubre':
                    x = np.arange(0, 11, 0.1)
                elif name == 'verim':
                    x = np.arange(0, 1001, 1)
                elif name == 'yagis':
                    x = np.arange(0, 201, 1)
                elif name == 'gunes':
                    x = np.arange(0, 13, 1)
                elif name == 'ekim':
                    x = np.arange(0, 11, 0.1)
                else:
                    x = np.arange(0, 101, 1)
                
                y = fuzz.trimf(x, [a, b, c])
                # Her iki figure'a da çiz
                ax.plot(x, y, label=label)
                save_ax.plot(x, y, label=label)
            
            # Ana figure için grafik ayarları
            ax.set_title(title)
            ax.set_xlabel(title)
            ax.set_ylabel('Üyelik Derecesi')
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            ax.grid(True)
            
            # Kaydetme figure'ı için grafik ayarları
            save_ax.set_title(title)
            save_ax.set_xlabel(title)
            save_ax.set_ylabel('Üyelik Derecesi')
            save_ax.legend(loc='center right')
            save_ax.grid(True)
            
            # Eksen sınırlarını ayarla
            if name == 'ekim':
                ax.set_xlim(0, 10)
                save_ax.set_xlim(0, 10)
            elif name == 'gunes':
                ax.set_xlim(0, 12)
                ax.set_xticks(range(0, 13, 2))
                save_ax.set_xlim(0, 12)
                save_ax.set_xticks(range(0, 13, 2))
            elif name == 'gubre':
                ax.set_xlim(0, 10)
                save_ax.set_xlim(0, 10)
            
            # Grafiği kaydet
            save_fig.tight_layout()
            save_fig.savefig(f'images/membership_{i}.png', 
                           bbox_inches='tight', 
                           dpi=300,
                           facecolor='white',
                           edgecolor='none')
            plt.close(save_fig)  # Belleği temizle
        
        # Ana figure için son ayarlar
        self.membership_figure.tight_layout()
        
        # Tüm üyelik fonksiyonlarını tek bir resimde kaydet
        self.membership_figure.savefig('images/uyelik_fonksiyonlari.png',
                                     bbox_inches='tight',
                                     dpi=300,
                                     facecolor='white',
                                     edgecolor='none')
        
        # Canvas'ı güncelle
        self.membership_canvas.draw()
        
        # Tab'ı üyelik fonksiyonları tab'ına geçir
        self.tab_widget.setCurrentIndex(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BugdayVerimApp()
    window.show()
    sys.exit(app.exec_()) 