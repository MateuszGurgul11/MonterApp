import io
import base64
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import streamlit as st

class DoorDiagram(Flowable):
    """Klasa do rysowania diagramów drzwi"""
    
    def __init__(self, door_config, width=6*cm, height=4*cm):
        Flowable.__init__(self)
        self.door_config = door_config
        self.width = width
        self.height = height
    
    def draw(self):
        """Rysuje diagram drzwi"""
        canvas = self.canv
        
        # Wymiary diagramu
        door_width = self.width * 0.6
        door_height = self.height * 0.7
        x_center = self.width / 2
        y_center = self.height / 2
        
        # Pozycja prostokąta drzwi
        door_x = x_center - door_width/2
        door_y = y_center - door_height/2
        
        # Rysuj ramę drzwi (ościeżnica)
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(2)
        canvas.rect(door_x, door_y, door_width, door_height)
        
        # Wypełnienie drzwi
        canvas.setFillColor(colors.HexColor('#F0F0F0'))
        canvas.rect(door_x + 2, door_y + 2, door_width - 4, door_height - 4, fill=1)
        
        # Rysuj klamkę
        handle_size = 3
        if self.door_config.get('lewe_przyl') or self.door_config.get('lewe_odwr'):
            # Klamka po lewej
            handle_x = door_x + door_width - 8
        else:
            # Klamka po prawej
            handle_x = door_x + 8
            
        handle_y = y_center
        canvas.setFillColor(colors.HexColor('#D4AF37'))  # Złoty kolor klamki
        canvas.circle(handle_x, handle_y, handle_size, fill=1)
        
        # Rysuj łuk otwierania
        canvas.setStrokeColor(colors.HexColor('#FF6B6B'))
        canvas.setLineWidth(2)
        canvas.setDash([3, 3])  # Linia przerywana
        
        # Określ kierunek otwierania
        if self.door_config.get('lewe_przyl'):
            # Lewe przylgowe
            start_angle = 0
            end_angle = 90
            arc_x = door_x
            arc_y = door_y
            self.draw_arc_with_arrow(canvas, arc_x, arc_y, door_width, start_angle, end_angle)
            self.add_label(canvas, "LEWE\nPRZYLGOWE", door_x - 20, y_center)
            
        elif self.door_config.get('prawe_przyl'):
            # Prawe przylgowe
            start_angle = 90
            end_angle = 180
            arc_x = door_x + door_width
            arc_y = door_y
            self.draw_arc_with_arrow(canvas, arc_x, arc_y, door_width, start_angle, end_angle)
            self.add_label(canvas, "PRAWE\nPRZYLGOWE", door_x + door_width + 10, y_center)
            
        elif self.door_config.get('lewe_odwr'):
            # Lewe odwrotna przylga
            start_angle = 270
            end_angle = 360
            arc_x = door_x
            arc_y = door_y + door_height
            self.draw_arc_with_arrow(canvas, arc_x, arc_y, door_width, start_angle, end_angle)
            self.add_label(canvas, "LEWE\nODWROTNA", door_x - 20, y_center)
            
        elif self.door_config.get('prawe_odwr'):
            # Prawe odwrotna przylga
            start_angle = 180
            end_angle = 270
            arc_x = door_x + door_width
            arc_y = door_y + door_height
            self.draw_arc_with_arrow(canvas, arc_x, arc_y, door_width, start_angle, end_angle)
            self.add_label(canvas, "PRAWE\nODWROTNA", door_x + door_width + 10, y_center)
        
        # Reset ustawień
        canvas.setDash([])
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(1)
    
    def draw_arc_with_arrow(self, canvas, x, y, radius, start_angle, end_angle):
        """Rysuje łuk z strzałką"""
        import math
        
        # Rysuj łuk
        extent = end_angle - start_angle
        canvas.arc(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            start_angle,
            extent,
        )
        
        # Dodaj strzałkę na końcu łuku
        end_angle_rad = math.radians(end_angle)
        arrow_x = x + radius * 0.8 * math.cos(end_angle_rad)
        arrow_y = y + radius * 0.8 * math.sin(end_angle_rad)
        
        # Rysuj strzałkę
        arrow_size = 5
        canvas.setFillColor(colors.HexColor('#FF6B6B'))
        
        # Kierunek strzałki
        arrow_angle = end_angle_rad + math.pi/6
        ax1 = arrow_x + arrow_size * math.cos(arrow_angle)
        ay1 = arrow_y + arrow_size * math.sin(arrow_angle)
        
        arrow_angle = end_angle_rad - math.pi/6
        ax2 = arrow_x + arrow_size * math.cos(arrow_angle)
        ay2 = arrow_y + arrow_size * math.sin(arrow_angle)
        
        # Narysuj trójkąt strzałki
        path = canvas.beginPath()
        path.moveTo(arrow_x, arrow_y)
        path.lineTo(ax1, ay1)
        path.lineTo(ax2, ay2)
        path.close()
        canvas.drawPath(path, stroke=1, fill=1)
    
    def add_label(self, canvas, text, x, y):
        """Dodaje etykietę z opisem"""
        canvas.setFillColor(colors.HexColor('#2E4057'))
        canvas.setFont('Helvetica-Bold', 8)
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            canvas.drawString(x, y - i * 10, line)

