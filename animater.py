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

# calculate sums
sums = [0]
for row in data:
    if row['Transaktionstype'] in ['INDBETALING', 'HÆVNING']:
        sums.append(sums[-1] + float(row['Beløb'].replace(".", "").replace(",", ".")))
    else:
        sums.append(sums[-1])

# create figure with 2 subplots
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# first plot: animation of sum of INDBETALING transactions
ax.set_xlim(0, len(sums))
ax.set_ylim(0, max(sums))
ax.set_title('', fontsize=40)
line, = ax.plot([], [])
text = ax.text(0.02, 0.95, '', transform=ax.transAxes)


# second plot: bar chart of total amount of INDBETALING and HÆVNING transactions
indbetaling_sum = 0
haevning_sum = 0

for row in data:
    if row['Transaktionstype'] == 'INDBETALING':
        indbetaling_sum += float(row['Beløb'].replace(".", "").replace(",", "."))
    elif row['Transaktionstype'] == 'HÆVNING':
        haevning_sum += float(row['Beløb'].replace(".", "").replace(",", "."))
totals = [indbetaling_sum * 1.2, haevning_sum]

rects  = ax2.bar(['INDBETALING', 'HÆVNING'], totals, color=['green', 'red'])

ax2.set_title('Ind- og ud-betalinger')
ax.set_title('Ind- og ud-betalinger')
for i, total in enumerate(totals):
    ax2.text(i, total+0.1*max(totals)/2, f'{total:,.0f} DKK', ha='center')


title_text = fig.suptitle('My Title', fontsize=20)


def init():
    line.set_data([], [])
    text.set_text('')
    return line, text, title_text


def update_data():
    insert_sum = 0
    withdraw_sum = 0
    sum = [0]
    def update(i):
        nonlocal insert_sum
        nonlocal withdraw_sum
        nonlocal sum
     #    line.set_data(range(i+1), sums[:i+1])
        # Clear the text objects in ax2
        for text_obj in ax2.texts:
            text_obj.remove()

        if data[i]['Transaktionstype'] in ['INDBETALING', 'HÆVNING']:
            sum.append(sum[-1] + float(data[i]['Beløb'].replace(".", "").replace(",", ".")))
        else:
            sum.append(sum[-1])

        line.set_data(range(i+1), sum[:i+1])

        text.set_text(f'Total sum: {sum[i]:,.0f} DKK')
        title_text.set_text(f'{date_text}: {data[i][posting_date_text]}')

        if data[i]['Transaktionstype'] == 'INDBETALING':
            insert_sum += float(data[i]['Beløb'].replace(".", "").replace(",", "."))
        elif data[i]['Transaktionstype'] == 'HÆVNING':
            withdraw_sum += float(data[i]['Beløb'].replace(".", "").replace(",", "."))

        totals = [insert_sum, withdraw_sum]

        for rect, total in zip(rects, totals):
            rect.set_height(total)

        for u, total in enumerate(totals):
             ax2.text(u, total + 0.1 * max(totals)/2, f'{total:,.0f} DKK', ha='center')

        return line, text, title_text

    return update

my_update_data = update_data()

ani1 = animation.FuncAnimation(fig, my_update_data, frames=len(data), interval=0.001, repeat=False)

# show the plots
plt.show()


