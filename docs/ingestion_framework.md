# Framework de ingestão

O framework em `src/ingestion/framework.py` concentra a lógica comum de ingestão para evitar que cada fonte implemente seu próprio download, hash e registro de origem.

## Responsabilidades

- `SourceSpec`: descreve fonte, URL, período e destino;
- `IngestionFramework.ingest_local_file`: preserva um arquivo já baixado;
- `IngestionFramework.download`: realiza download HTTP para o destino;
- `sha256_file`: calcula o hash do arquivo;
- metadados: grava um arquivo `.metadata.json` ao lado do original;
- logging: registra início, sucesso e falha;
- erros: usa `IngestionError` e `SourceFileExistsError` sem esconder falhas.

## Exemplo

```python
from pathlib import Path

from src.ingestion import IngestionFramework, SourceSpec

spec = SourceSpec(
    source_name="FENABRAVE",
    source_url="https://exemplo.org/relatorio.pdf",
    reference_period="2026-01",
    source_file="fenabrave_2026_01.pdf",
    destination_dir=Path("data/raw/fenabrave"),
)

record = IngestionFramework().download(spec)
print(record.file_hash)
```

Os coletores específicos de FENABRAVE, ABVE e SENATRAN deverão apenas construir seus `SourceSpec` e aplicar regras próprias da fonte. A implementação de cada coletor ocorrerá nas tarefas T10, T11 e T25.

