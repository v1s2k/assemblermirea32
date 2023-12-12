"""
0001 INC - увеличить значение регистра или памяти на 1
0010 DEC - уменьшить значение регистра или памяти на 1
0100 JZ - перейти к указанной метке, если значение регистра или памяти равно нулю
0101 JNZ - перейти к указанной метке, если значение регистра или памяти не равно нулю
0110 MVC - переместить значение из одного регистра в памяти другого
0111 MVS - сохранить значение регистра или памяти в стеке
1000 MVA - переместить значение из регистра или памяти в аккумулятор
1010 MVSRM - переместить значение из регистра стека в регистр или память
1001 ADDAR - прибавить значение регистра или памяти к аккумулятору (регистр  для временного хранения данных и выполнения арифметических операций)

0001 INC RX
0010 DEC RX
0100 JZ 1
0101 JNZ 1
0110 MVC 1
0111 MVS 1
1000 MVA 1
1010 MVSRM 1
1001 ADDAR 1
"""



REGS = [0, 0, 0]
memory = [1, 1, 1]

def reg_by_code(reg): # поиск положения регистра в памяти данных,
    # то есть номер от 1 до 3 (0-2 регистр) по типу команду(0000 итд)

    reg = str(reg)
    if reg == '0000' or reg == 'CX':
        return REGS[0], 0
    if reg == '0001' or reg == 'SI':
        return REGS[1], 1
    if reg == '0002' or reg == 'AC':
        return REGS[2], 2


def from_bin(raw_code): # парсинг 32 битовой строки, чтобы разбить по сегментам
    raw_code = str(raw_code) # переводим в строку для парса и делаем его
    cmd_type = bin(int(raw_code[:4], 2))[2:].zfill(4)
    literal = bin(int(raw_code[4:20], 2))[2:].zfill(16)
    op1 = bin(int(raw_code[20:24], 2))[2:].zfill(4)

    return cmd_type, literal, op1


def work_with_bin(filename):
    global REGS, memory
    with open(filename, 'r', encoding='UTF-8') as f:
        raw_data = f.readlines()

    commands = []
    for raw in raw_data:
        comment_start = raw.find('--')
        if comment_start != -1: # удаляем коммент (--)
            raw = raw[:comment_start]

        if raw.strip():
            if raw.startswith('#ARRAY'): # ищем метку объявления массива
                raw = raw.replace('#ARRAY', '').strip()
                memory = [int(x) for x in raw.split(',')]# присваем в память список целых чисел
                continue
            commands.append(from_bin(raw.strip())) # Если условия выше не выполнились,
            # то строка преобразуется из двоичного формата в формат команды и добавляется в список commands.

    cmd_it = 0

    while True:
        command = commands[cmd_it]

        if command[0] == '0001':
            reg = reg_by_code(command[2])
            REGS[reg[1]] += 1
        elif command[0] == '0010':
            reg = reg_by_code(command[2])
            REGS[reg[1]] -= 1
        elif command[0] == '0100':
            if reg_by_code('0000')[0] == 0:
                cmd_it = int(command[1], 2)
                continue
        elif command[0] == '0101':
            if reg_by_code('0000')[0] != 0:
                cmd_it = int(command[1], 2)
                continue
        elif command[0] == '0110':
            mem_ix = int(command[1], 2)
            REGS[0] = memory[mem_ix]
        elif command[0] == '0111':
            mem_ix = int(command[1], 2)
            REGS[1] = memory[mem_ix]
        elif command[0] == '1000':
            mem_ix = int(command[1], 2)
            REGS[2] = memory[mem_ix]
        elif command[0] == '1010':
            REGS[1] = memory[reg_by_code(command[2])[0]]
        elif command[0] == '1001':
            REGS[2] += reg_by_code(command[2])[0]

        print('REGS:')
        print(REGS)
        print('MEM:')
        print(memory)
        cmd_it += 1
        if cmd_it == len(commands): # достигаем макс длинны списка commands
            break


def work_from_text(filename):
    global REGS, memory

    with open(filename, 'r', encoding='UTF-8') as f:
        raw_data = f.readlines()

    results = []
    for raw in raw_data:
        if not raw.strip():# пропуск пустой строки в .txt
            continue
        op, *args = raw.split() #первый элемент( команда сохраняем в op),остальные (аргументы) в args
        code = ''.zfill(4) # парсим бинарники
        lit = ''.zfill(16)
        rg = ''.zfill(4)

        if op.startswith('#ARRAY'): # Если команда начинается с '#ARRAY',
            # то строка добавляется в список results и обработка строки прекращается.
            results.append(raw)
            continue

        args = [int(x.strip()) for x in args] #Аргументы преобразуются в целочисленные значения и сохраняются в список args

        if op.upper() == 'INC':
            code = '0001'
            rg = bin(args[0]).replace('0b', '').zfill(4)
        elif op.upper() == 'DEC':
            code = '0010'
            rg = bin(args[0]).replace('0b', '').zfill(4)
        elif op.upper() == 'JZ':
            code = '0100'
            lit = bin(args[0]).replace('0b', '').zfill(16)
        elif op.upper() == 'JNZ':
            code = '0101'
            lit = bin(args[0]).replace('0b', '').zfill(16)
        elif op.upper() == 'MVC':
            code = '0110'
            lit = bin(args[0]).replace('0b', '').zfill(16)
        elif op.upper() == 'MVS':
            code = '0111'
            lit = bin(args[0]).replace('0b', '').zfill(16)
        elif op.upper() == 'MVA':
            code = '1000'
            lit = bin(args[0]).replace('0b', '').zfill(16)
        elif op.upper() == 'MVSRM':
            code = '1010'
            rg = bin(args[0]).replace('0b', '').zfill(4)
        elif op.upper() == 'ADDAR':
            code = '1001'
            rg = bin(args[0]).replace('0b', '').zfill(4)

        results.append(f'{code}{lit}{rg}')

    open('result', 'w', encoding='UTF-8').write('\n'.join(results))
    work_with_bin('result')


if __name__ == '__main__':
    filename = 'test.tasm'
    print('Выберить тип тестововых данных? (bin/txt)')
    while True:
        choice = input('> ')
        if choice.lower() not in ('bin', 'txt'):
            continue
        break

    if choice == 'bin':
        work_from_text(filename)
    else:
        work_from_text(filename)
