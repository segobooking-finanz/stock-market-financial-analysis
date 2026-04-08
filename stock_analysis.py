import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np

# ── Configuración ──────────────────────────────────────────────────
tickers = ['^GSPC', 'AAPL', 'JPM', 'JNJ', 'AMZN']
nombres = {'^GSPC': 'S&P 500', 'AAPL': 'Apple',
           'JPM': 'JPMorgan', 'JNJ': 'Johnson & Johnson',
           'AMZN': 'Amazon'}

COLORS = ['#2ea043', '#388bfd', '#f78166', '#d2a8ff', '#ffa657']

# ── Estilo ─────────────────────────────────────────────────────────
plt.rcParams['figure.facecolor'] = '#0d1117'
plt.rcParams['axes.facecolor']   = '#161b22'
plt.rcParams['axes.edgecolor']   = '#30363d'
plt.rcParams['text.color']       = '#e6edf3'
plt.rcParams['axes.labelcolor']  = '#e6edf3'
plt.rcParams['xtick.color']      = '#8b949e'
plt.rcParams['ytick.color']      = '#8b949e'
plt.rcParams['grid.color']       = '#21262d'

# ── Descargar datos ────────────────────────────────────────────────
print('Descargando datos...')
data = yf.download(tickers=tickers, start='2020-01-01',
                   end='2024-12-31', auto_adjust=True)
precios = data['Close']
precios.columns = [nombres[t] for t in precios.columns]
print(f'✅ {len(precios)} días de trading descargados')

# ── Calcular retornos diarios ──────────────────────────────────────
retornos = precios.pct_change().dropna()

# ── Retorno acumulado ──────────────────────────────────────────────
retorno_acum = (1 + retornos).cumprod() - 1

# ══════════════════════════════════════════════════════════════════
# GRÁFICO 1 — Precio Normalizado (base 100)
# ══════════════════════════════════════════════════════════════════
precio_norm = precios / precios.iloc[0] * 100

fig, ax = plt.subplots(figsize=(14, 7))
for i, col in enumerate(precio_norm.columns):
    ax.plot(precio_norm.index, precio_norm[col],
            label=col, color=COLORS[i], linewidth=1.8)

# Marcar eventos clave
ax.axvline(pd.Timestamp('2020-03-23'), color='#ff7b72',
           linestyle='--', alpha=0.7, label='COVID Crash (Mar 2020)')
ax.axvline(pd.Timestamp('2022-01-03'), color='#ffa657',
           linestyle='--', alpha=0.7, label='Fed Rate Hikes Begin (2022)')
