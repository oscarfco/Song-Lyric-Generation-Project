import re
import pronouncing
import cmudict
import numpy as np
import matplotlib.pyplot as plt
from statistics import mode


rhyming_dict = cmudict.dict()


def is_rhyme(a, b):
    vowels = ['a', 'e', 'i', 'o', 'u']
    test_a = rhyming_dict[a]
    test_b = rhyming_dict[b]
    last_a = 0
    last_b = 0

    if len(test_a) == 0 or len(test_b) == 0:
        for i in range(len(a) - 1, -1, -1):
            if a[i] in vowels:
                last_a = a[i]
                break

        for i in range(len(b) - 1, -1, -1):
            if b[i] in vowels:
                last_b = b[i]
                break

    else:
        a_pronunciation = test_a[0]
        b_pronunciation = test_b[0]
        for i in range(len(a_pronunciation) - 1, -1, -1):
            if a_pronunciation[i][0].lower() in vowels:
                last_a = a_pronunciation[i]
                break

        for i in range(len(b_pronunciation) - 1, -1, -1):
            if b_pronunciation[i][0].lower() in vowels:
                last_b = b_pronunciation[i]
                break

    if last_a == last_b:
        return True
    else:
        return False


def format_text(my_file):
    read_file = open(my_file, encoding="utf8").read()
    read_file = read_file.split()
    regex = re.compile('[^a-zA-Z]')

    new_file = []
    for i in read_file:
        word = regex.sub('', i).lower()
        if word == '' or word == ' ':
            pass
        else:
            new_file.append(word)

    return new_file


def read_lines(f):
    file = open(f, encoding="utf8")
    lines = []
    for line in file:
        stripped = line.rstrip()
        word = re.sub('[!?,"-]', ' ', stripped).lower()
        lines.append(re.sub(' +', ' ', word))

    return lines


file_by_lines = read_lines('kanye_lyrics.txt')


def determine_verse_scheme(verse):
    scheme = []
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't']
    curr_index = 0
    my_dict = {}

    for line in verse:
        need_new_letter = True
        last_word = line.split()[-1]
        if len(scheme) == 0:
            scheme.append(alphabet[curr_index])
            my_dict[alphabet[curr_index]] = last_word
            curr_index += 1
        else:
            for i in range(curr_index):
                if is_rhyme(last_word, my_dict[alphabet[i]]):
                    scheme.append(alphabet[i])
                    need_new_letter = False
            if need_new_letter:
                scheme.append(alphabet[curr_index])
                my_dict[alphabet[curr_index]] = last_word
                curr_index += 1
    return scheme


def get_verses(f):
    verses = []
    curr_verse = []
    for line in f:
        if line != '':
            curr_verse.append(line)
        else:
            verses.append(curr_verse)
            curr_verse = []
    return verses


verses = get_verses(file_by_lines)
schemes = []
for i in range(len(verses)):
    schemes.append(determine_verse_scheme(verses[i]))


avg_scheme = [[],[],[],[],[],[],[],[]]


for j in range(8):
    for i in schemes:
        if len(i) >= 8:
            avg_scheme[j].append(i[j])


for i in range(len(avg_scheme)):
    avg_scheme[i] = mode(avg_scheme[i])

print("Kanye West's Average rhyme scheme is: ", avg_scheme)

def get_syllables(text):
    lines = text.split()

    regex = re.compile('[^a-zA-Z]')

    count = 0
    for i in lines:
        word = regex.sub('', i).lower()
        if word == '' or word == ' ' :
            pass
        else:
            if word[-1] == "'":
                word = word[:-1]
            pronunciation_list = pronouncing.phones_for_word(word)
            try:
                value = pronouncing.syllable_count(pronunciation_list[0])
            except IndexError:
                value = estimate_syllables(word)
            count += value

    return count


def estimate_syllables(word):
    vowels = ['a', 'e', 'i', 'o', 'u']
    count = 0
    prev_vowel = False

    for i in range(len(word) - 1):
        if word[i] in vowels and not prev_vowel:
            count += 1
            prev_vowel = True
        else:
            prev_vowel = False

    if word[-1] == 'y' and not prev_vowel:
        count += 1

    if count == 0:
        count = 1

    return count


def algorithm_accuracy():
    word_file = open('common_words.txt', encoding="utf8").read()
    word_file = word_file.split()

    estimate_sum = 0
    actual_sum = 0

    for i in word_file:
        estimate = estimate_syllables(i)
        pronunciation_list = pronouncing.phones_for_word(i)
        actual = pronouncing.syllable_count(pronunciation_list[0])
        estimate_sum += estimate
        actual_sum += actual

    return (actual_sum - estimate_sum)/actual_sum


accuracy = algorithm_accuracy()

print("My syllable estimation algorithm has a realtive error of: ",accuracy)


def get_word_count(line):
    line = line.split()
    return len(line)


def get_syllable_stats(f):
    syllables = []
    word_count = []
    for line in f:
        if line != '':
            syllables.append(get_syllables(line))
            word_count.append(get_word_count(line))

    print("Kanye West's mean number of words per line:", np.mean(word_count), "and the standard deviation of the distribution is:", np.sqrt(np.var(word_count)))
    plt.hist(word_count, bins=35, label='word count')
    return syllables


stats = get_syllable_stats(file_by_lines)

plt.hist(stats, bins = 50, label='syllabe count')

print("Kanye West's mean and modal number of words per line:", np.mean(stats), mode(stats), "and the standard deviation of the distribution is:", np.sqrt(np.var(stats)))

plt.show()