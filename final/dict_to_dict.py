with open('dict_original.txt', 'r') as f:
    count = 0
    nth = 1000
    group = 20
    with open('dict_new.txt', 'w') as new_dict:
        for line in f:
            if '\t' in line and (count // group % nth) == 0:
                word = line[0:line.find('\t')] # substring from 0 to the '\t' position
                new_dict.write(word + '\n')
            count += 1