class DoorPhotoWithLabels(Flowable):
    """Flowable rysujący zdjęcie drzwi wraz z podpisami: nad, pod i szerokość na środku."""

    def __init__(self, image_path: str, top_label: str | None, bottom_label: str | None, center_width_text: str | None, max_width: float = 3 * cm):
        super().__init__()
        self.image_path = image_path
        self.top_label = top_label or ""
        self.bottom_label = bottom_label or ""
        self.center_width_text = center_width_text or ""

        # Wczytaj rozmiar obrazu i wylicz wymiary rysowania
        reader = ImageReader(image_path)
        img_width_px, img_height_px = reader.getSize()
        scale = min(max_width / float(img_width_px), 1.0)
        self.draw_width = float(img_width_px) * scale
        self.draw_height = float(img_height_px) * scale

        # Miejsce na opisy nad i pod obrazem
        self.top_gap = 12
        self.bottom_gap = 14

        self.width = self.draw_width
        self.height = self.draw_height + self.top_gap + self.bottom_gap

    def draw(self):
        c = self.canv
        # Obraz
        c.drawImage(
            self.image_path,
            0,
            self.bottom_gap,
            width=self.draw_width,
            height=self.draw_height,
            preserveAspectRatio=True,
            mask='auto',
        )

        # Linia przerywana przez środek obrazu i szerokość w centrum
        center_y = self.bottom_gap + self.draw_height / 2.0
        c.setDash([3, 3])
        c.setStrokeColor(colors.HexColor('#FF6B6B'))
        c.line(0, center_y, self.draw_width, center_y)
        c.setDash([])

        if self.center_width_text:
            c.setFillColor(colors.HexColor('#2E4057'))
            c.setFont('Helvetica-Bold', 12)
            c.drawCentredString(self.draw_width / 2.0, center_y + 6, str(self.center_width_text))

        # Etykieta nad
        if self.top_label:
            c.setFillColor(colors.HexColor('#2E4057'))
            c.setFont('Helvetica-Bold', 10)
            c.drawCentredString(self.draw_width / 2.0, self.height - 10, str(self.top_label))

        # Etykieta pod
        if self.bottom_label:
            c.setFillColor(colors.HexColor('#2E4057'))
            c.setFont('Helvetica-Bold', 10)
            c.drawCentredString(self.draw_width / 2.0, 2, str(self.bottom_label))

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        # Bazowe ścieżki do katalogów ze zdjęciami
        self.door_image_base_dirs = [
            "drzwi/",
            "images/drzwi/",
        ]
        self.door_type_base_dirs = [
            "typ_drzwi/",
            "images/typ_drzwi/",
        ]
    
    def setup_custom_styles(self):
        """Tworzy niestandardowe style dla PDF"""
        # Próba zarejestrowania fontów obsługujących polskie znaki
        try:
            # Próbuj załadować font systemowy obsługujący UTF-8
            from reportlab.lib.fonts import addMapping
            # DejaVu fonts są dostępne na większości systemów i obsługują UTF-8
            font_paths = [
                '/System/Library/Fonts/Helvetica.ttc',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                'C:/Windows/Fonts/arial.ttf',  # Windows
            ]
            
            font_registered = False
            for font_path in font_paths:
                try:
                    import os
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                        pdfmetrics.registerFont(TTFont('CustomFont-Bold', font_path))
                        font_registered = True
                        break
                except:
                    continue
                    
            if not font_registered:
                # Fallback - użyj standardowych fontów reportlab
                self.font_name = 'Helvetica'
                self.font_bold = 'Helvetica-Bold'
            else:
                self.font_name = 'CustomFont'
                self.font_bold = 'CustomFont-Bold'
                
        except Exception as e:
            # Fallback na standardowe fonty
            self.font_name = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'
        
        # Styl nagłówka - kompaktowy
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E4057'),
            fontName=self.font_bold
        ))
        
        # Styl podtytułu - kompaktowy
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=11,
            spaceAfter=4,
            spaceBefore=6,
            textColor=colors.HexColor('#048A81'),
            borderWidth=1,
            borderColor=colors.HexColor('#048A81'),
            borderPadding=3,
            fontName=self.font_bold
        ))
        
        # Styl normalnego tekstu - kompaktowy
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=2,
            alignment=TA_LEFT,
            fontName=self.font_name
        ))
        
        # Styl dla informacji kontaktowych
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            fontName=self.font_name
        ))

    def safe_text(self, text):
        """Konwertuje tekst do bezpiecznego formatu dla PDF"""
        if not text:
            return ""
        # Zamień niektóre problematyczne znaki na bezpieczne odpowiedniki
        replacements = {
            'ą': 'a', 'ę': 'e', 'ć': 'c', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
            'Ą': 'A', 'Ę': 'E', 'Ć': 'C', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
        }
        
        try:
            # Próbuj zachować oryginalne znaki jeśli font je obsługuje
            return str(text)
        except:
            # Fallback - zamień polskie znaki
            result = str(text)
            for polish, replacement in replacements.items():
                result = result.replace(polish, replacement)
            return result

    def create_header(self, story, title):
        """Tworzy nagłówek dokumentu"""
        # Logo (jeśli istnieje)
        try:
            logo_path = "images/Logo.png"
            img = Image(logo_path, width=4*cm, height=2*cm)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 3*mm))
        except:
            # Jeśli logo nie istnieje, użyj tekstu
            company_name = Paragraph("DOMOWNIK", self.styles['CustomTitle'])
            story.append(company_name)
            story.append(Spacer(1, 5*mm))
        
        # Tytuł dokumentu
        title_para = Paragraph(self.safe_text(title), self.styles['CustomTitle'])
        story.append(title_para)
        story.append(Spacer(1, 2*mm))

    def create_info_section(self, story, title, data_dict):
        """Tworzy sekcję z informacjami"""
        # Nagłówek sekcji
        subtitle = Paragraph(self.safe_text(title), self.styles['CustomSubtitle'])
        story.append(subtitle)
        
        # Dane w tabeli
        table_data = []
        for key, value in data_dict.items():
            if value:  # Tylko jeśli wartość nie jest pusta
                table_data.append([self.safe_text(f"{key}:"), self.safe_text(str(value))])
        
        if table_data:
            table = Table(table_data, colWidths=[5*cm, 10*cm])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (0, -1), self.font_bold),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
            ]))
            story.append(table)
        
        story.append(Spacer(1, 3*mm))

    def build_info_panel(self, title, data_dict):
        """Buduje kompaktowy panel sekcji (nagłówek + tabela) do osadzenia obok innego panelu."""
        subtitle = Paragraph(self.safe_text(title), self.styles['CustomSubtitle'])

        table_data = []
        for key, value in data_dict.items():
            if value:
                table_data.append([self.safe_text(f"{key}:") , self.safe_text(str(value))])

        inner_table = Table(table_data)
        inner_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (0, -1), self.font_bold),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))

        # Owinięcie w tabelę jednokolumnową, by działało jako pojedynczy flowable w komórce rodzica
        panel = Table([[subtitle], [inner_table]])
        panel.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('TOPPADDING', (0, 1), (-1, 1), 3),
        ]))
        return panel

    def add_door_photo(self, story, door_opening_config, top_label: str | None = None, bottom_label: str | None = None, center_width_text: str | None = None):
        """Dodaje zdjęcie drzwi w zależności od wybranego kierunku otwierania.
        Oczekiwane pliki (dowolna z nazw):
          - lewe_przyl:   lewe_przyl.png | lewe_przylgowe.png
          - prawe_przyl:  prawe_przyl.png | prawe_przylgowe.png
          - lewe_odwr:    lewe_odwr.png | lewe_odwrotna.png | lewe_odwrotna_przylga.png
          - prawe_odwr:   prawe_odwr.png | prawe_odwrotna.png | prawe_odwrotna_przylga.png
        Szukane w katalogach: "drzwi/" oraz "images/drzwi/".
        """
        # Ustal wybrany wariant (pierwszy True w sensownej kolejności)
        order_of_priority = ["lewe_przyl", "prawe_przyl", "lewe_odwr", "prawe_odwr"]
        selected_key = next((k for k in order_of_priority if door_opening_config.get(k)), None)
        if not selected_key:
            return

        candidates_by_key = {
            "lewe_przyl": ["lewe_przyl.png", "lewe_przylgowe.png"],
            "prawe_przyl": ["prawe_przyl.png", "prawe_przylgowe.png"],
            "lewe_odwr": ["lewe_odwr.png", "lewe_odwrotna.png", "lewe_odwrotna_przylga.png"],
            "prawe_odwr": ["prawe_odwr.png", "prawe_odwrotna.png", "prawe_odwrotna_przylga.png"],
        }

        image_path = None
        for base_dir in self.door_image_base_dirs:
            for filename in candidates_by_key[selected_key]:
                candidate = os.path.join(base_dir, filename)
                if os.path.exists(candidate):
                    image_path = candidate
                    break
            if image_path:
                break

        if image_path:
            try:
                flowable = DoorPhotoWithLabels(
                    image_path=image_path,
                    top_label=self.safe_text(top_label),
                    bottom_label=self.safe_text(bottom_label),
                    center_width_text=self.safe_text(center_width_text),
                    max_width=3 * cm,
                )
                story.append(flowable)
                story.append(Spacer(1, 8 * mm))
            except Exception:
                pass
        else:
            # Brak pliku – dodaj krótką informację zamiast obrazka
            story.append(Paragraph(
                self.safe_text("Brak pliku ze zdjęciem kierunku otwierania w katalogu 'drzwi/'."),
                self.styles['CustomNormal']
            ))
            story.append(Spacer(1, 8 * mm))

    def _find_door_image_helper(self, door_opening_config):
        """Helper do wyszukiwania obrazka kierunku otwierania."""
        order_of_priority = ["lewe_przyl", "prawe_przyl", "lewe_odwr", "prawe_odwr"]
        selected_key = next((k for k in order_of_priority if door_opening_config.get(k)), None)
        if not selected_key:
            return None, None

        candidates_by_key = {
            "lewe_przyl": ["lewe_przyl.png", "lewe_przylgowe.png"],
            "prawe_przyl": ["prawe_przyl.png", "prawe_przylgowe.png"],
            "lewe_odwr": ["lewe_odwr.png", "lewe_odwrotna.png", "lewe_odwrotna_przylga.png"],
            "prawe_odwr": ["prawe_odwr.png", "prawe_odwrotna.png", "prawe_odwrotna_przylga.png"],
        }

        image_path = None
        for base_dir in self.door_image_base_dirs:
            for filename in candidates_by_key[selected_key]:
                candidate = os.path.join(base_dir, filename)
                if os.path.exists(candidate):
                    image_path = candidate
                    break
            if image_path:
                break
        return selected_key, image_path

    def _find_door_type_image(self, door_type):
        """Zwraca ścieżkę obrazka typu drzwi."""
        if not door_type:
            return None
            
        # Mapowanie typów drzwi na nazwy plików
        type_mappings = {
            "przylgowe": ["przylgowe.png", "przylg.png"],
            "bezprzylgowe": ["bezprzylgowe.png", "bezprzylg.png"],
            "odwrotna przylga": ["odwrotna_przylga.png", "odwrotna.png", "odwr.png"],
            "inne": ["inne.png", "other.png"]
        }
        
        # Znajdź pasujące mapowanie (case-insensitive)
        door_type_lower = door_type.lower()
        candidates = []
        for key, files in type_mappings.items():
            if key in door_type_lower or door_type_lower in key:
                candidates = files
                break
        
        if not candidates:
            # Fallback - spróbuj użyć nazwy typu bezpośrednio
            candidates = [f"{door_type_lower.replace(' ', '_')}.png"]

        # Szukaj pliku
        for base_dir in self.door_type_base_dirs:
            for filename in candidates:
                candidate = os.path.join(base_dir, filename)
                if os.path.exists(candidate):
                    return candidate
        return None

    def generate_drzwi_pdf(self, data):
        """Generuje PDF dla zamówienia drzwi"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                              topMargin=1*cm, bottomMargin=1*cm)
        
        story = []
        
        # Nagłówek
        self.create_header(story, "FORMULARZ DRZWI WEWNĘTRZNYCH")
        
        # Informacje podstawowe i dane produktu obok siebie
        basic_info = {
            "Pomieszczenie": data.get('pomieszczenie', ''),
            "Nazwisko klienta": data.get('nazwisko', ''),
            "Telefon": data.get('telefon', ''),
            "Data utworzenia": data.get('data_utworzenia', datetime.now()).strftime("%d.%m.%Y %H:%M") if data.get('data_utworzenia') else '',
            "ID dokumentu": data.get('id', '')
        }
        
        # Dane produktu
        product_info = {
            "Producent": data.get('producent', ''),
            "Seria": data.get('seria', ''),
            "Typ": data.get('typ', ''),
            "Rodzaj okleiny": data.get('rodzaj_okleiny', ''),
            "Ilość szyb": data.get('ilosc_szyb', ''),
            "Zamek": data.get('zamek', ''),
            "Szyba": data.get('szyba', ''),
            "Wentylacja": data.get('wentylacja', ''),
            "Klamka": data.get('klamka', '')
        }
        
        # Ułóż podstawowe i produktowe obok siebie
        basic_panel = self.build_info_panel("📋 INFORMACJE PODSTAWOWE", basic_info)
        product_panel = self.build_info_panel("🏷️ DANE PRODUKTU", product_info)
        top_row = Table([[basic_panel, product_panel]], colWidths=[8.0*cm, 8.0*cm])
        top_row.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(top_row)
        story.append(Spacer(1, 3*mm))
        
        # Pomiary otworu
        pomiary_info = {
            "Szerokość otworu": data.get('szerokosc_otworu', ''),
            "Wysokość otworu": data.get('wysokosc_otworu', ''),
            "Mierzona od": data.get('mierzona_od', ''),
            "Grubość muru": data.get('grubosc_muru', '') + " cm" if data.get('grubosc_muru') else '',
            "Stan ściany": data.get('stan_sciany', '')
        }
        # Specyfikacja techniczna
        spec_info = {
            "Typ drzwi": data.get('typ_drzwi', ''),
            "Ościeżnica": data.get('oscieznica', ''),
            "Kolor ościeżnicy": data.get('kolor_osc', ''),
            "Opaska": data.get('opaska', ''),
            "Kąt zacięcia": data.get('kat_zaciecia', ''),
            "Próg": data.get('prog', ''),
            "Wizjer": data.get('wizjer', ''),
            "Norma/Szkic": data.get('norma', '')
        }
        
        # Ułóż obie sekcje obok siebie jak na zdjęciu
        left_panel = self.build_info_panel("📐 POMIARY OTWORU", pomiary_info)
        right_panel = self.build_info_panel("🔨 SPECYFIKACJA TECHNICZNA", spec_info)
        side_by_side = Table([[left_panel, right_panel]], colWidths=[8.0*cm, 8.0*cm])
        side_by_side.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(side_by_side)
        story.append(Spacer(1, 3*mm))
        
        # Strona otwierania
        strona_otw = data.get('strona_otwierania', {})
        strony_txt = []
        if strona_otw.get('lewe_przyl'): strony_txt.append("Lewe przylgowe")
        if strona_otw.get('prawe_przyl'): strony_txt.append("Prawe przylgowe")
        if strona_otw.get('lewe_odwr'): strony_txt.append("Lewe odwrotna przylga")
        if strona_otw.get('prawe_odwr'): strony_txt.append("Prawe odwrotna przylga")
        
        strona_info = {
            "Strona otwierania": ", ".join(strony_txt) if strony_txt else "Nie wybrano"
        }
        
        # Układamy w 3 kolumny: strona otwierania + typ drzwi + zdjęcie kierunku
        strona_panel = self.build_info_panel("🚪 STRONA OTWIERANIA", strona_info)
        
        # Ilustracja typu drzwi
        door_type_image = None
        door_type = data.get('typ_drzwi/przylgowe.png', '')
        if door_type:
            door_type_path = self._find_door_type_image(door_type)
            if door_type_path:
                try:
                    door_type_image = DoorPhotoWithLabels(
                        image_path=door_type_path,
                        top_label="TYP DRZWI",
                        bottom_label=self.safe_text(door_type),
                        center_width_text=None,
                        max_width=2.2 * cm,
                        show_overlays=True
                    )
                except Exception:
                    pass
        
        # Ilustracja strony otwierania
        opening_image = None
        if any(strona_otw.values()):
            try:
                selected_key, image_path = self._find_door_image_helper(strona_otw)
                if image_path:
                    opening_image = DoorPhotoWithLabels(
                        image_path=image_path,
                        top_label=self.safe_text(data.get('napis_nad_drzwiami')),
                        bottom_label=self.safe_text(data.get('napis_pod_drzwiami')),
                        center_width_text=self.safe_text(data.get('szerokosc_skrzydla')),
                        max_width=2.2 * cm,
                    )
            except Exception:
                pass
        
        # Tabela 3-kolumnowa
        middle_row = Table([
            [strona_panel, door_type_image or "", opening_image or ""]
        ], colWidths=[5.5*cm, 5.25*cm, 5.25*cm])
            
        middle_row.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(middle_row)
        story.append(Spacer(1, 3*mm))
        
        # Uwagi i wykonawcy w jednym wierszu
        uwagi_info = {}
        if data.get('opcje_dodatkowe'):
            uwagi_info["Opcje dodatkowe"] = data.get('opcje_dodatkowe')
        if data.get('uwagi_montera'):
            uwagi_info["Uwagi montera"] = data.get('uwagi_montera')
        if data.get('uwagi_klienta'):
            uwagi_info["Uwagi dla klienta"] = data.get('uwagi_klienta')
        
        wykonawcy_info = {}
        if data.get('monter_id'):
            wykonawcy_info["Monter"] = data.get('monter_id')
        if data.get('data_pomiary'):
            wykonawcy_info["Data pomiarów"] = data.get('data_pomiary').strftime("%d.%m.%Y %H:%M")
        if data.get('sprzedawca_id'):
            wykonawcy_info["Sprzedawca"] = data.get('sprzedawca_id')
        if data.get('data_sprzedaz'):
            wykonawcy_info["Data sprzedaży"] = data.get('data_sprzedaz').strftime("%d.%m.%Y %H:%M")
        if data.get('status'):
            wykonawcy_info["Status"] = data.get('status').upper()
        
        if uwagi_info or wykonawcy_info:
            uwagi_panel = self.build_info_panel("💬 UWAGI I OPCJE", uwagi_info) if uwagi_info else ""
            wykonawcy_panel = self.build_info_panel("👥 WYKONAWCY", wykonawcy_info) if wykonawcy_info else ""
            
            bottom_row = Table([[uwagi_panel, wykonawcy_panel]], colWidths=[8.0*cm, 8.0*cm])
            bottom_row.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(bottom_row)
            story.append(Spacer(1, 2*mm))
        
        # Stopka
        story.append(Spacer(1, 5*mm))
        footer = Paragraph(
            f"Dokument wygenerowany automatycznie dnia {datetime.now().strftime('%d.%m.%Y o %H:%M')}<br/>"
            "DOMOWNIK - System zarzadzania zamowieniami",
            self.styles['ContactInfo']
        )
        story.append(footer)
        
        # Generuj PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_podlogi_pdf(self, data):
        """Generuje PDF dla zamówienia podłóg"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                              topMargin=2*cm, bottomMargin=2*cm)
        
        story = []
        
        # Nagłówek
        self.create_header(story, "FORMULARZ PODŁÓG")
        
        # Informacje podstawowe i system montażu obok siebie
        basic_info = {
            "Pomieszczenie": data.get('pomieszczenie', ''),
            "Telefon": data.get('telefon', ''),
            "Data utworzenia": data.get('data_utworzenia', datetime.now()).strftime("%d.%m.%Y %H:%M") if data.get('data_utworzenia') else '',
            "ID dokumentu": data.get('id', '')
        }
        
        montaz_info = {
            "System montażu": data.get('system_montazu', ''),
            "Podkład": data.get('podklad', ''),
            "MDF możliwy": data.get('mdf_mozliwy', '')
        }
        
        basic_panel = self.build_info_panel("📋 INFORMACJE PODSTAWOWE", basic_info)
        montaz_panel = self.build_info_panel("🔨 SYSTEM MONTAŻU", montaz_info)
        top_row_podlogi = Table([[basic_panel, montaz_panel]], colWidths=[8.0*cm, 8.0*cm])
        top_row_podlogi.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(top_row_podlogi)
        story.append(Spacer(1, 3*mm))
        
        # Pomiary listw i listwy progowe obok siebie
        suma_listw = (data.get('nw', 0) + data.get('nz', 0) + data.get('l', 0) + 
                     data.get('zl', 0) + data.get('zp', 0))
        
        listwy_info = {
            "NW": f"{data.get('nw', 0)} szt.",
            "NZ": f"{data.get('nz', 0)} szt.",
            "Ł": f"{data.get('l', 0)} szt.",
            "ZL": f"{data.get('zl', 0)} szt.",
            "ZP": f"{data.get('zp', 0)} szt.",
            "SUMA LISTW": f"{suma_listw} szt."
        }
        
        progowe_info = {
            "Jaka": data.get('listwy_jaka', ''),
            "Ile": data.get('listwy_ile', ''),
            "Gdzie": data.get('listwy_gdzie', '')
        }
        
        listwy_panel = self.build_info_panel("📏 POMIARY LISTW", listwy_info)
        progowe_panel = self.build_info_panel("🚪 LISTWY PROGOWE", progowe_info)
        middle_row_podlogi = Table([[listwy_panel, progowe_panel]], colWidths=[8.0*cm, 8.0*cm])
        middle_row_podlogi.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(middle_row_podlogi)
        story.append(Spacer(1, 3*mm))
        
        # Dane produktu w pełnej szerokości
        product_info = {
            "Rodzaj podłogi": data.get('rodzaj_podlogi', ''),
            "Seria": data.get('seria', ''),
            "Kolor": data.get('kolor', ''),
            "Folia": data.get('folia', ''),
            "Listwa przypodłogowa": data.get('listwa_przypodlogowa', '')
        }
        
        product_panel = self.build_info_panel("🏷️ DANE PRODUKTU", product_info)
        story.append(product_panel)
        story.append(Spacer(1, 3*mm))
        
        # Uwagi kompaktowo
        uwagi_info = {}
        if data.get('uwagi_montera'):
            uwagi_info["Uwagi montera"] = data.get('uwagi_montera')
        if data.get('uwagi'):
            uwagi_info["Uwagi dla klienta"] = data.get('uwagi')
        
        if uwagi_info:
            uwagi_panel = self.build_info_panel("💬 UWAGI", uwagi_info)
            story.append(uwagi_panel)
            story.append(Spacer(1, 3*mm))
        
        # Ostrzeżenie
        warning = Paragraph(
            self.safe_text("<b>⚠️ UWAGA!</b> Podloze powinno byc suche i rowne!!"),
            ParagraphStyle(
                name='Warning',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.red,
                alignment=TA_CENTER,
                borderWidth=2,
                borderColor=colors.red,
                borderPadding=10,
                backColor=colors.HexColor('#FFE6E6')
            )
        )
        story.append(warning)
        story.append(Spacer(1, 3*mm))
        
        # Informacje o wykonawcach - kompaktowo
        wykonawcy_info = {}
        if data.get('monter_id'):
            wykonawcy_info["Monter"] = data.get('monter_id')
        if data.get('data_pomiary'):
            wykonawcy_info["Data pomiarów"] = data.get('data_pomiary').strftime("%d.%m.%Y %H:%M")
        if data.get('sprzedawca_id'):
            wykonawcy_info["Sprzedawca"] = data.get('sprzedawca_id')
        if data.get('data_sprzedaz'):
            wykonawcy_info["Data sprzedaży"] = data.get('data_sprzedaz').strftime("%d.%m.%Y %H:%M")
        if data.get('status'):
            wykonawcy_info["Status"] = data.get('status').upper()
        
        if wykonawcy_info:
            wykonawcy_panel = self.build_info_panel("👥 WYKONAWCY", wykonawcy_info)
            story.append(wykonawcy_panel)
            story.append(Spacer(1, 2*mm))
        
        # Stopka
        story.append(Spacer(1, 5*mm))
        footer = Paragraph(
            f"Dokument wygenerowany automatycznie dnia {datetime.now().strftime('%d.%m.%Y o %H:%M')}<br/>"
            "DOMOWNIK - System zarzadzania zamowieniami",
            self.styles['ContactInfo']
        )
        story.append(footer)
        
        # Generuj PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

