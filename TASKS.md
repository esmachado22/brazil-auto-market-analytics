# TASKS.md — Brazil Auto Market Analytics

## Como usar este arquivo

As tarefas devem ser executadas em ordem.

O Codex deve:
- trabalhar uma tarefa por vez;
- verificar o estado atual do repositório antes de alterar;
- não implementar tarefas futuras sem necessidade;
- executar testes/validações relacionados à tarefa;
- atualizar documentação quando uma decisão técnica for tomada;
- marcar a tarefa como concluída somente após validação.

Status:
- `[ ]` Backlog
- `[~]` Em andamento
- `[x]` Concluída

---

# FASE 0 — Preparação

## T01 — Criar estrutura inicial do projeto
- [x] Criar estrutura de diretórios definida em `PROJECT.md`.
- [x] Criar `README.md`, `PROJECT.md` e `TASKS.md`.
- [x] Criar `.gitignore`.
- [x] Criar `data/README.md`.
- [x] Não adicionar datasets grandes ao Git.

**Aceite:** repositório organizado e pronto para desenvolvimento.

## T02 — Configurar ambiente Databricks Free
- [x] Documentar como conectar o projeto ao Databricks Free.
- [x] Confirmar disponibilidade de notebooks/SQL.
- [x] Criar notebook de teste.
- [x] Executar operação simples em Python e PySpark.

**Aceite:** notebook executa com sucesso no ambiente gratuito.

## T03 — Configurar Git e GitHub
- [x] Inicializar repositório.
- [x] Configurar branch principal.
- [x] Fazer primeiro commit.
- [x] Criar README inicial.

**Aceite:** projeto versionado e clonável.

---

# FASE 1 — Descoberta e validação das fontes

## T04 — Mapear fonte FENABRAVE
- [x] Identificar páginas/arquivos oficiais.
- [x] Identificar períodos disponíveis.
- [x] Identificar formatos.
- [x] Registrar URLs.
- [x] Registrar limitações.
- [x] Documentar em `docs/data_sources.md`.

**Aceite:** fonte FENABRAVE documentada e validada.

## T05 — Mapear fonte ABVE
- [x] Identificar dados de eletrificados.
- [x] Identificar categorias.
- [x] Identificar histórico disponível.
- [x] Registrar URLs.
- [x] Documentar limitações.

**Aceite:** fonte ABVE documentada.

## T06 — Mapear fonte SENATRAN
- [x] Identificar arquivos de frota.
- [x] Identificar campos disponíveis.
- [x] Identificar histórico.
- [x] Identificar tamanho dos arquivos.
- [x] Documentar formato e limitações.

**Aceite:** SENATRAN documentado sem assumir campos que não existam.

## T07 — Avaliar fonte de preço
- [x] Pesquisar fontes públicas permitidas.
- [x] Verificar possibilidade de automação.
- [x] Verificar termos de uso.
- [x] Definir se entra no MVP ou fase posterior.
- [x] Documentar decisão.

**Aceite:** decisão documentada sobre preço.

## T08 — Criar matriz de fontes
Criar uma tabela contendo:

- [x] Consolidar FENABRAVE, ABVE, SENATRAN e FIPE em `docs/source_matrix.md`.

| Fonte | Dado | Período | Formato | Automação | Limitações |
|---|---|---|---|---|---|

**Aceite:** matriz atualizada com evidências reais em `docs/source_matrix.md`.

---

# FASE 2 — Ingestão

## T09 — Criar framework de ingestão
- [x] Criar módulos reutilizáveis.
- [x] Criar logging.
- [x] Criar metadados.
- [x] Criar tratamento de erros.
- [x] Preparar estrutura para múltiplas fontes.

**Aceite:** framework permite adicionar novas fontes sem duplicar lógica.

## T10 — Implementar ingestão FENABRAVE
- [x] Baixar/ler fonte real.
- [x] Preservar conteúdo original.
- [x] Registrar metadados.
- [x] Gravar Bronze.
- [x] Validar volume.

**Aceite:** dados reais FENABRAVE disponíveis em Bronze.

