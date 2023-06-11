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
    def __init__(self, _fig_yields, _ax, ax_valuta_bars, ax_years_bars, ax_stocks_bars, data):
        self.fig_yields = _fig_yields
        self.ax = _ax
        self.line_total, = _ax.plot([], [], label='Total')
        self.line_yield, = _ax.plot([], [], label='Total')
        self.line_tax, = _ax.plot([], [], label='Total')
        self.text = _ax.text(0.02, 0.75, '', transform=_ax.transAxes)
        self.colors = self.get_random_colors(1)

        #
        # Stocks
        #
        self.stocks_table = {}
        self.ax_stocks_bars = ax_stocks_bars
        self.stocks_labels = []  # Initialize as an empty list
        self.stocks_rects = self.ax_stocks_bars.bar(0, 0, color=self.colors)


        #
        # Valuta
        #
        self.valutas_table = {}
        self.ax_valuta_bars = ax_valuta_bars
        self.valuta_labels = []  # Initialize as an empty list
        self.valuta_rects = self.ax_valuta_bars.bar(0, 0, color=self.colors)

        #
        # Years
        #
        self.years_table = {}
        self.ax_years_bars = ax_years_bars
        self.years_labels = []  # Initialize as an empty list
        self.years_rects = self.ax_years_bars.bar(0, 0, color=self.colors)

        #
        #
        #
        self.analyze(data)
        self.line_total_text = self.ax.text(0.05, 0.60, '', transform=self.ax.transAxes)
        self.line_tax_text = self.ax.text(0.05, 0.50, '', transform=self.ax.transAxes)
        self.line_yeilds_after_tax_text = self.ax.text(0.05, 0.40, '', transform=self.ax.transAxes)
        self.ax.legend([f'Udbytte minus skat:', f'Udbytte:', f'Skat:'], loc='upper left')

    def init(self):
        self.valutas_table = {}
        self.years_table = {}
        self.stocks_table = {}
    def get_year(self, date_string):
        year = date_string[:4]
        return year

    def analyze(self, data):
        self.init()
        self.data = data
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

        ##
        ## stocks
        ##
        keys = self.stocks_table.keys()
        totals = []
        for v in self.stocks_table:
            totals.append(0)

        self.ax_stocks_bars.set_title('Udbytter i valuta')
        self.stock_rects = self.ax_stocks_bars.bar(keys, totals, color=self.colors)
        all_values = [num for sublist in self.stocks_table.values() for num in sublist]
        max_value = max(all_values) * 1.2
        self.ax_stocks_bars.set_ylim(0, max_value)

        self.ax_stocks_bars.set_xticklabels(stock_keys, rotation=90)
        self.ax_stocks_bars.set_title('Udbytte per aktie i danske kr.')


        ##
        ## Valuta
        ##
        keys = self.valutas_table.keys()
        totals = []
        for v in self.valutas_table:
            totals.append(0)

        self.ax_valuta_bars.set_title('Udbytter i valuta')
        self.valuta_rects = self.ax_valuta_bars.bar(keys, totals, color=self.colors)
        all_values = [num for sublist in self.valutas_table.values() for num in sublist]
        max_value = max(all_values) * 1.2
        self.ax_valuta_bars.set_ylim(0, max_value)

        ##
        ## Years
        ##
        keys = self.years_table.keys()
        keys = self.years_table.keys()
        totals = []
        for v in self.years_table:
            totals.append(0)

        self.ax_years_bars.set_title('Udbytter per år')
        self.years_rects = self.ax_years_bars.bar(keys, totals, color=self.colors)
        all_values = [num for sublist in self.years_table.values() for num in sublist]
        max_value = max(all_values) * 1.2
        self.ax_years_bars.set_ylim(0, max_value)

    def plot_line(self, i):
        if self.total_sums[:i + 1] == self.total_sums[:i]:
            return
        self.line_total.set_data(range(i + 1), self.total_sums[:i + 1])
        self.line_yield.set_data(range(i + 1), self.yield_sums[:i + 1])
        self.line_tax.set_data(range(i + 1), self.tax_sums[:i + 1])
        self.line_total_text.set_text(f'Udbytte {self.yield_sums[i + 1]:,.0f} DKK')
        self.line_tax_text.set_text(f'Skat {self.tax_sums[i + 1]:,.0f} DKK')
        self.line_yeilds_after_tax_text.set_text(f'Udbytte efter skat {self.total_sums[i + 1]:,.0f} DKK')

    def get_random_colors(self, num_colors=4):
        """
        Returns a list of `num_colors` random colors.
        """
        colors = []
        for i in range(num_colors):
            hex_num = '#' + ''.join(random.choice('0123456789abcdef') for _ in range(6))
            colors.append(hex_num)
        return colors



    def plot_valuta_bars(self, index):
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
        self.valuta_labels = []
        for rect, total in zip(self.valuta_rects, totals):
            height = rect.get_height()
            label = self.ax_valuta_bars.text(rect.get_x() + rect.get_width() / 2, height, f'{total:,.0f} DKK', ha='center', va='bottom')
            self.valuta_labels.append(label)


    def plot_stocks(self, index):
        update_needed = False
        for v in self.stocks_table:
            if self.stocks_table[v][index + 1] != self.stocks_table[v][index]:
                update_needed = True

        if not update_needed:
            return

        keys = self.stocks_table.keys()

        totals = []
        for v in self.stocks_table:
            totals.append(self.stocks_table[v][index + 1])

        self.stocks_rects = self.ax_stocks_bars.bar(keys, totals, color=self.stock_colors)

        self.stocks_labels = []
        for rect, total in zip(self.stocks_rects, totals):
            height = rect.get_height()
            label = self.ax_stocks_bars.text(rect.get_x() + rect.get_width() / 2, height, f'{total:,.0f}', ha='center', va='bottom')
            self.stocks_labels.append(label)


    def plot_years(self, index):
        update_needed = False
        for v in self.years_table:
            if self.years_table[v][index + 1] != self.years_table[v][index]:
                update_needed = True

        if not update_needed:
            return

        keys = self.years_table.keys()
        totals = []
        for v in self.years_table:
            totals.append(self.years_table[v][index + 1])

        self.years_rects = self.ax_years_bars.bar(keys, totals, color=self.years_colors)
        self.years_labels = []
        for rect, total in zip(self.years_rects, totals):
            height = rect.get_height()
            label = self.ax_years_bars.text(rect.get_x() + rect.get_width() / 2, height, f'{total:,.0f} DKK', ha='center', va='bottom')
            self.years_labels.append(label)


    def update(self, i):
        self.plot_line(i)
        self.plot_valuta_bars(i)
        self.plot_stocks(i)
        self.plot_years(i)
        return self.line_total, self.line_yield, self.line_tax, self.valuta_rects, self.years_rects, self.stocks_rects, self.line_total_text, self.line_tax_text, self.line_yeilds_after_tax_text, self.valuta_labels, self.years_labels, self.stocks_labels