def generate_pdf_for_order(data, order_type):
    """
    Główna funkcja do generowania PDF
    
    Args:
        data: słownik z danymi zamówienia
        order_type: 'drzwi' lub 'podlogi'
    
    Returns:
        buffer z PDF
    """
    generator = PDFGenerator()
    
    if order_type == 'drzwi':
        return generator.generate_drzwi_pdf(data)
    elif order_type == 'podlogi':
        return generator.generate_podlogi_pdf(data)
    else:
        raise ValueError("order_type must be 'drzwi' or 'podlogi'")

def create_download_link(pdf_buffer, filename):
    """
    Tworzy link do pobrania PDF w Streamlit
    
    Args:
        pdf_buffer: buffer z PDF
        filename: nazwa pliku
    
    Returns:
        tuple (base64_pdf, filename)
    """
    pdf_buffer.seek(0)
    b64_pdf = base64.b64encode(pdf_buffer.read()).decode()
    return b64_pdf, filename

def display_pdf_download_button(data, order_type, doc_id):
    """
    Wyświetla przycisk pobierania PDF w Streamlit
    
    Args:
        data: dane zamówienia
        order_type: typ zamówienia ('drzwi' lub 'podlogi')
        doc_id: ID dokumentu
    """
    try:
        # Generuj PDF
        pdf_buffer = generate_pdf_for_order(data, order_type)
        
        # Utwórz nazwę pliku
        pomieszczenie = data.get('pomieszczenie', 'zamowienie')
        data_str = datetime.now().strftime("%Y%m%d")
        filename = f"{order_type}_{pomieszczenie}_{data_str}_{doc_id[:8]}.pdf"
        
        # Przycisk pobierania
        st.download_button(
            label=f"📄 Pobierz PDF - {order_type.upper()}",
            data=pdf_buffer.getvalue(),
            file_name=filename,
            mime="application/pdf",
            type="primary"
        )
        
        return True
        
    except Exception as e:
        st.error(f"Błąd podczas generowania PDF: {str(e)}")
        return False