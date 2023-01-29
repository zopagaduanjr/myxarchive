import csv


def scrape_to_input(date):
    input = open('../raw_data/input.csv', 'a')
    writer = csv.writer(input)
    with open('../raw_data/scrape.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for idx, row in enumerate(csv_reader):
            if idx != 0:
                writer.writerow([date, idx, row[0], row[1]])
    input.close()


scrape_to_input("2007-11-30")
