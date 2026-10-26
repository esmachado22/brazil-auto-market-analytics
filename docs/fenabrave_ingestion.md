# Ingestão FENABRAVE

O módulo `src/ingestion/fenabrave.py` consulta o índice oficial de emplacamentos, identifica os PDFs mensais disponíveis e usa o framework genérico da T09 para preservar um relatório em Bronze.

## Execução

```powershell
python -m src.ingestion.fenabrave --period 2026-01
```

O arquivo e o metadata são gravados em:

```text
data/bronze/fenabrave/2026-01/2026_01_02.pdf
data/bronze/fenabrave/2026-01/2026_01_02.pdf.metadata.json
```

O coletor valida que o arquivo existe, possui volume maior que zero e começa com a assinatura de PDF (`%PDF-`). A extração de tabelas e rankings fica para a padronização da T13; nesta etapa o conteúdo original é preservado sem alteração.

## Execução validada

Em 26/10/2026, o período `2026-01` foi baixado com sucesso:

- arquivo: `2026_01_02.pdf`;
- volume: `4.831.101` bytes;
- SHA-256: `0300494d57f731299645439742fda9484d5cc35637ec7902ae5cb59ce696dbe4`;
- metadata: `2026_01_02.pdf.metadata.json`.

O PDF e o metadata ficam em `data/bronze/`, que é ignorado pelo Git para evitar versionar arquivos grandes.

## Fonte

- Índice oficial: <https://www.fenabrave.org.br/Portal/conteudo/emplacamentos>
- O coletor não inventa URLs: os links são descobertos no HTML oficial.
- A disponibilidade de períodos pode mudar; o comando falha informando os períodos encontrados quando o solicitado não está publicado.
