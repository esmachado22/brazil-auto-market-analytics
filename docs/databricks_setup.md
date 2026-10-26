# Configuração do Databricks Free

O projeto usa um perfil Databricks separado do projeto `data_ans`.

## Pré-requisitos

- Databricks CLI instalado;
- acesso a um workspace Databricks Free;
- navegador disponível para autenticação OAuth.

## Autenticação

No terminal, a partir da raiz do projeto:

```powershell
databricks auth login --profile brazil-auto-market-analytics
```

O navegador será aberto para autenticação e seleção do workspace. Validar o perfil com:

```powershell
databricks auth profiles
databricks workspace list / --profile brazil-auto-market-analytics
```

O token fica na configuração local do usuário, fora do repositório. Credenciais nunca devem ser adicionadas ao Git.

## Notebook de teste

O notebook local `notebooks/00_databricks_test.py` foi importado para o workspace e executado com Serverless. O teste valida:

- operação Python simples;
- criação de DataFrame PySpark;
- agrupamento e contagem por tecnologia.

Resultado validado:

```text
PYTHON_OK=4
PYSPARK_OK=rows:3;groups:COMBUSTAO=1,ELETRICO=1,HIBRIDO=1
```

Também foi validado o SQL Warehouse Serverless Starter Warehouse com:

```sql
SELECT 1 AS test_value, current_date() AS test_date;
```

Resultado: `test_value = 1` e `test_date = 2026-10-26`.

