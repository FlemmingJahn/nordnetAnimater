"""Plotly-based analysis and figure building for the web visualizer.

This mirrors the numeric analysis already done in deposit.py / yields.py
(which are tied to matplotlib axes) but produces plain data structures and a
single Plotly figure with animation frames. Once sent to the browser, the
Play/Pause button and slider are driven entirely by Plotly.js client-side,
so playback is smooth and doesn't need a round-trip to the server per frame.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DEPOSIT_TRANSACTION_INSERTS = ['INDBETALING', 'INDSÆTTELSE', 'Straksoverførsel']
DEPOSIT_TRANSACTION_TYPES = ['INDBETALING', 'HÆVNING', 'INDSÆTTELSE', 'Straksoverførsel']

YIELD_TRANSACTION_INSERTS = ['UDB.', 'MAK. UDB.', 'UDBYTTE']
YIELD_TRANSACTION_TAX = ['UDBYTTESKAT', 'KUPSKAT', 'MAK. UDBYTTESKAT']
YIELD_TRANSACTION_TYPES = YIELD_TRANSACTION_INSERTS + YIELD_TRANSACTION_TAX

COLOR_PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
]


def _colors_for(keys):
    return [COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(len(keys))]


def _is_missing(value):
    return value is None or (isinstance(value, float) and value != value)


def _to_float(value):
    return float(str(value).replace(".", "").replace(",", "."))


def _get_amount_currency(row):
    """Currency of 'Beløb'. Some Nordnet exports only reliably populate the
    second 'Valuta' duplicate column (renamed 'Valuta.1' by pandas), while
    the first 'Valuta' is actually the currency of 'Samlede afgifter'."""
    if 'Valuta.1' in row and not _is_missing(row['Valuta.1']):
        return row['Valuta.1']
    return row.get('Valuta')


def _get_exchange_rate(row):
    """Exchange rate for converting 'Beløb' to DKK. Newer Nordnet exports
    frequently leave 'Vekslingskurs' blank and use 'Middelkurs' instead;
    when both are blank the transaction is already in DKK (rate 1)."""
    for col in ('Vekslingskurs', 'Middelkurs'):
        value = row.get(col)
        if not _is_missing(value):
            return _to_float(value)
    return 1.0


def _get_year(date_string):
    return str(date_string)[:4]


def analyze_deposits(data):
    """Running totals of deposits/withdrawals, one entry per transaction
    (plus a leading 0), matching DepositsAndWithDrawals.analyze()."""
    sums = [0.0]
    insert_sum = [0.0]
    withdraw_sum = [0.0]

    for row in data:
        ttype = row['Transaktionstype']
        if ttype in DEPOSIT_TRANSACTION_TYPES:
            amount = _to_float(row['Beløb'])
            sums.append(sums[-1] + amount)
            if ttype in DEPOSIT_TRANSACTION_INSERTS:
                insert_sum.append(insert_sum[-1] + amount)
                withdraw_sum.append(withdraw_sum[-1])
            else:  # HÆVNING
                insert_sum.append(insert_sum[-1])
                withdraw_sum.append(withdraw_sum[-1] + amount)
        else:
            sums.append(sums[-1])
            insert_sum.append(insert_sum[-1])
            withdraw_sum.append(withdraw_sum[-1])

    return {"sums": sums, "insert_sum": insert_sum, "withdraw_sum": withdraw_sum}


def analyze_yields(data):
    """Running totals of yields/tax plus per-currency/stock/year
    breakdowns, matching Yields.analyze()."""
    valutas_table, stocks_table, years_table = {}, {}, {}

    for row in data:
        valutas_table.setdefault(_get_amount_currency(row), [0.0])
        stock = row['Værdipapirer']
        if isinstance(stock, str):
            stocks_table.setdefault(stock, [0.0])
        years_table.setdefault(_get_year(row['Bogføringsdag']), [0.0])

    total_sums, yield_sums, tax_sums = [0.0], [0.0], [0.0]

    for row in data:
        ttype = row['Transaktionstype']
        valuta = _get_amount_currency(row)
        stock = row['Værdipapirer']
        year = _get_year(row['Bogføringsdag'])
        value_dk = _to_float(row['Beløb']) * _get_exchange_rate(row)

        total_sums.append(total_sums[-1] + value_dk if ttype in YIELD_TRANSACTION_TYPES else total_sums[-1])

        is_insert = ttype in YIELD_TRANSACTION_INSERTS
        yield_sums.append(yield_sums[-1] + value_dk if is_insert else yield_sums[-1])

        for k in valutas_table:
            add = value_dk if (is_insert and k == valuta) else 0.0
            valutas_table[k].append(valutas_table[k][-1] + add)
        for k in stocks_table:
            add = value_dk if (is_insert and k == stock) else 0.0
            stocks_table[k].append(stocks_table[k][-1] + add)
        for k in years_table:
            add = value_dk if (is_insert and k == year) else 0.0
            years_table[k].append(years_table[k][-1] + add)

        tax_sums.append(tax_sums[-1] - value_dk if ttype in YIELD_TRANSACTION_TAX else tax_sums[-1])

    return {
        "total_sums": total_sums,
        "yield_sums": yield_sums,
        "tax_sums": tax_sums,
        "valutas_table": valutas_table,
        "stocks_table": stocks_table,
        "years_table": years_table,
    }


def _sample_indices(n, max_frames):
    if n <= max_frames:
        return list(range(n))
    step = (n - 1) / (max_frames - 1)
    indices = sorted({round(i * step) for i in range(max_frames)})
    if indices[-1] != n - 1:
        indices.append(n - 1)
    return indices


def build_figure(data, max_frames=200, frame_duration_ms=60):
    """Build a single Plotly figure (3x3-ish grid) with animation frames
    covering the whole transaction history, plus Play/Pause + a slider.
    """
    deposits = analyze_deposits(data)
    yields_ = analyze_yields(data)
    n = len(data)

    specs = [
        [{}, {}, None],
        [{}, {}, {}],
        [{"colspan": 3}, None, None],
    ]
    fig = make_subplots(
        rows=3, cols=3, specs=specs,
        subplot_titles=(
            "Ind- og udbetalinger (total)", "Ind- og udbetalinger",
            "Udbytte", "Udbytte pr. valuta", "Udbytte pr. år",
            "Udbytte pr. aktie",
        ),
        vertical_spacing=0.12, horizontal_spacing=0.08,
    )

    valuta_keys = list(yields_["valutas_table"].keys())
    year_keys = list(yields_["years_table"].keys())
    stock_keys = list(yields_["stocks_table"].keys())

    # --- initial (frame 0) traces, in a fixed order matched by `traces=` below ---
    fig.add_trace(go.Scatter(x=[0], y=[deposits["sums"][0]], mode="lines", name="Total"), row=1, col=1)
    fig.add_trace(go.Bar(x=["INDBETALING", "HÆVNING"], y=[0, 0], marker_color=["green", "red"], name="Ind/hæv"), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0], y=[yields_["total_sums"][0]], mode="lines", name="Udbytte efter skat"), row=2, col=1)
    fig.add_trace(go.Scatter(x=[0], y=[yields_["yield_sums"][0]], mode="lines", name="Udbytte"), row=2, col=1)
    fig.add_trace(go.Scatter(x=[0], y=[yields_["tax_sums"][0]], mode="lines", name="Skat"), row=2, col=1)
    fig.add_trace(go.Bar(x=valuta_keys, y=[0] * len(valuta_keys), marker_color=_colors_for(valuta_keys), name="Valuta"), row=2, col=2)
    fig.add_trace(go.Bar(x=year_keys, y=[0] * len(year_keys), marker_color=_colors_for(year_keys), name="År"), row=2, col=3)
    fig.add_trace(go.Bar(x=stock_keys, y=[0] * len(stock_keys), marker_color=_colors_for(stock_keys), name="Aktie"), row=3, col=1)

    fig.update_yaxes(range=[0, max(deposits["sums"]) * 1.05 + 1], row=1, col=1)
    fig.update_yaxes(range=[min(deposits["withdraw_sum"] + [0]), max(deposits["insert_sum"]) * 1.05 + 1], row=1, col=2)
    fig.update_yaxes(range=[0, max(yields_["yield_sums"]) * 1.05 + 1], row=2, col=1)
    if valuta_keys:
        fig.update_yaxes(range=[0, max(v[-1] for v in yields_["valutas_table"].values()) * 1.2 + 1], row=2, col=2)
    if year_keys:
        fig.update_yaxes(range=[0, max(v[-1] for v in yields_["years_table"].values()) * 1.2 + 1], row=2, col=3)
    if stock_keys:
        fig.update_yaxes(range=[0, max(v[-1] for v in yields_["stocks_table"].values()) * 1.2 + 1], row=3, col=1)
        fig.update_xaxes(tickangle=90, row=3, col=1)

    # --- animation frames ---
    frames = []
    for i in _sample_indices(n, max_frames):
        x = list(range(i + 1))
        frame_data = [
            go.Scatter(x=x, y=deposits["sums"][:i + 1]),
            go.Bar(y=[deposits["insert_sum"][i + 1], deposits["withdraw_sum"][i + 1]]),
            go.Scatter(x=x, y=yields_["total_sums"][:i + 1]),
            go.Scatter(x=x, y=yields_["yield_sums"][:i + 1]),
            go.Scatter(x=x, y=yields_["tax_sums"][:i + 1]),
            go.Bar(y=[yields_["valutas_table"][k][i + 1] for k in valuta_keys]),
            go.Bar(y=[yields_["years_table"][k][i + 1] for k in year_keys]),
            go.Bar(y=[yields_["stocks_table"][k][i + 1] for k in stock_keys]),
        ]
        frames.append(go.Frame(
            data=frame_data,
            name=str(i),
            traces=list(range(len(frame_data))),
            layout=go.Layout(annotations=[
                dict(
                    text=f"Total ind/hæv: {deposits['sums'][i + 1]:,.0f} DKK &nbsp;|&nbsp; "
                         f"Udbytte efter skat: {yields_['total_sums'][i + 1]:,.0f} DKK",
                    xref="paper", yref="paper", x=0.5, y=1.08,
                    showarrow=False, font=dict(size=14),
                )
            ]),
        ))
    fig.frames = frames

    slider_steps = [
        {"args": [[f.name], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
         "label": f.name, "method": "animate"}
        for f in frames
    ]

    fig.update_layout(
        height=850,
        showlegend=False,
        margin=dict(t=90, b=40),
        updatemenus=[{
            "type": "buttons", "showactive": False, "x": 0.05, "y": 1.12, "xanchor": "left",
            "buttons": [
                {"label": "▶ Play", "method": "animate",
                 "args": [None, {"frame": {"duration": frame_duration_ms, "redraw": True},
                                  "fromcurrent": True, "transition": {"duration": 0}}]},
                {"label": "⏸ Pause", "method": "animate",
                 "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate", "transition": {"duration": 0}}]},
            ],
        }],
        sliders=[{
            "active": 0, "x": 0.15, "len": 0.8, "y": 1.12,
            "currentvalue": {"prefix": "Transaktion: "},
            "steps": slider_steps,
        }],
    )

    return fig
