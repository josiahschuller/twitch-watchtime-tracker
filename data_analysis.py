import csv

csvFile = open('Data/brodie_total_sorted.csv', 'r', newline='')
totalData = list(csv.reader(csvFile,delimiter=','))
viewers = totalData[0]
watchtime = [float(i) for i in totalData[1]]
"""
def insertionSort(viewers, watchtime):
    for i in range(1, len(watchtime)):
        key = watchtime[i]
        keyViewer = viewers[i]

        j = i - 1
        while j >= 0 and key < watchtime[j]:
            watchtime[j + 1] = watchtime[j]
            viewers[j + 1] = viewers[j]
            j -= 1
        watchtime[j + 1] = key
        viewers[j + 1] = keyViewer
    return [viewers, watchtime]


totalDataSorted = insertionSort(viewers, watchtime)
with open('Data/brodie_total_sorted', 'w', newline='') as sortedFile:
    writer_file = csv.writer(sortedFile)
    sortedFile.truncate()
    writer_file.writerows(totalDataSorted)
"""
no = 1
for i in range(len(watchtime) - 1, len(watchtime) - 1001, -1):
    print(f"{no}. {viewers[i]}: {watchtime[i]} minutes")
    no += 1