ax.axvline(pd.Timestamp('2023-01-01'), color='#2ea043',
           linestyle='--', alpha=0.7, label='Recovery (2023)')

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}'))
ax.set_title('Normalized Price Performance — Base 100 (Jan 2020 = 100)',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Date')
ax.set_ylabel('Normalized Price (Base 100)')
ax.legend(loc='upper left', fontsize=9)
ax.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig(r'C:\ecommerce\stock_01_normalized_price.png', dpi=150, bbox_inches='tight')
plt.show()
print('✅ Gráfico 1 guardado')

# ══════════════════════════════════════════════════════════════════
# GRÁFICO 2 — Retorno Total por Activo
# ══════════════════════════════════════════════════════════════════
retorno_total = (precios.iloc[-1] / precios.iloc[0] - 1) * 100
retorno_total = retorno_total.sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
colors_bar = [COLORS[list(nombres.values()).index(n)] 
              if n in nombres.values() else '#888' 
              for n in retorno_total.index]
bars = ax.barh(retorno_total.index, retorno_total.values,
               color=colors_bar, alpha=0.85)
for bar, val in zip(bars, retorno_total.values):
    ax.text(val + 1, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=11, fontweight='bold')
ax.axvline(0, color='white', linewidth=0.8, alpha=0.5)
ax.set_title('Total Return 2020–2024 (%)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Total Return (%)')
ax.grid(True, axis='x', alpha=0.4)
plt.tight_layout()
plt.savefig(r'C:\ecommerce\stock_02_total_return.png', dpi=150, bbox_inches='tight')
plt.show()
print('✅ Gráfico 2 guardado')

# ══════════════════════════════════════════════════════════════════
# GRÁFICO 3 — Volatilidad Anualizada (Rolling 30 días)
# ══════════════════════════════════════════════════════════════════
volatilidad = retornos.rolling(30).std() * np.sqrt(252) * 100

fig, ax = plt.subplots(figsize=(14, 7))
for i, col in enumerate(volatilidad.columns):
    ax.plot(volatilidad.index, volatilidad[col],
            label=col, color=COLORS[i], linewidth=1.5, alpha=0.85)
ax.axvline(pd.Timestamp('2020-03-23'), color='#ff7b72',
           linestyle='--', alpha=0.7, label='COVID Peak Volatility')
ax.set_title('30-Day Rolling Annualized Volatility (%)',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Date')
ax.set_ylabel('Annualized Volatility (%)')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig(r'C:\ecommerce\stock_03_volatility.png', dpi=150, bbox_inches='tight')
plt.show()
print('✅ Gráfico 3 guardado')

# ══════════════════════════════════════════════════════════════════
# GRÁFICO 4 — Matriz de Correlación
# ══════════════════════════════════════════════════════════════════
correlacion = retornos.corr()

fig, ax = plt.subplots(figsize=(9, 7))
mask = np.triu(np.ones_like(correlacion, dtype=bool), k=1)
sns.heatmap(correlacion, annot=True, fmt='.2f', cmap='RdYlGn',
            ax=ax, linewidths=0.5, linecolor='#30363d',
            vmin=-1, vmax=1, center=0,
            cbar_kws={'label': 'Correlation'})
ax.set_title('Return Correlation Matrix (2020–2024)',
             fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(r'C:\ecommerce\stock_04_correlation.png', dpi=150, bbox_inches='tight')
plt.show()
print('✅ Gráfico 4 guardado')

# ══════════════════════════════════════════════════════════════════
# GRÁFICO 5 — Risk vs Return (Scatter)
# ══════════════════════════════════════════════════════════════════
retorno_anual = retornos.mean() * 252 * 100
riesgo_anual  = retornos.std() * np.sqrt(252) * 100
sharpe        = retorno_anual / riesgo_anual

fig, ax = plt.subplots(figsize=(10, 7))
for i, activo in enumerate(retorno_anual.index):
    ax.scatter(riesgo_anual[activo], retorno_anual[activo],
               s=200, color=COLORS[i], zorder=5,
               edgecolors='white', linewidth=0.8)
    ax.annotate(f'{activo}\nSharpe: {sharpe[activo]:.2f}',
                (riesgo_anual[activo], retorno_anual[activo]),
                textcoords='offset points', xytext=(12, 5),
                fontsize=9, color='#e6edf3')

ax.axhline(0, color='white', linewidth=0.5, alpha=0.5)
ax.set_title('Risk vs Return — Annualized (2020–2024)',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Annualized Risk / Volatility (%)')
ax.set_ylabel('Annualized Return (%)')
ax.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig(r'C:\ecommerce\stock_05_risk_return.png', dpi=150, bbox_inches='tight')
plt.show()
print('✅ Gráfico 5 guardado')

# ══════════════════════════════════════════════════════════════════
# GRÁFICO 6 — Retorno por Año
# ══════════════════════════════════════════════════════════════════
retorno_x_anio = retornos.groupby(retornos.index.year).apply(
    lambda x: (1 + x).prod() - 1
) * 100

fig, ax = plt.subplots(figsize=(14, 7))
x = np.arange(len(retorno_x_anio.index))
width = 0.15
for i, col in enumerate(retorno_x_anio.columns):
    bars = ax.bar(x + i * width, retorno_x_anio[col],
                  width=width, label=col,
                  color=COLORS[i], alpha=0.85)

ax.axhline(0, color='white', linewidth=0.8, alpha=0.5)
ax.set_xticks(x + width * 2)
ax.set_xticklabels(retorno_x_anio.index)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))
ax.set_title('Annual Returns by Asset (2020–2024)',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Year')
ax.set_ylabel('Annual Return (%)')
ax.legend(fontsize=9)
ax.grid(True, axis='y', alpha=0.4)
plt.tight_layout()
plt.savefig(r'C:\ecommerce\stock_06_annual_returns.png', dpi=150, bbox_inches='tight')
plt.show()
print('✅ Gráfico 6 guardado')

# ── Guardar métricas en CSV ────────────────────────────────────────
metricas = pd.DataFrame({
    'Total Return (%)': retorno_total,
    'Ann. Return (%)': retorno_anual.round(2),
    'Ann. Volatility (%)': riesgo_anual.round(2),
    'Sharpe Ratio': sharpe.round(3)
})
metricas.to_csv(r'C:\ecommerce\stock_metrics.csv')
print('\n📊 Métricas:')
print(metricas.to_string())
print('\n🎉 Análisis completo guardado')
