import os
from pathspec import PathSpec

def load_gitignore(root_dir):
    """Charge les règles de .gitignore sous forme de PathSpec."""
    gitignore_path = os.path.join(root_dir, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            spec = PathSpec.from_lines('gitwildmatch', f)
            return spec
    return None

def generate_tree(dir_path, prefix='', spec=None, skip_dirs=None):
    """Génère une arborescence ASCII pour un répertoire donné."""
    entries = sorted(os.listdir(dir_path))
    entries = [e for e in entries if not spec or not spec.match_file(os.path.relpath(os.path.join(dir_path, e)))]

    for index, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        connector = '└── ' if index == len(entries) - 1 else '├── '

        # Si on rencontre le répertoire .git, on l'affiche mais on ignore son contenu
        if os.path.isdir(path) and entry == ".git":
            print(f"{prefix}{connector}{entry} (dépôt Git)")
            continue

        print(f"{prefix}{connector}{entry}")

        if os.path.isdir(path) and (not skip_dirs or entry not in skip_dirs):
            extension = '    ' if index == len(entries) - 1 else '│   '
            generate_tree(path, prefix + extension, spec, skip_dirs)

if __name__ == "__main__":
    root_directory = os.getcwd()  # Répertoire courant
    spec = load_gitignore(root_directory)  # Charger le .gitignore
    skip_dirs = {".git"}  # Répertoires à ignorer
    print(root_directory)
    generate_tree(root_directory, spec=spec, skip_dirs=skip_dirs)