## T11 — Implementar ingestão ABVE
- [x] Coletar dados reais.
- [x] Preservar categorias originais.
- [x] Registrar período e origem.
- [x] Gravar Bronze.

**Aceite:** dados reais ABVE disponíveis em Bronze.

## T12 — Criar controle de idempotência
- [x] Definir chave de ingestão.
- [x] Impedir duplicação.
- [x] Criar teste executando a mesma ingestão duas vezes.

**Aceite:** segunda execução não duplica registros.

---

# FASE 3 — Bronze → Silver

## T13 — Padronizar FENABRAVE
- [x] Padronizar nomes.
- [x] Converter tipos.
- [x] Normalizar períodos.
- [x] Tratar nulos.
- [x] Remover duplicidades justificadas.
- [x] Preservar rastreabilidade.

**Aceite:** tabela Silver validada.

## T14 — Padronizar ABVE
- [x] Padronizar períodos.
- [x] Preservar categorias.
- [x] Criar classificação tecnológica padronizada.
- [x] Documentar regras.

**Aceite:** tabela Silver validada.

## T15 — Criar classificação de tecnologia
Implementar:

```text
COMBUSTAO
HIBRIDO
ELETRICO
OUTRO
NAO_INFORMADO
```

- [x] Criar regra única e reutilizável.
- [x] Preservar categoria original.
- [x] Separar agregados de tecnologias.
- [x] Documentar regra e exceção MHEV da ABVE.

**Aceite:** regra reproduzível e documentada.

## T16 — Criar testes de qualidade
Testar:

- [x] campos obrigatórios;
- [x] quantidade negativa;
- [x] duplicidade;
- [x] período;
- [x] chaves;
- [x] nulos críticos.

**Aceite:** testes executáveis e com resultado registrado.

---

# FASE 4 — Modelo Gold

## T17 — Criar dimensão de tempo
- [x] Criar calendário.
- [x] Ano.
- [x] Mês.
- [x] trimestre.
- [x] período de referência.

**Aceite:** calendário cobre todo o histórico carregado.

## T18 — Criar dimensão de marca
- [x] Criar chave.
- [x] Padronizar nomes.
- [x] Manter nome original quando necessário.

**Aceite:** marcas sem duplicidade indevida.

## T19 — Criar dimensão de modelo
- [x] Criar chave.
- [x] Relacionar marca/modelo.
- [x] Preservar nomenclatura original.

**Aceite:** relacionamento marca → modelo validado.

## T20 — Criar fato de emplacamentos
Campos mínimos esperados:

- [x] período;
- [x] marca;
- [x] modelo;
- [x] categoria;
- [x] quantidade;
- [x] tecnologia, quando possível.

**Aceite:** consultas de ranking funcionam.

## T21 — Criar fato de eletrificados
- [ ] Integrar dados ABVE.
- [ ] Preservar classificação original.
- [ ] Criar métricas mensais.

**Aceite:** comparação entre tecnologias funciona.

## T22 — Criar modelo analítico final
- [ ] Validar dimensões.
- [ ] Validar fatos.
- [ ] Validar chaves.
- [ ] Validar totais contra as fontes.

**Aceite:** Gold pronta para análise.

---

# FASE 5 — Analytics

## T23 — Criar consultas principais
Criar SQL para:

- top 10 modelos;
- top 10 marcas;
- volume mensal;
- market share;
- crescimento mensal;
- combustão x híbrido x elétrico;
- BEV/PHEV/HEV/MHEV;
- evolução dos eletrificados.

**Aceite:** consultas reproduzíveis.

## T24 — Validar métricas
Comparar resultados Gold com os números publicados pelas fontes.

**Aceite:** divergências documentadas e justificadas.

---

# FASE 6 — SENATRAN

## T25 — Implementar ingestão SENATRAN
Somente após o MVP principal funcionar.

- [ ] Coletar dados reais.
- [ ] Avaliar tamanho.
- [ ] Gravar Bronze.
- [ ] Documentar origem.

## T26 — Criar Silver SENATRAN
- [ ] Combustível.
- [ ] Marca/modelo.
- [ ] UF.
- [ ] Município.
- [ ] Ano.
- [ ] Potência, quando disponível.

