import os

def map_file_structure(root_directory, output_file):
    tree = []
    
    for root, dirs, files in os.walk(root_directory):
        level = root.replace(root_directory, '').count(os.sep)
        indent = '│   ' * level
        tree.append('{}{}/'.format(indent, os.path.basename(root)))

        subindent = '│   ' * (level + 1)
        for f in files:
            tree.append('{}├── {}'.format(subindent, f))

        # If there are directories, change the last file's prefix to '└──'
        if dirs:
            tree[-1] = tree[-1].replace('├──', '└──')
    
    # Change the last directory's prefix to '└──'
    if tree:
        tree[-1] = tree[-1].replace('├──', '└──')

    with open(output_file, 'w', encoding='utf-8') as file:  # Specify encoding as utf-8
        for line in tree:
            file.write(line + '\n')

if __name__ == "__main__":
    directory_to_map = input("Enter the directory path to map: ")
    output_filename = input("Enter the output file name: ")
    map_file_structure(directory_to_map, output_filename)
    print(f"File structure mapped to {output_filename}")

