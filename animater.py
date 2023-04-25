import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation

date_text = "Dato"
posting_date_text = "Bogføringsdag"

filename = 'C:/tmp/inbetalinger.csv'
# read data from csv file
with open(filename, 'r', encoding='utf-16') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    data = [row for row in reversed(list(reader))]








# show the plots
class DepositsAndWithDrawals():
    transaction_type = ['INDBETALING', 'HÆVNING']
    transaction_type_text = 'Transaktionstype'
    amount_text = 'Beløb'
    sum = [0]

    # create figure with 2 subplots
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    line, = ax.plot([], [])
    text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    title_text = fig.suptitle('My Title', fontsize=20)
    rects = 0
    def analyze(self, row):
        if row[self.transaction_type_text] in self.transaction_type:
            self.sum.append(self.sum[-1] + float(row[self.amount_text].replace(".", "").replace(",", ".")))
        else:
            self.sum.append(self.sum[-1])

    def deposits_bars(self):
        # calculate sums
        sums = [0]
        for row in data:
            if row['Transaktionstype'] in ['INDBETALING', 'HÆVNING']:
                sums.append(sums[-1] + float(row['Beløb'].replace(".", "").replace(",", ".")))
            else:
                sums.append(sums[-1])



        # first plot: animation of sum of INDBETALING transactions
        self.ax.set_xlim(0, len(sums))
        self.ax.set_ylim(0, max(sums))
        self.ax.set_title('', fontsize=40)


        # second plot: bar chart of total amount of INDBETALING and HÆVNING transactions
        indbetaling_sum = 0
        haevning_sum = 0

        for row in data:
            if row['Transaktionstype'] == 'INDBETALING':
                indbetaling_sum += float(row['Beløb'].replace(".", "").replace(",", "."))
            elif row['Transaktionstype'] == 'HÆVNING':
                haevning_sum += float(row['Beløb'].replace(".", "").replace(",", "."))
        totals = [indbetaling_sum * 1.2, haevning_sum]

        self.rects = self.ax2.bar(['INDBETALING', 'HÆVNING'], totals, color=['green', 'red'])

        self.ax2.set_title('Ind- og ud-betalinger')
        self.ax.set_title('Ind- og ud-betalinger')
        for i, total in enumerate(totals):
            self.ax2.text(i, total + 0.1 * max(totals) / 2, f'{total:,.0f} DKK', ha='center')
        return self.fig

    def update(self, i):
        insert_sum = 0
        withdraw_sum = 0

        for text_obj in self.ax2.texts:
            text_obj.remove()

        self.line.set_data(range(i + 1), self.sum[:i + 1])

        self.text.set_text(f'Total sum: {self.sum[i]:,.0f} DKK')
        self.title_text.set_text(f'{date_text}: {data[i][posting_date_text]}')

        if data[i]['Transaktionstype'] == 'INDBETALING':
            insert_sum += float(data[i]['Beløb'].replace(".", "").replace(",", "."))
        elif data[i]['Transaktionstype'] == 'HÆVNING':
            withdraw_sum += float(data[i]['Beløb'].replace(".", "").replace(",", "."))

        totals = [insert_sum, withdraw_sum]

        for rect, total in zip(self.rects, totals):
            rect.set_height(total)

        for u, total in enumerate(totals):
            self.ax2.text(u, total + 0.1 * max(totals) / 2, f'{total:,.0f} DKK', ha='center')

        return self.line, self.text, self.title_text
    def figure(self):
        pass
class Animate():
    deposits_and_withdrawals = DepositsAndWithDrawals()
    deposits_and_withdrawals2 = DepositsAndWithDrawals()

    fig = deposits_and_withdrawals.deposits_bars()
    fig2 = deposits_and_withdrawals.deposits_bars()



    def update_data(self):
        def update(i):
            #    line.set_data(range(i+1), sums[:i+1])
            # Clear the text objects in ax2

            self.deposits_and_withdrawals.analyze(data[i])
            return self.deposits_and_withdrawals.update(i)


        return update

    def update_data2(self):
        def update(i):
            #    line.set_data(range(i+1), sums[:i+1])
            # Clear the text objects in ax2

            self.deposits_and_withdrawals.analyze(data[i])
            return self.deposits_and_withdrawals.update(i)


        return update

    def plot(self):
        my_update_data = self.update_data()
        my_update_data2 = self.update_data2()
        ani1 = animation.FuncAnimation(self.fig, my_update_data, frames=len(data), interval=0, repeat=False)
        plt.show()





animate = Animate()
animate.plot()