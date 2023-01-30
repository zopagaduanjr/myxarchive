import csv
import operator


def scrape_to_input(date):
    input = open('../raw_data/input.csv', 'a')
    writer = csv.writer(input)
    with open('../raw_data/scrape.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for idx, row in enumerate(csv_reader):
            if idx != 0:
                writer.writerow([date, idx, row[0], row[1].strip()])
    input.close()


def sort_csv(input_csv, output_csv):
    with open(input_csv, 'r') as infile, open(output_csv, 'w') as outfile:
        infile_reader = csv.reader(infile, delimiter=',')
        outfile_writer = csv.writer(outfile)
        headers = []
        for row in infile_reader:
            headers = row
            break
        outfile_writer.writerow(headers)
        sortedlist = sorted(infile_reader,
                            key=operator.itemgetter(0), reverse=False)
        outfile_writer.writerows(sortedlist)


# testing station
# sort_csv('../raw_data/spotified_input.csv',
#          '../raw_data/spotified_input_ordered_date.csv')
# scrape_to_input("2007-08-20")
