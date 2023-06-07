import random
class Yields():
    transaction_inserts = ['UDB.', 'MAK. UDB.']
    transaction_tax     = ['UDBYTTESKAT', 'KUPSKAT', 'MAK. UDBYTTESKAT']
    transaction_type = transaction_inserts + transaction_tax

    transaction_type_text = 'Transaktionstype'
    amount_text = 'Beløb'
    exchnage_text = 'Vekslingskurs'
    total_sums = [0]
    yield_sums = [0]
    tax_sums = [0]
    years_sum = [0]
    def __init__(self, _fig_yields, _ax, _ax_bars, fig_yield_ax3, _fig_yield_years, data):
        self.fig_yields = _fig_yields
        self.ax = _ax
        self.fig_yield_ax3 = fig_yield_ax3
        self.ax_valuta_bars = _ax_bars
        self.line_total, = _ax.plot([], [], label='Total')
        self.line_yield, = _ax.plot([], [], label='Total')
        self.line_tax, = _ax.plot([], [], label='Total')
        self.fig_yields_year = _fig_yield_years
        self.text = _ax.text(0.02, 0.75, '', transform=_ax.transAxes)
        self.valutas_table = {}
        self.stocks_table = {}
        self.years_table = {}
        self.colors = self.get_random_colors(1)
        self.data = data
        self.valuta_labels = []  # Initialize as an empty list
        self.valuta_rects = self.ax_valuta_bars.bar(0, 0, color=self.colors)
        self.analyze()
        self.stocks_rects = self.fig_yield_ax3.bar(0, 0, color=self.stock_colors)
        self.year_rects = self.fig_yields_year.bar(0, 0, color=self.years_colors)
        self.line_total_text = self.ax.text(0.40, 0.80, '', transform=self.ax.transAxes)
        self.ax.legend([f'Udbytte minus skat:', f'Udbytte:', f'Skat:'], loc='upper left')

    def init(self):
        self.total_sums = [0]
        self.yield_sums = [0]
        self.years_sum = [0]
        self.tax_sums = [0]
        self.valutas_table = {}
        self.stocks_table = {}
        self.years_table = {}
        self.analyze()
        return self.line_total, self.text, self.ax_valuta_bars.texts, self.fig_yield_ax3.texts

    def get_year(self, date_string):
        year = date_string[:4]
        return year

    def analyze(self):
        for row in self.data:
            valuta = row['Valuta']
            stock = row['Værdipapirer']
            year = self.get_year(row['Bogføringsdag'])

            if valuta not in self.valutas_table:
                self.valutas_table[valuta] = [0]
            if stock not in self.stocks_table:
                if isinstance(stock, str):
                    self.stocks_table[stock] = [0]

            if year not in self.years_table:
                self.years_table[year] = [0]

        valuta_keys = self.valutas_table.keys()
        self.colors = self.get_random_colors(len(valuta_keys))

        stock_keys = self.stocks_table.keys()
        self.stock_colors = self.get_random_colors(len(stock_keys))

        years_keys = self.years_table.keys()
        self.years_colors = self.get_random_colors(len(years_keys))

        # calculate sums
        for row in self.data:
            valuta = row['Valuta']
            stock  = row['Værdipapirer']
            year = self.get_year(row['Bogføringsdag'])
            value = float(row['Beløb'].replace(".", "").replace(",", "."))
            exchange = float(row[self.exchnage_text].replace(".", "").replace(",", "."))
            value_in_dk = value*exchange


            if row['Transaktionstype'] in self.transaction_type:
                self.total_sums.append(self.total_sums[-1] + value_in_dk)
            else:
                self.total_sums.append(self.total_sums[-1])

            if row['Transaktionstype'] in self.transaction_inserts:
                self.yield_sums.append(self.yield_sums[-1] + value_in_dk)
                for k in valuta_keys:
                    if k == valuta:
                        self.valutas_table[k].append(self.valutas_table[k][-1] + value_in_dk)
                    else:
                        self.valutas_table[k].append(self.valutas_table[k][-1])

                for k in stock_keys:
                    if k == stock:
                        self.stocks_table[k].append(self.stocks_table[k][-1] + value_in_dk)
                    else:
                        self.stocks_table[k].append(self.stocks_table[k][-1])

                for k in years_keys:
                    if k == year:
                        self.years_table[k].append(self.years_table[k][-1] + value_in_dk)
                    else:
                        self.years_table[k].append(self.years_table[k][-1])


            else:
                for k in valuta_keys:
                    self.valutas_table[k].append(self.valutas_table[k][-1])
                for k in stock_keys:
                    self.stocks_table[k].append(self.stocks_table[k][-1])

                for k in years_keys:
                    self.years_table[k].append(self.years_table[k][-1])

                self.yield_sums.append(self.yield_sums[-1])

            if row['Transaktionstype'] in self.transaction_tax:
                self.tax_sums.append(self.tax_sums[-1] - value_in_dk)
            else:
                self.tax_sums.append(self.tax_sums[-1])


        self.ax.set_title('Udbytter')
        self.ax.set_xlim(0, len(self.yield_sums))
        self.ax.set_ylim(0, max(self.yield_sums))
        self.ax_valuta_bars.set_title('Udbytter i valuta')
        self.fig_yields_year.set_title('Udbytte per år')

        self.fig_yield_ax3.set_xticklabels(stock_keys, rotation=90)
        self.fig_yield_ax3.set_title('Udbytte per aktie i danske kr.')

    def plot_line(self, i):
        if self.total_sums[:i + 1] == self.total_sums[:i]:
            return
        self.line_total.set_data(range(i + 1), self.total_sums[:i + 1])
        self.line_yield.set_data(range(i + 1), self.yield_sums[:i + 1])
        self.line_tax.set_data(range(i + 1), self.tax_sums[:i + 1])
        self.line_total_text.set_text(f'{self.yield_sums[i + 1]:,.0f} DKK')

    def get_random_colors(self, num_colors=4):
        """
        Returns a list of `num_colors` random colors.
        """
        colors = []
        for i in range(num_colors):
            hex_num = '#' + ''.join(random.choice('0123456789abcdef') for _ in range(6))
            colors.append(hex_num)
        return colors



    def plot_bars(self, index):
        self.valuta_labels = []  # Initialize as an empty list

        update_needed = False
        for v in self.valutas_table:
            if self.valutas_table[v][index + 1] != self.valutas_table[v][index]:
                update_needed = True

        if not update_needed:
            return

        keys = self.valutas_table.keys()
        totals = []
        for v in self.valutas_table:
            totals.append(self.valutas_table[v][index + 1])

        self.valuta_rects = self.ax_valuta_bars.bar(keys, totals, color=self.colors)

        for rect, total in zip(self.valuta_rects, totals):
            height = rect.get_height()
            label = self.ax_valuta_bars.text(rect.get_x() + rect.get_width() / 2, height, f'{total:,.0f} DKK', ha='center', va='bottom')
            self.valuta_labels.append(label)

        for rect, total, label in zip(self.valuta_rects, totals, self.valuta_labels):
            height = rect.get_height()
            label.set_position((rect.get_x() + rect.get_width() / 2, height))
            label.set_text(f'{total:,.0f} DKK')

    def plot_stocks(self, index):
        update_needed = False
        for v in self.stocks_table:
            if self.stocks_table[v][index + 1] != self.stocks_table[v][index]:
                update_needed = True

        if not update_needed:
            return

        for text_obj in self.fig_yield_ax3.texts:
            text_obj.remove()

        keys = self.stocks_table.keys()

        #keys = self.valutas_table.keys()

        totals = []
        for v in self.stocks_table:
            totals.append(self.stocks_table[v][index + 1])

        self.stocks_rects = self.fig_yield_ax3.bar(keys, totals, color=self.stock_colors)

        for u, total in enumerate(totals):
            self.fig_yield_ax3.text(u, total, f'{total:,.0f}', ha='center')

    def plot_years(self, index):
        update_needed = False
        for v in self.years_table:
            if self.years_table[v][index + 1] != self.years_table[v][index]:
                update_needed = True

        if not update_needed:
            return

        for text_obj in self.fig_yields_year.texts:
            text_obj.remove()

        keys = self.years_table.keys()
        totals = []
        for v in self.years_table:
            totals.append(self.years_table[v][index + 1])

        self.year_rects = self.fig_yields_year.bar(keys, totals, color=self.years_colors)

        for u, total in enumerate(totals):
            self.fig_yields_year.text(u, total, f'{total:,.0f} DKK', ha='center')

    def update(self, i):
        self.plot_line(i)
        self.plot_bars(i)
        self.plot_stocks(i)
        self.plot_years(i)

        # Update the bar label positions and text values
        for rect, total, label in zip(self.valuta_rects, [self.valutas_table['DKK'][i+1]], self.valuta_labels):
            label.set_position((rect.get_x() + rect.get_width() / 2, 0))
            label.set_text(f'{total:,.0f} DKK')

        return self.line_total, self.line_yield, self.line_tax, self.valuta_rects, self.year_rects, self.stocks_rects, self.line_total_text, self.valuta_labels
