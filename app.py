import flet as ft
import json
import os
import subprocess
from datetime import datetime

ARQUIVO_JSON = 'dados.json'

# --- FUNÇÕES DE DADOS E LÓGICA ---
def carregar_dados():
    with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def calcular_status(dados):
    total_xp = sum(p['xp_ganho'] for p in dados['projetos']) + sum(h['xp'] for h in dados['habilidades'])
    if total_xp < 500: rank = "Ferro", ft.colors.BLUE_GREY_400
    elif total_xp < 1000: rank = "Bronze", ft.colors.BROWN_400
    elif total_xp < 1500: rank = "Prata", ft.colors.GREY_400
    elif total_xp < 2200: rank = "Ouro", ft.colors.AMBER_400
    elif total_xp < 3000: rank = "Platina", ft.colors.CYAN_300
    else: rank = "Diamante", ft.colors.PURPLE_300
    return total_xp, rank[0], rank[1]

# --- INTERFACE GRÁFICA COM FLET ---
def main(page: ft.Page):
    # Configurações da Janela 1920x1200
    page.title = "Sistema de Progressão Profissional - Nível ADS"
    page.window_width = 1920
    page.window_height = 1200
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 40
    page.bgcolor = "#1a1c23" # Fundo escuro gamer

    dados = carregar_dados()

    # --- COMPONENTES VISUAIS ---
    texto_rank = ft.Text(size=30, weight=ft.FontWeight.BOLD)
    texto_xp = ft.Text(size=20, color=ft.colors.WHITE70)
    lista_projetos = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=400)

    def atualizar_dashboard():
        total_xp, nome_rank, cor_rank = calcular_status(dados)
        texto_rank.value = f"RANK ATUAL: {nome_rank.upper()}"
        texto_rank.color = cor_rank
        texto_xp.value = f"Total Acumulado: {total_xp} XP"
        
        lista_projetos.controls.clear()
        for p in reversed(dados['projetos']): # Mostra os mais recentes primeiro
            card = ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Text(p['nome'], weight=ft.FontWeight.BOLD, size=16),
                        ft.Text(p['tipo'], size=12, color=ft.colors.WHITE54),
                        ft.Text(f"+{p['xp_ganho']} XP", color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD)
                    ])
                ),
                color="#2d323e"
            )
            lista_projetos.controls.append(card)
        page.update()

    # --- FUNÇÕES DE AÇÃO ---
    def adicionar_projeto(e):
        if not all([input_nome.value, input_tipo.value, input_data.value, input_desc.value, input_xp.value]):
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos da Quest!"), bgcolor=ft.colors.RED_700)
            page.snack_bar.open = True
            page.update()
            return

        try:
            xp_int = int(input_xp.value)
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("O XP precisa ser um número!"), bgcolor=ft.colors.RED_700)
            page.snack_bar.open = True
            page.update()
            return

        novo_projeto = {
            "nome": input_nome.value,
            "tipo": input_tipo.value,
            "data": input_data.value,
            "descricao": input_desc.value,
            "xp_ganho": xp_int
        }
        
        dados['projetos'].append(novo_projeto)
        salvar_dados(dados)
        atualizar_dashboard()

        # Limpar campos
        input_nome.value = input_tipo.value = input_data.value = input_desc.value = input_xp.value = ""
        
        page.snack_bar = ft.SnackBar(ft.Text(f"Missão Concluída! +{xp_int} XP Adicionado."), bgcolor=ft.colors.GREEN_700)
        page.snack_bar.open = True
        page.update()

    def gerar_curriculo(e):
        try:
            # Chama o seu script gerador.py
            subprocess.run(["python", "gerador.py"], check=True)
            page.snack_bar = ft.SnackBar(ft.Text("Item Forjado! Currículo HTML atualizado com sucesso."), bgcolor=ft.colors.BLUE_700)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao forjar: {ex}"), bgcolor=ft.colors.RED_700)
        
        page.snack_bar.open = True
        page.update()

    # --- LAYOUT DO FORMULÁRIO (ESQUERDA) ---
    input_nome = ft.TextField(label="Nome do Projeto (Ex: API em Python)", width=600)
    input_tipo = ft.TextField(label="Tipo (Ex: Projeto Integrado)", width=600)
    input_data = ft.TextField(label="Data (Ex: Março de 2026)", width=600)
    input_desc = ft.TextField(label="Descrição da Missão", multiline=True, width=600)
    input_xp = ft.TextField(label="Recompensa de XP (Ex: 300)", width=600)
    
    btn_adicionar = ft.ElevatedButton("Completar Quest (+XP)", icon=ft.icons.ADD_TASK, on_click=adicionar_projeto, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE, width=600, height=50)

    coluna_formulario = ft.Column([
        ft.Text("ADICIONAR NOVA MISSÃO", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_300),
        input_nome, input_tipo, input_data, input_desc, input_xp, btn_adicionar
    ], spacing=15)

    # --- LAYOUT DO INVENTÁRIO (DIREITA) ---
    coluna_inventario = ft.Column([
        ft.Text("INVENTÁRIO DE PROJETOS", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_300),
        lista_projetos
    ], spacing=15)

    # --- CABEÇALHO DE STATUS ---
    painel_status = ft.Container(
        content=ft.Column([texto_rank, texto_xp], alignment=ft.MainAxisAlignment.CENTER),
        padding=30,
        bgcolor="#2d323e",
        border_radius=15,
        width=page.window_width
    )

    # BOTÃO GIGANTE DE AÇÃO
    btn_gerar = ft.ElevatedButton(
        "FORJAR CURRÍCULO (GERAR HTML)", 
        icon=ft.icons.HARDWARE, 
        on_click=gerar_curriculo, 
        bgcolor=ft.colors.BLUE_700, 
        color=ft.colors.WHITE, 
        width=page.window_width, 
        height=80,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )

    # --- MONTAGEM DA PÁGINA ---
    page.add(
        painel_status,
        ft.Divider(height=40, color=ft.colors.TRANSPARENT),
        ft.Row([coluna_formulario, ft.VerticalDivider(width=40, color=ft.colors.TRANSPARENT), coluna_inventario], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START),
        ft.Divider(height=40, color=ft.colors.TRANSPARENT),
        btn_gerar
    )

    atualizar_dashboard()

ft.app(target=main)