# Ingestão FENABRAVE

O módulo `src/ingestion/fenabrave.py` consulta o índice oficial de emplacamentos, identifica os PDFs mensais disponíveis e usa o framework genérico da T09 para preservar um relatório em Bronze.

## Execução

```powershell
# Um período específico
python -m src.ingestion.fenabrave --period 2026-01

# Repetir para cada mês publicado no índice oficial
foreach ($period in '2026-01','2026-02','2026-03','2026-04','2026-05','2026-06','2026-07','2026-08','2026-09') {
  python -m src.ingestion.fenabrave --period $period
}
```

O arquivo e o metadata são gravados em:

```text
data/bronze/fenabrave/2026-01/2026_01_02.pdf
data/bronze/fenabrave/2026-01/2026_01_02.pdf.metadata.json
```

O coletor valida que o arquivo existe, possui volume maior que zero e começa com a assinatura de PDF (`%PDF-`). A extração de tabelas e rankings fica para a padronização da T13; nesta etapa o conteúdo original é preservado sem alteração.

## Execução validada

Em 26/10/2026, os períodos `2026-01` a `2026-09` foram baixados com sucesso.
Cada período possui seu PDF e metadata com hash SHA-256 em `data/bronze/`.
O índice consultado listava janeiro a setembro de 2026; outubro ainda não tinha
relatório mensal publicado na consulta.

O primeiro período foi registrado como:

- arquivo: `2026_01_02.pdf`;
- volume: `4.831.101` bytes;
- SHA-256: `0300494d57f731299645439742fda9484d5cc35637ec7902ae5cb59ce696dbe4`;
- metadata: `2026_01_02.pdf.metadata.json`.

O PDF e o metadata ficam em `data/bronze/`, que é ignorado pelo Git para evitar versionar arquivos grandes.

## Fonte

- Índice oficial: <https://www.fenabrave.org.br/portalv2/Conteudo/Emplacamentos>
- O coletor não inventa URLs: os links são descobertos no HTML oficial.
- A disponibilidade de períodos pode mudar; o comando falha informando os períodos encontrados quando o solicitado não está publicado.
