# Ingestão SENATRAN / RENAVAM

## Origem oficial

O MVP usa o conjunto público [Registro Nacional de Veículos Automotores (RENAVAM)](https://dados.transportes.gov.br/dataset/registro-nacional-de-veiculos-automotores-renavam), mantido pelo Ministério dos Transportes/SENATRAN. A consulta ao catálogo CKAN seleciona o arquivo mensal de **UF, município, marca e modelo**, que é o recorte necessário para a próxima camada Silver.

O recurso usado no MVP é setembro de 2026:

`https://dados.transportes.gov.br/dataset/12686da0-3d71-4499-b432-d270f785c907/resource/4408da67-7821-4abf-96db-58acdf1497da/download/i_frota_por_uf_municipio_marca_e_modelo_ano_setembro_2026.zip`

## Tamanho e Bronze

- Tamanho publicado pelo catálogo: **136.926.215 bytes** (aprox. 130,4 MiB).
- O ZIP contém um TXT de **1.219.605.816 bytes** (aprox. 1,14 GiB) descompactado; essa expansão foi registrada para orientar o processamento Silver em streaming/chunks.
- Os arquivos auxiliares oficiais de combustível e potência são armazenados em `data/bronze/senatran/2026-09/auxiliary/`, com 1.327.325 e 24.253.009 bytes, respectivamente.
- Destino: `data/bronze/senatran/2026-09/`.
- O arquivo permanece ignorado pelo Git por ser um artefato grande.
- O arquivo `.metadata.json` ao lado registra URL, período, tamanho, SHA-256 e timestamp de ingestão.

## Execução reproduzível

```powershell
$py = 'C:\Users\Desktop\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m src.ingestion.senatran --period 2026-09 --destination-root data/bronze/senatran
```

O coletor é idempotente: se o arquivo e a proveniência já existirem, a execução reutiliza o Bronze existente; se a proveniência ou o hash divergirem, a execução falha para evitar sobrescrita silenciosa.
