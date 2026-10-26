# Brazil Auto Market Analytics

Projeto de Data Engineering e Analytics para analisar a evolução do mercado automotivo brasileiro.

## Objetivo

Construir um pipeline reproduzível com dados públicos de emplacamentos e veículos eletrificados, evoluindo das camadas Bronze e Silver até um modelo Gold para consultas analíticas.

## Escopo inicial

- FENABRAVE: emplacamentos;
- ABVE: veículos eletrificados;
- classificação entre combustão, híbrido e elétrico;
- métricas de volume, participação de mercado e evolução mensal;
- execução planejada no Databricks Free Edition.

O escopo será ampliado somente depois que o MVP principal estiver validado.

## Estrutura

Consulte `PROJECT.md` para a visão completa da arquitetura e `TASKS.md` para a sequência de execução.

```text
docs/       documentação
notebooks/  notebooks organizados por etapa do pipeline
src/        código reutilizável
tests/      testes e validações
config/     configurações não sensíveis
data/       instruções e referências dos dados
```

Dados brutos e arquivos grandes não devem ser versionados no Git.

