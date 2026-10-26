# Ingestão ABVE

O módulo `src/ingestion/abve.py` preserva em Bronze o comunicado HTML oficial da ABVE Data associado a um período de referência. O HTML mantém o conteúdo original e as categorias publicadas pela fonte; a transformação para a camada Silver será feita posteriormente.

## Execução

```powershell
python -m src.ingestion.abve --period 2026-08 --url https://abve.org.br/com-57-mil-emplacamentos-em-agosto-eletrificados-abrem-a-corrida-para-o-milhao-em-setembro/
```

O arquivo e o metadata são gravados em:

```text
data/bronze/abve/2026-08/abve_2026_08.html
data/bronze/abve/2026-08/abve_2026_08.html.metadata.json
```

O coletor valida que o HTML possui volume maior que zero e mantém as categorias originais `BEV`, `PHEV`, `HEV`, `HEV Flex` e `MHEV`. Ele não soma nem reclassifica categorias nesta etapa.

## Execução validada

Em 26/10/2026, o período `2026-08` foi baixado com sucesso:

- arquivo: `abve_2026_08.html`;
- volume: `147.684` bytes;
- SHA-256: `1398840c25476547236c09911132f35769db906a4f284a8e3484cbd8126ba085`;
- metadata: `abve_2026_08.html.metadata.json`.

O HTML e o metadata ficam em `data/bronze/`, que é ignorado pelo Git para evitar versionar arquivos de dados.

## Fontes oficiais

- ABVE Data: <https://abve.org.br/abve-data/eletrificadosmhev/>
- Comunicado usado na validação: <https://abve.org.br/com-57-mil-emplacamentos-em-agosto-eletrificados-abrem-a-corrida-para-o-milhao-em-setembro/>

O comunicado informa que o total de eletrificados da ABVE é composto por `BEV + PHEV + HEV + HEV Flex`, sem incluir `MHEV`. Essa regra será implementada na padronização da T14, não durante a preservação Bronze.
