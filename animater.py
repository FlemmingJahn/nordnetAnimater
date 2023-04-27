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
    transaction_inserts = ['INDBETALING','INDSÆTTELSE', 'Straksoverførsel']
    transaction_type = ['INDBETALING', 'HÆVNING', "INDSÆTTELSE", 'Straksoverførsel']
    transaction_type_text = 'Transaktionstype'

    amount_text = 'Beløb'
    sum = [0]
    sums = [0]

    # create figure with 2 subplots
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    line, = ax.plot([], [])
    text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    title_text = fig.suptitle('My Title', fontsize=20)
    rects = 0
    def analyze(self):
        # calculate sums
        for row in data:
            if row['Transaktionstype'] in self.transaction_type:
                self.sums.append(self.sums[-1] + float(row['Beløb'].replace(".", "").replace(",", ".")))
            else:
                self.sums.append(self.sums[-1])
        self.ax2.set_title('Ind- og ud-betalinger')
        self.ax.set_title('', fontsize=40)
        self.ax.set_title('Ind- og ud-betalinger')

    def plot_line(self, row, i):
        if row[self.transaction_type_text] in self.transaction_type:
            self.sum.append(self.sum[-1] + float(row[self.amount_text].replace(".", "").replace(",", ".")))
        else:
            self.sum.append(self.sum[-1])

        # first plot: animation of sum of INDBETALING transactions
        self.ax.set_xlim(0, len(self.sums))
        self.ax.set_ylim(0, max(self.sums))

        self.line.set_data(range(i + 1), self.sum[:i + 1])
        self.text.set_text(f'Total sum: {self.sum[i]:,.0f} DKK')
        self.title_text.set_text(f'{date_text}: {data[i][posting_date_text]}')

    def plot_bars(self, index):
        for text_obj in self.ax2.texts:
            text_obj.remove()

        t = data[index]['Transaktionstype']
        if t in self.transaction_inserts:
            self.insert_sum += float(data[index]['Beløb'].replace(".", "").replace(",", "."))
        elif data[index]['Transaktionstype'] == 'HÆVNING':
            self.withdraw_sum += float(data[index]['Beløb'].replace(".", "").replace(",", "."))


        totals = [self.insert_sum, self.withdraw_sum]
        print (index, totals)
        self.rects = self.ax2.bar(['INDBETALING', 'HÆVNING'], totals, color=['green', 'red'])

        for rect, total in zip(self.rects, totals):
                rect.set_height(total)

        for u, total in enumerate(totals):
            self.ax2.text(u, total, f'{total:,.0f} DKK', ha='center')

        return self.fig

    def get_fig(self):
        return self.fig

    insert_sum = 0
    withdraw_sum = 0

    def update(self, i):
        self.plot_line(data[i], i)
        self.plot_bars(i)
        return self.line, self.text, self.title_text

    def figure(self):
        pass

class Animate():
    deposits_and_withdrawals = DepositsAndWithDrawals()

    fig = deposits_and_withdrawals.get_fig()

    def update_data(self):
        is_first_frame = True  # flag to indicate the first frame

        def update(i):
            nonlocal is_first_frame
            if is_first_frame:
                is_first_frame = False
                return None  # skip the first frame
            print (i)
            #    line.set_data(range(i+1), sums[:i+1])
            # Clear the text objects in ax2

            #self.deposits_and_withdrawals.analyze(data[i])
            return self.deposits_and_withdrawals.update(i)
        return update

    def plot(self):
        self.deposits_and_withdrawals.analyze()
        ani1 = animation.FuncAnimation(self.fig,  self.update_data(), frames=len(data), interval=0, repeat=False)
        plt.show()





animate = Animate()
animate.plot()