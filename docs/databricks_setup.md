# Configuração do Databricks Free

O projeto usa um perfil Databricks separado do projeto `data_ans`:
`brazil-auto-market-analytics`.

## Autenticação

Na raiz do projeto:

```powershell
databricks auth login --profile brazil-auto-market-analytics
databricks auth profiles
databricks workspace list / --profile brazil-auto-market-analytics
```

O perfil do projeto foi validado em 26/10/2026. O perfil antigo `data_ans`
permanece inválido e não é usado por este repositório. Tokens ficam na
configuração local do usuário, fora do Git.

## Notebook de teste

O notebook local `notebooks/00_databricks_test.py` foi importado para:

```text
/Shared/brazil-auto-market-analytics/00_databricks_test
```

Confirmação da importação:

```powershell
databricks workspace list /Shared/brazil-auto-market-analytics `
  --profile brazil-auto-market-analytics
```

retornando um objeto `NOTEBOOK` em Python.

## Execução validada

Foi submetido um run serverless com `environment_version=2` e concluído com
sucesso:

- run: `423100269764702`;
- task run: `644607977573622`;
- estado: `TERMINATED / SUCCESS`;
- resultado:
  `PYTHON_OK=4;PYSPARK_OK=rows:3;groups:COMBUSTAO=1,ELETRICO=1,HIBRIDO=1`.

O primeiro envio com `client=1` falhou antes de executar por incompatibilidade
do canal no workspace; a configuração corrigida usa `environment_version=2`.
