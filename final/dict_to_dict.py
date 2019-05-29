import config

with open('dict.opcorpora.txt', 'r', encoding='utf-8') as f:
    count = 0
    nth = 100
    group = 40
    with open('dict_new.txt', 'w', encoding='utf-8') as new_dict:
        for line in f:
            if '\t' in line and (count // group % nth) == 0:
                word = line[0:line.find('\t')] # substring from 0 to the '\t' position
                if not any((d in word) for d in '0123456789'):
                    new_dict.write(config.FNREV(word) + '\n')
            count += 1
