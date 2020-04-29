import re
import random
import cmudict
import pronouncing

# this function finds the number of syllables in a word
# if it is in the CMU dictionary it returns that value else it uses my estimation algorithm
def get_syllables(word):
    count = 0
    pronunciation_list = pronouncing.phones_for_word(word)
    try:
        value = pronouncing.syllable_count(pronunciation_list[0])
    except IndexError:
        value = estimate_syllables(word)
        count += value

    return count

# This function estimatest the syllables in a word
def estimate_syllables(word):
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    count = 1
    prev_vowel = False

    # add a syllable for each vowel
    for i in range(len(word) - 1):
        # Two vowels in a row only counts as one syllable
        if word[i] in vowels and not prev_vowel:
            count += 1
            prev_vowel = True
        else:
            prev_vowel = False

    # y at the end of the word adds one syllable to the
    if word[-1] == 'y' and not prev_vowel:
        count += 1

    # e at the end of the word does is usually silent
    if word[-1] == 'e' and not prev_vowel:
        count -= 1

    return count


rhyming_dict = cmudict.dict()

# My function for determining if two words rhyme
def is_rhyme(a, b):
    vowels = ['a', 'e', 'i', 'o', 'u']
    test_a = rhyming_dict[a]
    test_b = rhyming_dict[b]
    last_a = 0
    last_b = 0

    # This is when either the first or second word are not in the CMU rhyming dictionary
    # In this case I say they rhyme if the last syllable in each word is the same
    if len(test_a) == 0 or len(test_b) == 0:
        for i in range(len(a) - 1, -1, -1):
            if a[i] in vowels:
                last_a = a[i]
                break

        for i in range(len(b) - 1, -1, -1):
            if b[i] in vowels:
                last_b = b[i]
                break

    # This is when either the first and second are in the CMU rhyming dictionary
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


# This file formats the source files into an array where each entry is one word
# The words are stripped of all punctuation and all in lowercase
def format_text(my_file):
    read_file = open(my_file, encoding="utf8").read()
    read_file = read_file.split()
    # regular expression that removes all non alphabet characters from a string
    regex = re.compile('[^a-zA-Z]')

    new_file = []
    for i in read_file:
        word = regex.sub('', i).lower()
        if word == '' or word == ' ':
            pass
        else:
            new_file.append(word)

    return new_file


file = format_text('kanye_lyrics.txt')

# This function creates the N-gram dictionary
def create_dict(n):
    keys = []
    my_dict = {}
    for i in range(len(file) - n):
        words = ' '.join(file[i:i+n])
        word_after = file[i + n]
        if words not in my_dict:
            my_dict[words] = {'total_count': 1, word_after: 1}
            keys.append(words)
        else:
            values = my_dict.get(words)
            new_total_count = values['total_count'] + 1
            values['total_count'] = new_total_count
            if word_after not in values.keys():
                values[word_after] = 1
            else:
                count = values.get(word_after)
                values[word_after] = count + 1
                my_dict[words] = values

    return my_dict, keys


my_dict, my_keys = create_dict(2)

# This function picks the next word in the sentence
# It picks the word according to its frequency in the dictionary.
def which_option(values_dict):
    keys = [i for i in values_dict.keys()]
    keys = keys[1:]
    values = [j for j in values_dict.values()]
    total_count = values[0]
    values = values[1:]

    population = []
    for j in range(len(values)):
        for k in range(values[j]):
            population.append(j)

    option = random.randint(0, total_count - 1)
    index = population[option]

    return keys[index]

# This function creates a sentence.
def create_sentence(start_words, len_sentence):
    curr = start_words
    sentence = start_words
    for i in range(len_sentence):
        new_word = which_option(my_dict[curr])
        sentence += ' ' + new_word
        curr = (curr.split())
        curr = ' '.join(curr[1:]) + ' ' + new_word

    return sentence

# This function picks a random entry in the N-gram dictionary and creates a sentence
# with that word as the first word
def create_random_sentence(len_sentence, keys):
    start_index = random.randint(0, len(keys) - 1)
    start_word = keys[start_index]

    len_sentence = random.randint(8,12)
    return create_sentence(start_word, len_sentence)

# This function takes all the lines created and makes a dictionary where each
# entry is a line and the values are an array of all other lines that rhyme with it.
def create_rhyming_dict(lines):
    rhyming_words = {}
    rhyming_keys = []

    for i in range(len(lines)):
        last_word = (lines[i].split())[-1]
        for j in range(len(lines)):
            if j == i:
                pass
            else:
                if last_word in pronouncing.rhymes(lines[j].split()[-1]):
                    if lines[i] not in rhyming_words:
                        rhyming_words[lines[i]] = [lines[j]]
                    else:
                        temp = rhyming_words[lines[i]]
                        temp.append(lines[j])
                        rhyming_words[lines[i]] = temp

    return rhyming_words

# This function uses the rhyming line dictionary and creates a verse according
# to the rhyme scheme that I found in my analysis.
def create_song(verse_length, rhyming_words):
    song = []
    keys = []
    structure = [2, 2, 1, 3]
    for line in rhyming_words.keys():
        if len(rhyming_words[line]) != 0:
            keys.append(line)
    prev_last_word = ""
    for i in range(4):
        curr_line = keys[random.randint(0, len(keys) - 1)]
        for j in range(structure[i]):
            song.append(curr_line)

            line_options = rhyming_words[curr_line]
            curr_line = line_options[random.randint(0, len(line_options) - 1)]

    return song


lines = []

# fill the lines array with 3000 sentences.
for i in range(3000):
    sentence = create_random_sentence(8, my_keys)
    syllables = get_syllables(sentence)
    if syllables > 6 and syllables < 14:
        lines.append(sentence)


verse_length = 8

# Call the function which creates the rhyming line dictionary.
my_rhyming_dict = create_rhyming_dict(lines)
my_songs = []


# Create 20 verses.
# A verse can't be created if a line is picked for a verse and that line
# does not have any other lines that rhyme with it.
# In this case I stop building that verse and move on to creating a new verse
for i in range(20):
    try:
        verse = create_song(verse_length, my_rhyming_dict)
        my_songs.append(verse)
    except:
        pass

# prints out all the verses from the my_songs array
for i in my_songs:
    for line in i:
        print(line)
    print('----------------------------------------------------------')