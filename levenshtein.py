import os


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def damerau_levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return damerau_levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            transpositions = (
                previous_row[j] if c1 == s2[j - 1] and c2 == s1[i - 1] else float("inf")
            )
            current_row.append(
                min(insertions, deletions, substitutions, transpositions)
            )
        previous_row = current_row

    return previous_row[-1]


def compare_files(folder_path):
    file_list = os.listdir(folder_path)
    similar_files = []

    for i in range(len(file_list)):
        for j in range(i + 1, len(file_list)):
            file1 = os.path.join(folder_path, file_list[i])
            file2 = os.path.join(folder_path, file_list[j])

            with open(file1, "r", encoding="utf-8") as f1, open(
                file2, "r", encoding="utf-8"
            ) as f2:
                content1 = f1.read()
                content2 = f2.read()

            levenshtein_dist = levenshtein_distance(content1, content2)
            damerau_levenshtein_dist = damerau_levenshtein_distance(content1, content2)

            print(f"Comparing {file_list[i]} and {file_list[j]}:")
            print(f"Levenshtein distance: {levenshtein_dist}")
            print(f"Damerau-Levenshtein distance: {damerau_levenshtein_dist}")
            print()

            # Define a threshold para considerar os arquivos como similares
            if levenshtein_dist <= 10 or damerau_levenshtein_dist <= 10:
                similar_files.append((file_list[i], file_list[j]))

    return similar_files


if __name__ == "__main__":
    folder_path = input("Digite o caminho da pasta: ")
    similar_files = compare_files(folder_path)
    print("\nArquivos similares:")
    for pair in similar_files:
        print(pair)
