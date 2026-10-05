"""Generates a professional, 20-slide 16:9 PowerPoint presentation (apresentacao_banca_tcc.pptx).

Based on the thesis defense script (reports/apresentacao_banca_tcc.md).
Features:
- 16:9 widescreen layout
- Aerospace executive theme (Space Navy #0B1B3D, Gold #E5A93C, Clean Gray #F4F6F9)
- Structured speaker notes for each slide (1st person narrative)
- Formatted tables, cards, and technical figures
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


def create_deck(output_pptx_path: Path, figures_dir: Path) -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    blank_layout = prs.slide_layouts[6]
    
    # Colors
    c_navy_dark = RGBColor(11, 27, 61)
    c_navy_accent = RGBColor(27, 54, 93)
    c_gold = RGBColor(229, 169, 60)
    c_card_bg = RGBColor(245, 247, 250)
    c_card_border = RGBColor(218, 224, 233)
    c_text_dark = RGBColor(30, 41, 59)
    c_text_muted = RGBColor(100, 116, 139)
    c_white = RGBColor(255, 255, 255)
    c_green = RGBColor(39, 174, 96)
    c_red = RGBColor(192, 57, 43)

    def add_header(slide, title_text: str, subtitle_text: str = "", slide_num: int = 1):
        # Top banner
        header_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.1))
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = c_navy_dark
        header_shape.line.color.rgb = c_navy_dark
        
        # Gold accent line
        gold_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.08), Inches(13.333), Inches(0.04))
        gold_line.fill.solid()
        gold_line.fill.fore_color.rgb = c_gold
        gold_line.line.color.rgb = c_gold
        
        # Title text
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(10.5), Inches(0.85))
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Calibri"
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = c_white
        
        if subtitle_text:
            p2 = tf.add_paragraph()
            p2.text = subtitle_text
            p2.font.name = "Calibri"
            p2.font.size = Pt(12)
            p2.font.color.rgb = c_gold

        # Slide Number Badge
        num_box = slide.shapes.add_textbox(Inches(11.8), Inches(0.2), Inches(1.0), Inches(0.6))
        np = num_box.text_frame.paragraphs[0]
        np.alignment = PP_ALIGN.RIGHT
        np.text = f"{slide_num:02d} / 20"
        np.font.name = "Calibri"
        np.font.size = Pt(13)
        np.font.bold = True
        np.font.color.rgb = c_white

        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.1), Inches(11.7), Inches(0.3))
        fp = footer_box.text_frame.paragraphs[0]
        fp.text = "UESC | TCC Engenharia Mecânica -- Gabriel Marques de Andrade | Orientadora: Prof.ª Dr.ª Nila C. F. L. Medeiros"
        fp.font.name = "Calibri"
        fp.font.size = Pt(9.5)
        fp.font.color.rgb = c_text_muted

    def add_card(slide, left: float, top: float, width: float, height: float, title: str = "", text_lines: list = None, bg_color = c_card_bg):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = c_card_border
        card.line.width = Pt(1)
        
        tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.15), Inches(width - 0.4), Inches(height - 0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        if title:
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = "Calibri"
            p.font.size = Pt(15)
            p.font.bold = True
            p.font.color.rgb = c_navy_accent
            p.space_after = Pt(8)
            
        if text_lines:
            first = True if not title else False
            for line in text_lines:
                if first:
                    p = tf.paragraphs[0]
                    first = False
                else:
                    p = tf.add_paragraph()
                p.text = line
                p.font.name = "Calibri"
                p.font.size = Pt(11.5)
                p.font.color.rgb = c_text_dark
                p.space_after = Pt(4)
        return card

    # =========================================================================
    # SLIDE 1: Capa
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = c_navy_dark
    bg1.line.color.rgb = c_navy_dark
    
    # Title Box
    t1_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(10.9), Inches(3.2))
    tf1 = t1_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "UNIVERSIDADE ESTADUAL DE SANTA CRUZ (UESC)\nCOLEGIADO DE ENGENHARIA MECÂNICA"
    p1.font.name = "Calibri"
    p1.font.size = Pt(14)
    p1.font.color.rgb = c_gold
    p1.font.bold = True
    p1.space_after = Pt(20)
    
    p2 = tf1.add_paragraph()
    p2.text = "CubeSat em Baixa Órbita: Otimização de Volume e Geometria para Maximização de Desempenho Estrutural e Funcional"
    p2.font.name = "Calibri"
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = c_white
    p2.space_after = Pt(15)
    
    p3 = tf1.add_paragraph()
    p3.text = "Metamateriais Auxéticos e Aprendizado Profundo Guiado por Física (Physics-Guided ResNet)"
    p3.font.name = "Calibri"
    p3.font.size = Pt(17)
    p3.font.color.rgb = c_gold
    
    # Author and Advisor Card
    infobox = s1.shapes.add_textbox(Inches(1.2), Inches(5.2), Inches(10.9), Inches(1.5))
    tfi = infobox.text_frame
    pi1 = tfi.paragraphs[0]
    pi1.text = "Autor: Gabriel Marques de Andrade   |   Orientadora: Prof.ª Dr.ª Nila Cecília de Faria Lopes Medeiros"
    pi1.font.name = "Calibri"
    pi1.font.size = Pt(14)
    pi1.font.bold = True
    pi1.font.color.rgb = c_white
    pi2 = tfi.add_paragraph()
    pi2.text = "Trabalho de Conclusão de Curso (TCC) -- Ilhéus, Bahia -- 2027"
    pi2.font.name = "Calibri"
    pi2.font.size = Pt(12)
    pi2.font.color.rgb = c_text_muted

    s1.notes_slide.notes_text_frame.text = (
        "Bom dia a todos os membros da banca examinadora, à minha orientadora Prof.ª Dr.ª Nila Cecília e aos presentes. "
        "Meu nome é Gabriel Marques de Andrade e hoje apresento meu Trabalho de Conclusão de Curso sobre a otimização "
        "estrutural e dinâmica de chassis CubeSat 1U via metamateriais auxéticos e inteligência computacional acelerada por física."
    )

    # =========================================================================
    # SLIDE 2: Contextualização
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Contextualização: A Era New Space e os Limites dos CubeSats 1U", "Crescimento de constelações LEO e restrições geométricas severas", 2)
    
    add_card(s2, 0.8, 1.4, 3.7, 5.4, "Padrão CalPoly CDS", [
        "• Formato 1U: 100 x 100 x 113.5 mm.",
        "• Orçamento de massa: 1.33 kg a 2.0 kg.",
        "• Estruturas monolíticas consomem até 35% da massa útil da plataforma.",
        "• Restrição de volume severa para eletrônicos, baterias e payloads científicos."
    ])
    add_card(s2, 4.8, 1.4, 3.7, 5.4, "Interface do Lançador P-POD", [
        "• Poly-Picosatellite Orbital Deployer (P-POD).",
        "• Ejeção cinemática por mola axial.",
        "• Contato metal-metal em 4 trilhos guia.",
        "• Impõe arestas maciças (8.5 x 8.5 mm) sem protuberâncias ou alívios externos."
    ])
    add_card(s2, 8.8, 1.4, 3.7, 5.4, "A Oportunidade Metamaterial", [
        "• Impossível aliviar trilhos externos.",
        "• Inovação concentrada nos painéis internos.",
        "• Manufatura Aditiva Metálica (L-PBF) em liga AlSi10Mg viabiliza células celulares complexas.",
        "• Alívio de massa com amortecimento de choques de ejeção."
    ])
    s2.notes_slide.notes_text_frame.text = (
        "A consolidação do padrão CubeSat permitiu que pequenas instituições colocassem cargas úteis no espaço. "
        "Contudo, a estrutura convencional consome uma fração expressiva do peso total. O mecanismo de mola do P-POD "
        "exige trilhos maciços, proibindo alívios externos. Portanto, a inovação precisa focar exclusivamente nos painéis internos."
    )

    # =========================================================================
    # SLIDE 3: O Problema de Engenharia
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "O Conflito de Engenharia: Rigidez, Massa e Cargas de Lançamento", "Severidade dinâmica da norma NASA GEVS vs. integridade estrutural", 3)
    
    add_card(s3, 0.8, 1.4, 5.7, 5.4, "Ambiente Dinâmico Severo (NASA GEVS)", [
        "• Vibração Aleatória Estocástica: 14.1 Grms.",
        "• Faixa de frequência: 20 a 2000 Hz.",
        "• Duração do teste: 120 s por eixo ortogonal.",
        "• Transmissibilidade em alumínio sólido ~ 85%.",
        "• Risco crítico de falha por fadiga em juntas de solda de PCBs (padrão PC/104)."
    ])
    add_card(s3, 6.8, 1.4, 5.7, 5.4, "O Dilema Tradicional de Projeto", [
        "• Alívio convencional de espessura reduz rigidez modal fundamental (f1 < 100 Hz).",
        "• Risco de acoplamento ressonante 'pogo' com os modos acústicos do veículo lançador.",
        "• Amortecedores elastoméricos adicionam peso e sofrem outgassing (desgasificação em vácuo).",
        "• Desafio: Aliviar > 60% de massa e aumentar rigidez modal, atenuando passivamente as vibrações."
    ])
    s3.notes_slide.notes_text_frame.text = (
        "O lançamento impõe um ambiente dinâmico brutal de 14.1 Grms. Em estruturas convencionais, quase 85% dessa vibração "
        "chega aos eletrônicos. Aliviar o alumínio comum torna o satélite flexível e viola o piso de 100 Hz da NASA. "
        "Nosso objetivo é resolver esse trade-off usando células auxéticas que absorvem vibrações passivamente."
    )

    # =========================================================================
    # SLIDE 4: Objetivos do Trabalho
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Objetivos: Rota 100% Computacional de Alto Desempenho", "Arquitetura preditiva e otimização sob normas espaciais", 4)
    
    add_card(s4, 0.8, 1.4, 11.7, 1.6, "Objetivo Geral", [
        "Desenvolver e validar um arcabouço computacional autônomo para projeto, aceleração neural e otimização multiobjetivo de chassi CubeSat 1U em liga AlSi10Mg (L-PBF) com painéis auxéticos reentrantes sob normas NASA GEVS."
    ])
    add_card(s4, 0.8, 3.3, 2.7, 3.5, "1. DfAM & CAD", [
        "• Parametrização 3D.",
        "• Sobressalto >= 35°.",
        "• Parede t >= 0.5 mm.",
        "• Despoeiramento desobstruído."
    ])
    add_card(s4, 3.8, 3.3, 2.7, 3.5, "2. Automação CAE", [
        "• Ansys MAPDL batch.",
        "• Elementos SOLID187.",
        "• Block Lanczos modal.",
        "• Espectro PSD GEVS."
    ])
    add_card(s4, 6.8, 3.3, 2.7, 3.5, "3. Physics ResNet", [
        "• Deep Learning com skip.",
        "• Perda Gibson-Ashby.",
        "• Monotonicidade física.",
        "• Latência sub-milissegundo."
    ])
    add_card(s4, 9.8, 3.3, 2.7, 3.5, "4. Multi-Agente & NSGA-II", [
        "• Máquina LangGraph.",
        "• 10.000 avaliações.",
        "• Fronteira de Pareto.",
        "• Seleção TOPSIS de voo."
    ])
    s4.notes_slide.notes_text_frame.text = (
        "Adotamos uma rota 100% computacional de alta fidelidade baseada na liga espacial AlSi10Mg. "
        "Nossos quatro pilares cobrem: modelagem DfAM para manufatura aditiva, geração de base de dados no Ansys, "
        "treinamento de modelo neural informado por física e orquestração evolutiva com NSGA-II e TOPSIS."
    )

    # =========================================================================
    # SLIDE 5: Metamateriais Auxéticos & Gibson-Ashby
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Fundamentação: Metamateriais Auxéticos e Leis de Escala", "Cinemática de Poisson negativo e modelo constitutivo celular", 5)
    
    add_card(s5, 0.8, 1.4, 5.7, 5.4, "Cinemática Auxética Reentrante", [
        "• Coeficiente de Poisson efetivo negativo (nu_eff < 0).",
        "• Rotação e flexão de costelas oblíquas e verticais.",
        "• Expansão lateral sob compressão axial.",
        "• Aumento da tenacidade à fratura e dissipação elástica.",
        "• Filtro mecânico passivo contra ondas de cisalhamento e choque."
    ])
    # Add Figure
    fig_auxetic = figures_dir / "auxetic_cell_geometry.png"
    if fig_auxetic.exists():
        s5.shapes.add_picture(str(fig_auxetic), Inches(6.8), Inches(1.4), width=Inches(5.7))
    
    s5.notes_slide.notes_text_frame.text = (
        "A célula reentrante possui geometria em gravata-borboleta. Sob compressão, as costelas oblíquas flexionam para fora, "
        "expandindo transversalmente. O modelo clássico de Gibson-Ashby rege a escala do módulo de elasticidade e tensão de escoamento "
        "com a densidade relativa celular, fornecendo a âncora física que usamos na função de perda da rede neural."
    )

    # =========================================================================
    # SLIDE 6: Critérios Normativos NASA GEVS
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Governança Normativa: Qualificação Espacial NASA GEVS", "NASA GSFC-STD-7000A e metodologia de fadiga de 3 bandas de Steinberg", 6)
    
    add_card(s6, 0.8, 1.4, 3.7, 5.4, "1. Rigidez Veicular", [
        "• Requisito: f1 >= 100.0 Hz.",
        "• Evita acoplamento ressonante dinâmico com modos de baixa frequência do foguete lançador.",
        "• Previne acelerações transientes 'pogo' catastróficas."
    ])
    add_card(s6, 4.8, 1.4, 3.7, 5.4, "2. Margens de Segurança", [
        "• Resposta estocástica a 3-sigma (99.73% de probabilidade).",
        "• Fator de segurança: FS_yield = 1.25.",
        "• Tensão admissível: sigma_adm = 184.0 MPa.",
        "• MS_yield = (sigma_adm / sigma_3sigma) - 1 > 0."
    ])
    add_card(s6, 8.8, 1.4, 3.7, 5.4, "3. Dano de Fadiga (Steinberg)", [
        "• Método das 3 bandas gaussianas (1s, 2s, 3s).",
        "• Regra linear de Palmgren-Miner.",
        "• Critério NASA-HDBK-7005: D <= 0.25.",
        "• Fator de segurança de vida de 4x sobre o teste de 120 segundos."
    ])
    s6.notes_slide.notes_text_frame.text = (
        "A qualificação é rigorosa: exigimos frequência fundamental acima de 100 Hz, margem de segurança positiva a 3-sigma "
        "sob escoamento com FS de 1.25 e dano acumulado de fadiga vibracional pelo método de Steinberg inferior a 0.25, "
        "o que garante uma sobrevida estrutural de quatro vezes o tempo de qualificação de voo."
    )

    # =========================================================================
    # SLIDE 7: DfAM para L-PBF em AlSi10Mg
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Restrições de Manufatura Aditiva Metálica (DfAM - LPBF)", "Portões paramétricos para garantia de fabricabilidade em liga AlSi10Mg", 7)
    
    add_card(s7, 0.8, 1.4, 3.7, 5.4, "Ângulo de Sobressalto", [
        "• theta_overhang >= 35°.",
        "• Elimina suportes internos inalcançáveis no núcleo auxético.",
        "• Evita acúmulo de calor e deformação térmica residual.",
        "• Reduz necessidade de pós-processamento mecânico."
    ])
    add_card(s7, 4.8, 1.4, 3.7, 5.4, "Espessura de Costela", [
        "• Espessura mínima: t >= 0.50 mm (nominal >= 0.60 mm).",
        "• Garante coalescência estável da poça de fusão laser.",
        "• Mitiga defeitos de falta de fusão (lack of fusion) e microporosidades."
    ])
    add_card(s7, 8.8, 1.4, 3.7, 5.4, "Evacuação de Pó", [
        "• Folga mínima desobstruída: gap >= 1.50 mm.",
        "• Orifícios de drenagem: d_drain >= 2.0 mm.",
        "• Previne aprisionamento de pó metálico não fundido (massa parasita oculta)."
    ])
    s7.notes_slide.notes_text_frame.text = (
        "Projetar para manufatura aditiva metálica exige portões estritos. Células internas não admitem suportes removíveis; "
        "portanto, o ângulo autossuportado precisa ser superior a 35 graus. A espessura mínima de 0.5 mm garante fusão sem vazios, "
        "e canais desobstruídos acima de 1.5 mm garantem a drenagem total do pó residual de alumínio."
    )

    # =========================================================================
    # SLIDE 8: Amostragem DoE (LHS)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Amostragem do Espaço de Projeto: Hipercubo Latino (LHS)", "250 amostras paramétricas para exploração elastodinâmica global", 8)
    
    add_card(s8, 0.8, 1.4, 5.7, 5.4, "Configuração do DoE", [
        "• Amostragem por Hipercubo Latino (LHS).",
        "• Semente pseudoaleatória reprodutível (seed=42).",
        "• Espaço 4D viável:",
        "  - Ângulo reentrante: theta in [50°, 85°]",
        "  - Espessura de parede: t in [0.5, 1.8] mm",
        "  - Comprimento da costela: l in [6.0, 15.0] mm",
        "  - Altura vertical: h in [8.0, 20.0] mm",
        "• 250 pontos gerados em doe_samples_input.csv."
    ])
    add_card(s8, 6.8, 1.4, 5.7, 5.4, "Triagem Inicial DfAM", [
        "• 250 configurações submetidas aos portões DfAM.",
        "• 181 amostras aprovadas (72.4% de taxa de viabilidade geométrica).",
        "• 69 amostras rejeitadas precocemente por colapso de folga de pó ou sobressalto excessivo.",
        "• Economia imediata de esforço computacional antes da fase de elementos finitos."
    ])
    s8.notes_slide.notes_text_frame.text = (
        "Exploramos o espaço de projeto com 250 amostras via Hipercubo Latino. A triagem prévia pelos portões DfAM descartou "
        "de imediato 69 configurações geometricamente inviáveis. As 181 amostras aprovadas seguiram para o laço de simulação em elementos finitos."
    )

    # =========================================================================
    # SLIDE 9: Automação FEA (Ansys MAPDL)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Simulação Numérica de Alta Ordem: Ansys MAPDL Batch", "Discretização com SOLID187, Block Lanczos e espectro estocástico PSD", 9)
    
    add_card(s9, 0.8, 1.4, 5.7, 5.4, "Modelagem Numérica", [
        "• Elementos tetraédricos quadráticos de 10 nós (SOLID187).",
        "• Mapeamento de tensões locais em entalhes celulares.",
        "• Análise modal pré-tensionada: Block Lanczos (MODOPT, LANB, 10).",
        "• Análise espectral PSD GEVS (14.1 Grms, zeta = 2.0%).",
        "• Runner batch resiliente com telemetria estruturada."
    ])
    add_card(s9, 6.8, 1.4, 5.7, 5.4, "Estatísticas da Base CAE (250 Pontos)", [
        "• Frequência f1: Média = 746.3 Hz (572.7 a 1205.9 Hz).",
        "• Desacoplamento perfeito sobre a restrição de 100 Hz.",
        "• Tensão 3-sigma média = 85.7 MPa (limite = 184 MPa).",
        "• Transmissibilidade média T = 0.233 (atenuação média > 76%).",
        "• Dano de fadiga médio D = 0.0061 << 0.25.",
        "• Tempo médio por simulação: 60 a 120 segundos."
    ])
    s9.notes_slide.notes_text_frame.text = (
        "As simulações automatizadas no Ansys MAPDL utilizaram elementos tetraédricos de alta ordem SOLID187. "
        "A base revelou frequências fundamentais médias de 746 Hz e atenuação média superior a 76%. "
        "Porém, cada simulação leva até dois minutos. Executar um laço genético com milhares de pontos levaria semanas."
    )

    # =========================================================================
    # SLIDE 10: Physics-Guided ResNet
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Metamodelo Neural: Physics-Guided ResNet", "Aprendizado residual profundo com função de perda composta informada por física", 10)
    
    add_card(s10, 0.8, 1.4, 5.7, 5.4, "Arquitetura Deep Residual", [
        "• Entrada 5D: [theta, t, l, h, rho_rel].",
        "• 2 Blocos Residuais com conexões skip.",
        "• 64 neurônios por camada, LayerNorm, SiLU.",
        "• Saída 4D: [f1, sigma_3sigma, Grms, T].",
        "• Elimina desvanecimento de gradiente."
    ])
    add_card(s10, 6.8, 1.4, 5.7, 5.4, "Função de Perda Física Composta", [
        "L_total = L_MSE + lambda_phys * L_GA + lambda_mono * L_mono",
        "",
        "• L_GA: Penaliza desvio assintótico da lei de Gibson-Ashby (f1 proporcional a sqrt(rho_rel)).",
        "• L_mono: Penalização ReLU para assegurar monotonicidade estrita (densidade maior não pode reduzir rigidez).",
        "• Erradica alucinações e previsões não-físicas."
    ])
    s10.notes_slide.notes_text_frame.text = (
        "Para substituir o Ansys com extrema velocidade e confiabilidade, desenvolvemos a Physics-Guided ResNet. "
        "Sua função de perda penaliza desvios da lei de Gibson-Ashby e impõe monotonicidade física. "
        "Isso impede que a rede gere predições absurdas onde um aumento de material reduzisse a rigidez."
    )

    # =========================================================================
    # SLIDE 11: Treinamento e Paridade Neural
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Desempenho da Rede: Paridade e Benchmarks", "Acurácia superior a 98.7% e aceleração computacional de 250.000x", 11)
    
    add_card(s11, 0.8, 1.4, 4.5, 5.4, "Métricas no Teste Cego (N=50)", [
        "• R2 Médio = 0.9874 (98.74% de acurácia).",
        "• NRMSE Médio = 2.07%.",
        "• R2 (f1) = 0.9543 | NRMSE = 5.68%",
        "• R2 (sigma_3sigma) = 0.9989 | NRMSE = 0.73%",
        "• R2 (Grms) = 0.9982 | NRMSE = 0.93%",
        "• R2 (T) = 0.9981 | NRMSE = 0.94%",
        "",
        "• Latência de Inferência: 0.4049 ms",
        "  (> 2.400 avaliações / segundo).",
        "• Aceleração de ~250.000x frente ao FEA."
    ])
    fig_parity = figures_dir / "parity_plots.png"
    if fig_parity.exists():
        s11.shapes.add_picture(str(fig_parity), Inches(5.6), Inches(1.4), width=Inches(6.9))
    
    s11.notes_slide.notes_text_frame.text = (
        "No conjunto de teste cego, a rede atingiu R2 médio de 98.74% e NRMSE de apenas 2%. Em tensão e transmissibilidade, "
        "o R2 superou 99.8%. A latência de inferência foi de 0.4 milissegundos por avaliação — acelerando o cálculo em mais de "
        "250.000 vezes em relação ao solver de elementos finitos."
    )

    # =========================================================================
    # SLIDE 12: Orquestrador Multi-Agente (LangGraph)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Orquestração Determinística via LangGraph", "Máquina de estados fortemente tipada com triagem prévia automática", 12)
    
    add_card(s12, 0.8, 1.4, 4.5, 5.4, "Governança Multi-Agente", [
        "• Contrato de estado unificado: CubeSatState.",
        "• Nós Especialistas:",
        "  - CadDfamAgent (triagem 3D)",
        "  - NeuralSurrogateAgent (inferência 0.4 ms)",
        "  - GevsQualifierAgent (normas NASA)",
        "  - GroundTruthFeaAgent (solver alta ordem)",
        "• Descarte precoce de candidatos inviáveis.",
        "• Trilha de auditoria cronológica UTC."
    ])
    fig_workflow = figures_dir / "multi_agent_workflow.png"
    if fig_workflow.exists():
        s12.shapes.add_picture(str(fig_workflow), Inches(5.6), Inches(1.4), width=Inches(6.9))
        
    s12.notes_slide.notes_text_frame.text = (
        "Implementamos uma máquina de estados finitos determinística com o LangGraph. "
        "O fluxo descarta antecipadamente qualquer candidato não-conforme no portão DfAM ou nos limites da NASA GEVS. "
        "Apenas designs estritamente qualificados avançam para validação de alta ordem, economizando computação e garantindo auditoria UTC."
    )

    # =========================================================================
    # SLIDE 13: Otimização Multiobjetivo (NSGA-II)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Otimização Multiobjetivo: Algoritmo NSGA-II", "Busca evolutiva de 10.000 avaliações com Deb's Constrained Domination", 13)
    
    add_card(s13, 0.8, 1.4, 5.7, 5.4, "Formulação Multiobjetivo", [
        "Minimizar f1(x) = Massa Estrutural (kg)",
        "Minimizar f2(x) = Transmissibilidade Dinâmica (T)",
        "",
        "Sujeito a:",
        "• theta in [50°, 85°], t in [0.5, 1.8] mm",
        "• l in [6.0, 15.0] mm, h in [8.0, 20.0] mm",
        "• theta_overhang >= 35° (DfAM)",
        "• t >= 0.50 mm, gap >= 1.50 mm (DfAM)",
        "• f1 >= 100 Hz (NASA GEVS)",
        "• MS_yield > 0 (NASA GEVS)",
        "• D_Steinberg <= 0.25 (NASA-HDBK-7005)"
    ])
    add_card(s13, 6.8, 1.4, 5.7, 5.4, "Parâmetros e Performance", [
        "• População = 100 indivíduos | Gerações = 100.",
        "• Total de avaliações = 10.000 candidatos.",
        "• Cruzamento SBX (eta_c=15, p_c=0.90).",
        "• Mutação Polinomial (eta_m=20, p_m=0.25).",
        "• Deb's Constrained Domination (inviáveis ordenados por violação de restrições).",
        "",
        "• Tempo Total de Execução: 4.82 segundos!",
        "• Equivalente no Ansys: ~277 horas ininterruptas."
    ])
    s13.notes_slide.notes_text_frame.text = (
        "Acoplamos o modelo neural ao algoritmo genético NSGA-II com dominação restrita de Deb. "
        "A campanha de 10.000 avaliações foi executada em apenas 4.82 segundos. "
        "Se tivéssemos feito essa busca diretamente no Ansys, levaríamos quase 12 dias de computação contínua."
    )

    # =========================================================================
    # SLIDE 14: Fronteira de Pareto
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Fronteira de Pareto e Trade-offs Estruturais", "100 designs Pareto-ótimos factíveis mapeando o espaço de compromisso", 14)
    
    add_card(s14, 0.8, 1.4, 4.5, 5.4, "Análise dos Regimes Físicos", [
        "1. Regime Ultraleve (m < 0.10 kg):",
        "• Células esbeltas (t ~ 0.50 mm).",
        "• Densidade relativa < 10%.",
        "• Transmissibilidade T ~ 0.23 a 0.28.",
        "• Tensões 3-sigma próximas de 180 MPa.",
        "",
        "2. Regime de Ultra-Atenuação (T < 0.18):",
        "• Costelas espessas (t ~ 0.80 a 1.10 mm).",
        "• Ângulos reentrantes pronunciados (70°-80°).",
        "• Maximização do efeito auxético tridimensional.",
        "• Massa estrutural m ~ 0.14 a 0.16 kg."
    ])
    fig_pareto = figures_dir / "pareto_frontier.png"
    if fig_pareto.exists():
        s14.shapes.add_picture(str(fig_pareto), Inches(5.6), Inches(1.4), width=Inches(6.9))
        
    s14.notes_slide.notes_text_frame.text = (
        "A fronteira de Pareto evidencia 100 soluções factíveis divididas em dois regimes claros: "
        "estruturas ultraleves de 100 gramas com amortecimento moderado, e estruturas de ultra-atenuação com T abaixo de 0.18, "
        "mas ligeiramente mais pesadas. Para selecionar o ponto ótimo para voo espacial, aplicamos o método multicritério TOPSIS."
    )

    # =========================================================================
    # SLIDE 15: Seleção TOPSIS & Design Ótimo
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "Tomada de Decisão Multicritério: TOPSIS", "Eleição do Design de Voo Ótimo (#28) com equilíbrio de objetivos aeroespaciais", 15)
    
    add_card(s15, 0.8, 1.4, 5.7, 5.4, "Ponderação Multicritério", [
        "Vetor de Pesos Aeroespacial:",
        "• w_m = 0.35 (Massa estrutural -- custo)",
        "• w_T = 0.30 (Transmissibilidade -- custo)",
        "• w_f1 = 0.15 (Frequência fundamental -- benefício)",
        "• w_sigma = 0.10 (Tensão 3-sigma -- custo)",
        "• w_D = 0.10 (Dano de fadiga -- custo)",
        "",
        "Resultado TOPSIS:",
        "• Design #28 eleito como solução de maior proximidade relativa (C* = 0.814)."
    ])
    add_card(s15, 6.8, 1.4, 5.7, 5.4, "Geometria do Design #28", [
        "• Ângulo reentrante: theta = 65.75°",
        "• Espessura de costela: t = 0.613 mm",
        "• Comprimento oblíquo: l = 8.50 mm",
        "• Altura vertical: h = 13.96 mm",
        "• Densidade relativa: rho_rel = 12.52%",
        "• Coeficiente de Poisson: nu_eff = -13.81",
        "",
        "Comportamento fortemente auxético tridimensional proporcionando atenuação acústica passiva."
    ])
    s15.notes_slide.notes_text_frame.text = (
        "Pelo método TOPSIS, ponderamos 35% de peso para massa, 30% para transmissibilidade e 35% para rigidez e integridade. "
        "O Design #28 foi destacado com folga. Sua geometria possui espessura de 0.61 mm e coeficiente de Poisson de menos 13.81, "
        "gerando alta capacidade de blindagem contra choques dinâmicos."
    )

    # =========================================================================
    # SLIDE 16: Validação FEA Ground Truth
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    add_header(s16, "Validação Cruzada: FEA Ground Truth vs. ResNet", "Confronto de alta fidelidade no Ansys MAPDL para o Design Ótimo #28", 16)
    
    # Table layout
    rows, cols = 8, 5
    table_shape = s16.shapes.add_table(rows, cols, Inches(0.8), Inches(1.5), Inches(11.7), Inches(4.5))
    table = table_shape.table
    
    headers = ["Resposta Estrutural", "Predição Neural", "FEA Ground Truth", "Erro Relativo", "Limite NASA"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = c_navy_accent
        for p in cell.text_frame.paragraphs:
            p.font.name = "Calibri"
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = c_white
            p.alignment = PP_ALIGN.CENTER
            
    data_rows = [
        ["Massa Total (kg)", "0.1155 kg", "0.1155 kg", "0.00%", "<= 0.350 kg (Aprovado)"],
        ["Frequência Fundamental (f1)", "642.38 Hz", "579.62 Hz", "+10.83%", ">= 100.0 Hz (Aprovado)"],
        ["Pico de Tensão 3-sigma", "168.57 MPa", "166.91 MPa", "+0.99%", "<= 184.0 MPa (Aprovado)"],
        ["Aceleração na Carga Útil", "2.814 Grms", "2.816 Grms", "-0.07%", "<= 14.1 Grms (Aprovado)"],
        ["Transmissibilidade (T)", "0.19973", "0.19974", "-0.008%", "< 1.00 (Aprovado)"],
        ["Margem de Segurança (MS)", "+0.092", "+0.102", "-9.80%", "> 0.00 (Aprovado)"],
        ["Dano de Fadiga (Steinberg)", "0.0543", "0.0458", "+18.56%", "<= 0.25 (Aprovado)"],
    ]
    
    for row_idx, r in enumerate(data_rows):
        for col_idx, val in enumerate(r):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = c_card_bg if row_idx % 2 == 0 else c_white
            for p in cell.text_frame.paragraphs:
                p.font.name = "Calibri"
                p.font.size = Pt(10.5)
                p.font.color.rgb = c_text_dark
                if col_idx in [1, 2, 3, 4]:
                    p.alignment = PP_ALIGN.CENTER
                if "Aprovado" in val:
                    p.font.bold = True
                    p.font.color.rgb = c_green

    s16.notes_slide.notes_text_frame.text = (
        "Reanalisamos o Design #28 em alta fidelidade no Ansys MAPDL. A concordância foi extraordinária: erro de 0.99% em tensão "
        "e 0.008% em transmissibilidade. A frequência real foi de 579 Hz, muito acima dos 100 Hz exigidos, e o dano de fadiga de 0.046 "
        "atesta sobrevida de mais de cinco vezes o tempo de teste do foguete."
    )

    # =========================================================================
    # SLIDE 17: Benchmark Frente ao Sólido
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    add_header(s17, "Benchmark: Chassi Monolítico vs. Chassi Auxético Ótimo", "Salto de desempenho aeroespacial e eficiência estrutural", 17)
    
    add_card(s17, 0.8, 1.4, 3.7, 5.4, "Massa Estrutural", [
        "• Baseline Sólido: 0.308 kg",
        "• Chassi Auxético: 0.116 kg",
        "",
        "REDUÇÃO DE 62.49%",
        "",
        "• 192 gramas economizados.",
        "• Massa convertível em baterias adicionais, módulos de propulsão ou sensores ópticos de maior abertura."
    ])
    add_card(s17, 4.8, 1.4, 3.7, 5.4, "Isolamento Vibratório", [
        "• Transmissibilidade: 0.850 -> 0.1997",
        "",
        "ATENUAÇÃO DE 76.50%",
        "(12.6 dB de atenuação)",
        "",
        "• Aceleração na carga útil cai de 12.0 Grms para apenas 2.82 Grms.",
        "• Elimina necessidade de coxins e isoladores viscoelásticos externos."
    ])
    add_card(s17, 8.8, 1.4, 3.7, 5.4, "Rigidez & Fadiga", [
        "• Frequência fundamental aumenta de 512.0 Hz para 579.62 Hz (+13.20%).",
        "• Rigidez dinâmica específica (f1/m) amplamente superior.",
        "• MS_yield = +0.10 (Plenamente elástico).",
        "• Dano D = 0.046 (Qualificado NASA)."
    ])
    s17.notes_slide.notes_text_frame.text = (
        "O confronto direto com o chassi convencional consolida as vantagens: reduzimos a massa em 62.5%, liberando quase 200 gramas "
        "para instrumentação científica. Atenuamos as vibrações em 76.5%, blindando os sensores a bordo com 12.6 dB de isolamento passivo, "
        "e ainda aumentamos a frequência natural em 13.2%."
    )

    # =========================================================================
    # SLIDE 18: Conclusões
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    add_header(s18, "Conclusões e Principais Contribuições", "Validação completa do arcabouço computacional autônomo de alta fidelidade", 18)
    
    add_card(s18, 0.8, 1.4, 5.7, 5.4, "Metas Alcançadas", [
        "1. Concepção e parametrização DfAM de chassi auxético 1U em liga aeroespacial AlSi10Mg.",
        "2. Redução de 62.49% na massa estrutural mantendo conformidade CalPoly CDS.",
        "3. Atenuação dinâmica de 76.50% na carga útil sem amortecedores externos.",
        "4. Qualificação estrutural plena sob as normas NASA GSFC-STD-7000A e NASA-HDBK-7005.",
        "5. Metamodelo neural acelerou o laço genético em mais de 200.000x."
    ])
    add_card(s18, 6.8, 1.4, 5.7, 5.4, "Contribuições Técnicas", [
        "• Formulação Physics-Guided ResNet: perda informada por Gibson-Ashby e monotonicidade.",
        "• Governança determinística LangGraph: auditoria UTC e triagem de descarte precoce.",
        "• Preservação de arestas monolíticas maciças (8.5 x 8.5 mm) para interface P-POD.",
        "• Reprodutibilidade científica integral: 53 testes automatizados (100% de aprovação)."
    ])
    s18.notes_slide.notes_text_frame.text = (
        "Em conclusão, comprovamos que a manufatura aditiva aliada ao deep learning guiado por física viabiliza satélites "
        "substancialmente mais leves e dinamicamente protegidos. Atingimos todas as metas de projeto, aceleramos a busca evolutiva "
        "e garantimos a qualificação estrutural perante a NASA."
    )

    # =========================================================================
    # SLIDE 19: Trabalhos Futuros
    # =========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    add_header(s19, "Trabalhos Futuros e Próximos Passos", "Extensões experimentais e escalonamento para envelopes espaciais estendidos", 19)
    
    add_card(s19, 0.8, 1.4, 3.7, 5.4, "1. Validação Experimental", [
        "• Manufatura física de espécimes L-PBF em máquina industrial com pó AlSi10Mg.",
        "• Ensaios dinâmicos em mesa vibratória triaxial (shaker table).",
        "• Confronto espectral direto das curvas de transmissibilidade física e numérica."
    ])
    add_card(s19, 4.8, 1.4, 3.7, 5.4, "2. Ciclagem Térmica (TVAC)", [
        "• Ensaio em câmara de termovácuo (-40°C a +85°C em 10^-6 Torr).",
        "• Investigação da condutividade térmica anisotrópica do núcleo celular.",
        "• Avaliação de dissipação de calor de eletrônicos durante eclipses orbitais."
    ])
    add_card(s19, 8.8, 1.4, 3.7, 5.4, "3. Escalonamento 3U / 6U / 12U", [
        "• Extensão da parametrização para envelopes maiores.",
        "• Núcleos auxéticos com Gradação Funcional de Densidade (FGL) tridimensional contínua.",
        "• Avaliação de degradação ambiental por oxigênio atômico (AO) em LEO."
    ])
    s19.notes_slide.notes_text_frame.text = (
        "Como continuidade, propomos: testes físicos em mesa vibratória com protótipos impressos em AlSi10Mg; "
        "ensaios em câmara de termovácuo TVAC para avaliar a condutividade anisotrópica do núcleo auxético; "
        "e expansão da metodologia para plataformas maiores de 3U, 6U e 12U com densidade funcionalmente graduada."
    )

    # =========================================================================
    # SLIDE 20: Agradecimentos
    # =========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    bg20 = s20.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg20.fill.solid()
    bg20.fill.fore_color.rgb = c_navy_dark
    bg20.line.color.rgb = c_navy_dark
    
    tb20 = s20.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(10.9), Inches(3.8))
    tf20 = tb20.text_frame
    tf20.word_wrap = True
    
    p = tf20.paragraphs[0]
    p.text = "MUITO OBRIGADO PELA ATENÇÃO!"
    p.font.name = "Calibri"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = c_gold
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(25)
    
    p = tf20.add_paragraph()
    p.text = "Agradecimentos especiais à Universidade Estadual de Santa Cruz (UESC), ao Colegiado de Engenharia Mecânica e à orientadora Prof.ª Dr.ª Nila Cecília de Faria Lopes Medeiros."
    p.font.name = "Calibri"
    p.font.size = Pt(14)
    p.font.color.rgb = c_white
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(25)
    
    p = tf20.add_paragraph()
    p.text = "Repositório do Projeto: https://github.com/Marques-svnt/tcc-cubesats\nEstamos à disposição para a arguição e considerações da banca examinadora."
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.color.rgb = c_gold
    p.alignment = PP_ALIGN.CENTER

    s20.notes_slide.notes_text_frame.text = (
        "Gostaria de agradecer sinceramente à UESC, ao corpo docente e em especial à minha orientadora Prof.ª Dr.ª Nila Cecília "
        "pelo apoio e rigor científico. Agradeço também aos membros da banca examinadora e coloco-me à inteira disposição para a arguição."
    )

    prs.save(str(output_pptx_path))
    print(f"Presentation successfully saved to: {output_pptx_path}")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    deck_path = base_dir / "reports" / "apresentacao_banca_tcc.pptx"
    fig_dir = base_dir / "figures"
    create_deck(deck_path, fig_dir)
