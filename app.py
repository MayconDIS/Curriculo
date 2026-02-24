import flet as ft
import json
import os
import asyncio
from datetime import date, datetime
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

ARQUIVO_JSON = 'dados.json'

# --- FUNÇÕES DE DADOS E LÓGICA ---
def carregar_dados():
    with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def calcular_status(dados):
    total_xp = sum(p['xp_ganho'] for p in dados['projetos']) + sum(h.get('xp', 0) for h in dados.get('habilidades', []))
    if total_xp < 500: rank = "Ferro", ft.Colors.BLUE_GREY_400
    elif total_xp < 1000: rank = "Bronze", ft.Colors.BROWN_400
    elif total_xp < 1500: rank = "Prata", ft.Colors.GREY_400
    elif total_xp < 2200: rank = "Ouro", ft.Colors.AMBER_400
    elif total_xp < 3000: rank = "Platina", ft.Colors.CYAN_300
    else: rank = "Diamante", ft.Colors.PURPLE_300
    return total_xp, rank[0], rank[1]

async def forjar_curriculo_magia(dados_atuais):
    total_xp, nome_rank, _ = calcular_status(dados_atuais)
    
    hoje = date.today()
    try:
        inicio = datetime.strptime(dados_atuais['curso']['inicio'], "%Y-%m-%d").date()
        fim = datetime.strptime(dados_atuais['curso']['fim'], "%Y-%m-%d").date()
        porcentagem = int(((hoje - inicio).days / (fim - inicio).days) * 100)
    except:
        porcentagem = 0
        
    barra = ("█" * (porcentagem // 10)) + ("░" * (10 - (porcentagem // 10)))

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    html_renderizado = template.render(
        perfil=dados_atuais.get('perfil', {}),
        projetos=dados_atuais.get('projetos', []),
        habilidades=dados_atuais.get('habilidades', []),
        total_xp=total_xp,
        rank_atual=nome_rank,
        barra_progresso=barra,
        porcentagem_curso=porcentagem
    )

    caminho_html = os.path.abspath('index_gerado.html')
    with open(caminho_html, 'w', encoding='utf-8') as f:
        f.write(html_renderizado)

    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        pagina = await navegador.new_page()
        await pagina.goto(f"file://{caminho_html}")
        await pagina.pdf(
            path="Curriculo_Maycon_Douglas.pdf",
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
        )
        await navegador.close()

# --- INTERFACE: NOTION (ESQ) + ESPELHO A4 (DIR) ---
def main(page: ft.Page):
    page.title = "Próximo Nível do Dev"
    page.window.width = 1600
    page.window.height = 900
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#191919" 

    dados = carregar_dados()

    # --- LADO ESQUERDO (FORMULÁRIO NOTION CLEAN) ---
    estilo_input = {
        "bgcolor": "transparent",
        "border_color": ft.Colors.WHITE_24,
        "border_radius": 4, 
        "color": ft.Colors.WHITE,
        "cursor_color": ft.Colors.WHITE,
        "text_size": 13,
        "dense": True, # Deixa o campo mais estreito e elegante
        "content_padding": ft.padding.all(12)
    }

    input_nome = ft.TextField(label="Nome do Projeto / Missão", **estilo_input)
    input_tipo = ft.TextField(label="Categoria (Ex: Aplicação Python)", **estilo_input)
    input_data = ft.TextField(label="Data (Ex: Março de 2026)", **estilo_input)
    input_desc = ft.TextField(label="Descrição técnica do projeto...", multiline=True, min_lines=3, **estilo_input)
    input_xp = ft.TextField(label="Recompensa (XP)", **estilo_input)

    # --- LADO DIREITO (ESPELHO DO PDF A4) ---
    texto_rank_papel = ft.Text("", size=11, color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD)
    projetos_container_papel = ft.Column(spacing=10)

    def titulo_secao_esq(texto):
        return ft.Text(texto, size=13, weight=ft.FontWeight.W_800, color=ft.Colors.WHITE, margin=ft.padding.only(top=15, bottom=2))

    def item_esq(texto):
        return ft.Text(texto, size=10, color=ft.Colors.WHITE_70)

    def titulo_secao_dir(texto):
        return ft.Container(
            content=ft.Text(texto, size=14, weight=ft.FontWeight.W_800, color="#2C3E50"),
            border=ft.border.only(bottom=ft.BorderSide(1.5, "#2C3E50")),
            margin=ft.padding.only(top=15, bottom=8), padding=ft.padding.only(bottom=2)
        )

    # Coluna Esquerda do PDF (Exatamente #2C3E50)
    col_esq_papel = ft.Container(
        width=240, bgcolor="#2C3E50", padding=ft.padding.all(25),
        content=ft.Column([
            ft.Text("Contato", size=15, weight=ft.FontWeight.W_800, color=ft.Colors.WHITE),
            ft.Divider(color=ft.Colors.WHITE_24, height=1),
            ft.Container(height=5),
            item_esq("Telefone"), item_esq("(12) 99183-8082"), ft.Container(height=5),
            item_esq("E-mail"), item_esq("mayconinveste@gmail.com"), ft.Container(height=5),
            item_esq("LinkedIn"), item_esq("linkedin.com/in/maycondis"), ft.Container(height=5),
            item_esq("GitHub"), item_esq("github.com/MayconDIS"),

            titulo_secao_esq("Competências Técnicas"), ft.Divider(color=ft.Colors.WHITE_24, height=1), ft.Container(height=5),
            item_esq("Python (Nv.5) +300 XP"), item_esq("C (Nv.4) +200 XP"),
            item_esq("C# (Nv.2) +100 XP"), item_esq("Java (Nv.2) +100 XP"),
            item_esq("Linux Zorin OS (Nv.4) +150 XP"), item_esq("Outros: POO, Cibersegurança, LGPD"),

            titulo_secao_esq("Idiomas"), ft.Divider(color=ft.Colors.WHITE_24, height=1), ft.Container(height=5),
            item_esq("Inglês (Estudando - Foco em\nconversação e tecnologia)"), ft.Container(height=5),
            item_esq("Espanhol (Básico)"),

            titulo_secao_esq("Soft Skills"), ft.Divider(color=ft.Colors.WHITE_24, height=1), ft.Container(height=5),
            item_esq("Resolução de problemas"), item_esq("Trabalho em equipe"), item_esq("Atendimento ao cliente")
        ], spacing=2)
    )

    # Coluna Direita do PDF
    col_dir_papel = ft.Container(
        expand=True, padding=ft.padding.all(35),
        content=ft.Column([
            ft.Text("Maycon Douglas", size=24, weight=ft.FontWeight.W_800, color="#2C3E50"),
            ft.Text("Estudante de Análise e Desenvolvimento de Sistemas", size=12, color=ft.Colors.BLACK_87),
            ft.Container(height=5),
            texto_rank_papel,
            ft.Text("Quest Principal (ADS): 129% Concluído", size=10, color=ft.Colors.BLACK_54),
            ft.Text("São José dos Campos, SP, Brasil", size=10, color=ft.Colors.BLACK_54),

            titulo_secao_dir("Resumo Profissional"),
            ft.Text("Estudante do 3º semestre de Análise e Desenvolvimento de Sistemas, em busca da primeira oportunidade na área de tecnologia (Estágio/Júnior). Possuo conhecimentos práticos em linguagens como Python e C, e atualmente aprofundo meus estudos em C# e Java. Entusiasta de Inteligência Artificial e Data Science.", size=10, color=ft.Colors.BLACK_87),

            titulo_secao_dir("Projetos Acadêmicos Práticos"),
            projetos_container_papel, # Live Server injetado aqui

            titulo_secao_dir("Formação Acadêmica"),
            ft.Text("Universidade Paulista (UNIP)", weight=ft.FontWeight.BOLD, size=11, color=ft.Colors.BLACK_87),
            ft.Text("CST em Análise e Desenvolvimento de Sistemas (3º Semestre)", size=10, color=ft.Colors.BLACK_87),
            ft.Text("Julho de 2025 - Previsão de Conclusão: Julho de 2027", size=9, color=ft.Colors.BLACK_54, italic=True),
            ft.Container(height=5),
            ft.Text("CEPHAS - Colégio de Educação Profissional Hélio Augusto", weight=ft.FontWeight.BOLD, size=11, color=ft.Colors.BLACK_87),
            ft.Text("Ensino Técnico em Administração", size=10, color=ft.Colors.BLACK_87),
            ft.Text("Julho de 2022 - Julho de 2023", size=9, color=ft.Colors.BLACK_54, italic=True),

            titulo_secao_dir("Histórico Profissional"),
            ft.Text("UNIP", weight=ft.FontWeight.BOLD, size=11, color=ft.Colors.BLACK_87),
            ft.Text("Auxiliar Administrativo", size=10, color=ft.Colors.BLACK_87),
            ft.Text("Outubro de 2024 - Presente", size=9, color=ft.Colors.BLACK_54, italic=True),
            ft.Container(height=5),
            ft.Text("Kinoplex", weight=ft.FontWeight.BOLD, size=11, color=ft.Colors.BLACK_87),
            ft.Text("Supervisor de Atendimento / Atendente (Diversas Unidades)", size=10, color=ft.Colors.BLACK_87),
            ft.Text("Julho de 2023 - Outubro de 2024", size=9, color=ft.Colors.BLACK_54, italic=True),
        ], spacing=2)
    )

    # Medidas EXATAS de uma folha A4 (794x1123 px)
    papel_curriculo = ft.Container(
        width=794, height=1123,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK_45, offset=ft.Offset(0, 5)),
        content=ft.Row([col_esq_papel, col_dir_papel], spacing=0, vertical_alignment=ft.CrossAxisAlignment.START, expand=True)
    )

    # --- ATUALIZAÇÕES EM TEMPO REAL ---
    def criar_card_projeto_papel(nome, tipo, data, desc, xp, is_preview=False):
        borda = ft.border.BorderSide(3, ft.Colors.RED_400) if is_preview else ft.border.BorderSide(0, ft.Colors.TRANSPARENT)
        return ft.Container(
            border=ft.border.only(left=borda),
            padding=ft.padding.only(left=8 if is_preview else 0),
            content=ft.Column([
                ft.Row([
                    ft.Text(nome, weight=ft.FontWeight.BOLD, size=11, color=ft.Colors.BLACK_87),
                    ft.Text(f"(+{xp} XP)", color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD, size=10)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(f"{tipo} | {data}", size=10, color=ft.Colors.BLACK_54, italic=True),
                ft.Text(desc, size=10, color=ft.Colors.BLACK_87)
            ], spacing=2)
        )

    def atualizar_live_server(e=None):
        projetos_container_papel.controls.clear()

        for p in dados['projetos']:
            projetos_container_papel.controls.append(
                criar_card_projeto_papel(p['nome'], p['tipo'], p['data'], p['descricao'], p['xp_ganho'])
            )

        if input_nome.value or input_tipo.value or input_desc.value:
            projetos_container_papel.controls.append(
                criar_card_projeto_papel(
                    input_nome.value if input_nome.value else "Nome do Projeto...",
                    input_tipo.value if input_tipo.value else "Tipo",
                    input_data.value if input_data.value else "Data",
                    input_desc.value if input_desc.value else "A descrição aparecerá aqui...",
                    input_xp.value if input_xp.value else "0",
                    is_preview=True
                )
            )
        page.update()

    input_nome.on_change = input_tipo.on_change = input_data.on_change = input_desc.on_change = input_xp.on_change = atualizar_live_server

    # --- PAINEL DE STATUS ---
    texto_rank = ft.Text("RANK: ...", size=14, weight=ft.FontWeight.BOLD)
    texto_xp_total = ft.Text("0 XP", size=12, color=ft.Colors.WHITE_70)

    def atualizar_status_jogador():
        total_xp, nome_rank, cor_rank = calcular_status(dados)
        texto_rank.value = f"RANK ATUAL: {nome_rank.upper()}"
        texto_rank.color = cor_rank
        texto_xp_total.value = f"Total Acumulado: {total_xp} XP"
        texto_rank_papel.value = f"Status do Jogador: Rank {nome_rank.capitalize()} ({total_xp} XP)"
        page.update()

    painel_status = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER_400, size=20),
            ft.Column([texto_rank, texto_xp_total], spacing=0)
        ]),
        bgcolor="#202020", padding=ft.padding.symmetric(horizontal=15, vertical=10), border_radius=6, margin=ft.padding.only(bottom=25)
    )

    # --- FUNÇÕES DE BOTÃO ---
    def adicionar_projeto(e):
        if not all([input_nome.value, input_tipo.value, input_data.value, input_desc.value, input_xp.value]):
            page.overlay.append(ft.SnackBar(ft.Text("Preencha todos os campos!"), bgcolor=ft.Colors.RED_700, open=True))
            page.update()
            return
        try:
            xp_int = int(input_xp.value)
        except:
            page.overlay.append(ft.SnackBar(ft.Text("O XP precisa ser um número!"), bgcolor=ft.Colors.RED_700, open=True))
            page.update()
            return

        dados['projetos'].append({"nome": input_nome.value, "tipo": input_tipo.value, "data": input_data.value, "descricao": input_desc.value, "xp_ganho": xp_int})
        salvar_dados(dados)
        
        input_nome.value = input_tipo.value = input_data.value = input_desc.value = input_xp.value = ""
        atualizar_live_server()
        atualizar_status_jogador()
        
        page.overlay.append(ft.SnackBar(ft.Text(f"Salvo! +{xp_int} XP"), bgcolor=ft.Colors.GREEN_700, open=True))
        page.update()

    async def acionar_forja(e):
        btn_forjar.content.controls[0].name = ft.Icons.HOURGLASS_TOP
        btn_forjar.content.controls[1].value = "Gerando PDF..."
        page.update()
        
        try:
            await forjar_curriculo_magia(dados)
            page.overlay.append(ft.SnackBar(ft.Text("PDF forjado com sucesso!"), bgcolor=ft.Colors.BLUE_700, open=True))
        except Exception as ex:
            page.overlay.append(ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor=ft.Colors.RED_700, open=True))
        
        btn_forjar.content.controls[0].name = ft.Icons.PICTURE_AS_PDF
        btn_forjar.content.controls[1].value = "Exportar PDF"
        page.update()

    btn_salvar = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.ADD, size=16, color=ft.Colors.WHITE), ft.Text("Adicionar Missão", size=13, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor="#2EA043", padding=12, border_radius=4, on_click=adicionar_projeto
    )

    btn_forjar = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.PICTURE_AS_PDF, size=16, color=ft.Colors.WHITE), ft.Text("Exportar PDF", size=13, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor="#238636", padding=12, border_radius=4, on_click=acionar_forja, margin=ft.padding.only(top=15)
    )

    # ==========================================
    # MONTAGEM DA TELA
    # ==========================================
    lado_esquerdo = ft.Container(
        width=380, padding=35, bgcolor="#191919", border=ft.border.only(right=ft.BorderSide(1, ft.Colors.WHITE_12)),
        content=ft.Column([
            ft.Text("Próximo Nível", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text("Preencha o formulário para atualizar o documento em tempo real.", color=ft.Colors.WHITE_54, size=11),
            ft.Divider(height=25, color="transparent"),
            painel_status, 
            ft.Text("NOVA EXPERIÊNCIA", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE_54),
            input_nome, input_tipo, input_data, input_desc, input_xp,
            ft.Container(height=5), btn_salvar, btn_forjar
        ], scroll=ft.ScrollMode.AUTO)
    )

    lado_direito = ft.Container(
        expand=True,
        bgcolor="#525659", # Fundo padrão de leitura de PDF do Chrome
        padding=40,
        content=ft.Column([papel_curriculo], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    page.add(ft.Row([lado_esquerdo, lado_direito], expand=True, spacing=0))
    
    atualizar_status_jogador()
    atualizar_live_server()

ft.run(main)