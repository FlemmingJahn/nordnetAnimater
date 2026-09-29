class DepositsAndWithDrawals:
    transaction_inserts = ['INDBETALING', 'INDSÆTTELSE', 'Straksoverførsel']
    transaction_type = ['INDBETALING', 'HÆVNING', "INDSÆTTELSE", 'Straksoverførsel']
    transaction_type_text = 'Transaktionstype'

    amount_text = 'Beløb'
    sum = [0]
    sums = [0]

    def __init__(self, fig1, fig_ax, data):
        self.ax = fig_ax

        self.fig = fig1
        self.line, = fig_ax.plot([], [])
        self.line_text = fig_ax.text(0.04, 0.90, '', transform=fig_ax.transAxes)
        self.insert_sum = [0]
        self.withdraw_sum = [0]
        self.analyze(data)

    def init(self):
        self.sum = [0]
        self.sums = [0]
        self.insert_sum = [0]
        self.withdraw_sum = [0]

    def analyze(self, data):
        self.init()
        self.data = data
        for row in self.data:
            if row['Transaktionstype'] in self.transaction_type:
                self.sums.append(self.sums[-1] + float(row['Beløb'].replace(".", "").replace(",", ".")))
                if row['Transaktionstype'] in self.transaction_inserts:
                    self.insert_sum.append(self.insert_sum[-1] + float(row['Beløb'].replace(".", "").replace(",", ".")))
                    self.withdraw_sum.append(self.withdraw_sum[-1])
                elif row['Transaktionstype'] == 'HÆVNING':
                    self.insert_sum.append(self.insert_sum[-1])
                    self.withdraw_sum.append(self.withdraw_sum[-1] + float(row['Beløb'].replace(".", "").replace(",", ".")))
            else:
                self.sums.append(self.sums[-1])
                self.insert_sum.append(self.insert_sum[-1])
                self.withdraw_sum.append(self.withdraw_sum[-1])

        self.ax.set_title('', fontsize=40)
        self.ax.set_title('Ind- og ud-betalinger')

        if (len(self.sums) != 0):
            # The line's x-data is the transaction index (range(i + 1)), so the
            # x-axis limits must be based on the number of data points, not on
            # the money values in self.sums.
            if len(set(self.sums)) == 1:  # Check if all values in self.sums are the same
                self.ax.set_ylim(0, max(self.sums) + 1)  # Expand the limits slightly
            else:
                self.ax.set_ylim(min(0, min(self.sums)), max(self.sums))
            self.ax.set_xlim(0, len(self.sums) - 1)

    def plot_line(self, i):
        if self.sums[:i + 1] == self.sums[:i]:
            return

        self.line_text.set_text(f'Total: {self.sums[i]:,.0f} DKK')
        self.line.set_data(range(i + 1), self.sums[:i + 1])

    def update(self, i):
        self.plot_line(i)

        return self.line, self.line_text

    def figure(self):
        pass
