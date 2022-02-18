import time
import csv
import threading

from NightMarketChecker.nmChecker import nmChecker

threads = []


def colwrite():
    with open("output.csv", 'a+', newline="\n") as csvfile:
        write = csv.writer(csvfile)
        topcol = ['Account', 'Offer1', 'Offer2',
                  'Offer3', 'Offer4', 'Offer5', 'Offer6']
        write.writerow(topcol)


def ani(delay=0.099):
    text = "Fetching Data\n"
    for letter in text:
        print(letter, end='', flush=True)
        time.sleep(delay)
    print()


def threadRun():
    with open("accounts.txt", encoding='utf-8') as f:
        for i in f.readlines():
            acc = i.rstrip("\n").split(";")
            t = threading.Thread(target=nmChecker().loop, args=(acc,))
            threads.append(t)
            t.start()
    ani()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    colwrite()
    threadRun()
    print("\nComplete info saved in output.csv")