## T27 — Criar fato de frota
Manter clara a diferença entre:

```text
FENABRAVE/ABVE = fluxo
SENATRAN = estoque
```

**Aceite:** análises de frota não são confundidas com vendas.

---

# FASE 7 — Preço

## T28 — Integrar preço de referência
Executar somente se a fonte estiver validada.

- [ ] Implementar ingestão.
- [ ] Registrar fonte.
- [ ] Criar Silver.
- [ ] Criar fato de preços.
- [ ] Documentar limitações.

**Aceite:** preço identificado como referência, não preço efetivo de venda.

## T29 — Criar análise volume x preço
- [ ] Preço médio por tecnologia.
- [ ] Preço por marca.
- [ ] Preço por modelo.
- [ ] Volume x preço.

---

# FASE 8 — Power BI

## T30 — Definir modelo para BI
- [ ] Definir tabelas.
- [ ] Definir medidas.
- [ ] Documentar relacionamentos.

## T31 — Criar dashboard executivo
Páginas:

1. Mercado geral
2. Combustão x eletrificados
3. Eletrificados
4. Marcas e modelos
5. Geografia

**Aceite:** dashboard utiliza somente dados Gold validados.

---

# FASE 9 — IA

## T32 — Definir camada de análise com IA
- [ ] Definir entradas.
- [ ] Definir métricas permitidas.
- [ ] Definir formato de saída.
- [ ] Impedir invenção de dados.

## T33 — Criar análise executiva automática
Exemplos:

- resumo mensal;
- maiores crescimentos;
- principais quedas;
- evolução dos eletrificados;
- mudanças de market share.

## T34 — Structured Output
Criar saída estruturada semelhante a:

```json
{
  "periodo": "2026-08",
  "resumo": "...",
  "principais_movimentos": [],
  "dados_observados": [],
  "alertas": []
}
```

**Aceite:** IA produz saída validável e baseada somente nos dados fornecidos.

---

# FASE 10 — Documentação e publicação

## T35 — Documentar arquitetura
Atualizar:

`docs/architecture.md`

## T36 — Criar dicionário de dados
Atualizar:

`docs/data_dictionary.md`

## T37 — Documentar metodologia
Explicar:

- fontes;
- definições;
- market share;
- tecnologia;
- fluxo x estoque;
- preço de referência;
- limitações.

## T38 — Documentar qualidade
Atualizar:

`docs/data_quality.md`

## T39 — Criar README final
README deve explicar:

- problema;
- arquitetura;
- fontes;
- tecnologias;
- pipeline;
- resultados;
- dashboard;
- IA;
- como reproduzir;
- limitações.

## T40 — Preparar release
- [ ] Revisar código.
- [ ] Remover credenciais.
- [ ] Remover arquivos grandes.
- [ ] Executar testes.
- [ ] Validar documentação.
- [ ] Criar release GitHub.
- [ ] Criar exemplo de execução.

---

# Definition of Done

O projeto só deve ser considerado concluído quando:

- [ ] Fontes documentadas.
- [ ] FENABRAVE funcionando.
- [ ] ABVE funcionando.
- [ ] Bronze funcionando.
- [ ] Silver funcionando.
- [ ] Gold funcionando.
- [ ] Qualidade implementada.
- [ ] Idempotência implementada.
- [ ] Market share validado.
- [ ] Combustão x híbridos x elétricos funcionando.
- [ ] SENATRAN integrado ou decisão documentada.
- [ ] Preço integrado ou decisão documentada.
- [ ] Power BI publicado.
- [ ] IA funcionando, se incluída.
- [ ] README completo.
- [ ] Projeto reproduzível.
- [ ] Nenhuma credencial exposta.
- [ ] Release pública pronta.

# Regra final

Não aumentar o escopo antes de o MVP funcionar.

A ordem prioritária é:

```text
Fontes
  ↓
FENABRAVE + ABVE
  ↓
Bronze
  ↓
Silver
  ↓
Gold
  ↓
Qualidade
  ↓
Analytics
  ↓
SENATRAN
  ↓
Preço
  ↓
Power BI
  ↓
IA
```
