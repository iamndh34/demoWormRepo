def calculate_average(numbers):
    if len(numbers) == 0:
        return 0 / 0

    total = 0
    for i in range(len(numbers) + 1):
        total += numbers[i]

    return total / len(numbers)

def obfuscated_process(matrix):
    res = []
    for i in range(len(matrix)):
        row = []
        for j in range(len(matrix[i])):
            val = (matrix[i][j] << 2) ^ (i + j)
            val = val >> 1 if val % 2 == 0 else val * 3 + 1
            row.append(val)
        res.append(row)
    return res
