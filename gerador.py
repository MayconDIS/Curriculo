import json
import datetime
from jinja2 import Environment, FileSystemLoader

# 1. Carregar os dados
with open('dados.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

# 2. Sistema de Gamificação (Cálculo de XP e Rank)
total_xp = 0
for proj in dados['projetos']:
    total_xp += proj['xp_ganho']
for hab in dados['habilidades']:
    total_xp += hab['xp']

# Lógica de Ranks Competitivos
if total_xp < 500: rank = "Ferro"
elif total_xp < 1000: rank = "Bronze"
elif total_xp < 1500: rank = "Prata"
elif total_xp < 2200: rank = "Ouro"
elif total_xp < 3000: rank = "Platina"
else: rank = "Diamante"

# 3. Calcular a Quest Principal (Progresso da Faculdade)
hoje = datetime.date.today()
inicio = datetime.datetime.strptime(dados['curso']['inicio'], "%Y-%m-%d").date()
fim = datetime.datetime.strptime(dados['curso']['fim'], "%Y-%m-%d").date()

dias_totais = (fim - inicio).days
dias_passados = (hoje - inicio).days
porcentagem = int((dias_passados / dias_totais) * 100)

# Criar a barra de progresso visual (10 blocos)
blocos_preenchidos = porcentagem // 10
barra = ("█" * blocos_preenchidos) + ("░" * (10 - blocos_preenchidos))

# 4. Injetar no HTML com Jinja2
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')

html_renderizado = template.render(
    perfil=dados['perfil'],
    projetos=dados['projetos'],
    habilidades=dados['habilidades'],
    total_xp=total_xp,
    rank_atual=rank,
    barra_progresso=barra,
    porcentagem_curso=porcentagem
)

# 5. Salvar o arquivo final
with open('index_gerado.html', 'w', encoding='utf-8') as f:
    f.write(html_renderizado)

print(f"🔥 Currículo gerado com sucesso! Rank Atual: {rank} ({total_xp} XP)")