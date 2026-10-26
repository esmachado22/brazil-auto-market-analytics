# Matriz de fontes

Atualizada em 26/10/2026.

| Fonte | Dado | Período observado | Formato | Automação | Limitações |
|---|---|---|---|---|---|
| FENABRAVE | Emplacamentos, segmentos, rankings e participação de mercado | Jan/2025 a Set/2026 na página consultada; outros anos por seletor | HTML + PDF mensal | Parcial: download oficial e extração documentada de PDF | PDF não é estruturado; rankings podem ser recortes; dados regionais/municipais detalhados exigem cadastro |
| ABVE Data | Eletrificados leves por tecnologia; market share e alguns recortes geográficos | Jan/2012 a Set/2026 na série/comunicados consultados | BI web + HTML | Parcial: leitura de dashboard/comunicados | Sem arquivo estruturado identificado; MHEV fica fora do total de eletrificados desde 2025 |
| SENATRAN/RENAVAM | Frota registrada por UF, município, tipo, combustível, marca/modelo, ano e outros atributos | Arquivos mensais; página de 2026 com Jan/2026 a Set/2026; histórico de anos anteriores disponível | XLSX mensal + ZIP/CSV/TXT no catálogo | Possível via página oficial/portal de dados, após o MVP | É estoque, não fluxo; arquivos separados e grandes; nomes e periodicidade podem mudar |
| FIPE | Preço médio de referência por veículo, versão/ano conforme consulta | Mês/ano selecionado na consulta | Consulta web modelo a modelo | Não adequada para o MVP: sem API e sem download da base completa | Valor é referência, não preço efetivo de venda; automação precisa de autorização e mecanismo reproduzível |

## Decisões

- MVP: FENABRAVE + ABVE.
- Fase posterior: SENATRAN.
- Preço: fora do MVP até existir fonte autorizada e automatizável.
- Nenhum dataset grande será versionado no Git.
