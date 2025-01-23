Site officiel de mkdocs : https://www.mkdocs.org/

Site officiel de mkdocs-material : https://squidfunk.github.io/mkdocs-material/

Site web : https://manastria.github.io/proclab-unix-docs/


```
pipenv run mkdocs serve
```

pipenv run mkdocs build

pipenv run mkdocs gh-deploy --force


pipenv run python -m http.server


```powershell
$Env:ENABLE_MINIFY = "false"; pipenv run mkdocs serve; Remove-Item Env:ENABLE_MINIFY
```

