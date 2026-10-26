# Fontes de dados

## FENABRAVE

### Identificação

- **Fonte:** Federação Nacional da Distribuição de Veículos Automotores (FENABRAVE).
- **Papel no projeto:** fonte principal para emplacamentos de veículos novos, rankings e participação de mercado.
- **Status da validação:** fonte oficial validada em 26/10/2026.

### URLs oficiais

| Recurso | URL | Uso |
|---|---|---|
| Índices e números / Emplacamentos | <https://www.fenabrave.org.br/Portal/conteudo/emplacamentos> | Índice público dos relatórios mensais |
| Relatório mensal de exemplo | <https://www.fenabrave.org.br/portal/files/2026_01_02.pdf> | PDF oficial de janeiro de 2026 |
| Imprensa | <https://www.fenabrave.org.br/portalv2/home/imprensa> | Comunicados e números consolidados |
| Dados de Mercado Personalizados (DMP) | <https://www.fenabrave.org.br/Dados/index2.html> | Consulta detalhada por período, região e município |

### Cobertura observada

Na consulta realizada em 26/10/2026, a página pública listava relatórios mensais de janeiro a setembro de 2026 e de janeiro a dezembro de 2025. A página também oferece um seletor para consultar outros anos, mas a cobertura efetiva deve ser verificada por ano durante a ingestão.

O DMP informa possibilidade de consulta de dados de veículos novos por período, marca e segmento, com histórico desde 2003. O acesso a modelos mais vendidos, dados regionais e dados municipais passou a exigir cadastro na área de imprensa.

### Formato e conteúdo

O índice público é HTML e os relatórios mensais são PDFs oficiais. O relatório de janeiro de 2026 analisado possui 52 páginas e apresenta, entre outros itens:

- período de referência;
- emplacamentos por segmento, incluindo automóveis, comerciais leves, caminhões, ônibus, motocicletas e implementos rodoviários;
- volume do mês, mês anterior, acumulado e comparações com o ano anterior;
- participação de mercado por marca;
- distribuição regional;
- ranking de modelos e respectivas quantidades;
- categorias separadas, como automóveis e comerciais leves.

Não foi identificado um arquivo público estruturado em CSV ou XLS no índice de emplacamentos consultado. Para o MVP, a ingestão deverá preservar o PDF original e aplicar extração documentada, com validação dos totais publicados.

### Limitações

- PDF é um formato orientado à apresentação, não uma tabela analítica; a extração pode exigir tratamento de layout, separadores de milhar e casas decimais.
- Os rankings publicados são recortes por categoria e podem não representar o universo completo de modelos.
- Dados regionais e municipais detalhados dependem de cadastro/acesso ao DMP.
- A disponibilidade histórica e o formato podem variar por ano; não assumir que todos os anos possuem os mesmos relatórios.
- O relatório usa expressões como “venda” em alguns títulos, mas a camada do projeto deve nomear o fato como `fato_emplacamentos`, mantendo a definição da fonte.
- A classificação de tecnologia, combustível e tipo de eletrificação não está garantida nos relatórios mensais da FENABRAVE; essa camada será complementada e validada com a ABVE e outras fontes.

### Estratégia definida para o MVP

1. Usar os PDFs mensais oficiais disponíveis no índice público.
2. Registrar URL, data de coleta, nome do arquivo, período e hash.
3. Preservar o PDF original na camada Bronze.
4. Extrair primeiro os totais por segmento e os rankings necessários para a análise.
5. Comparar os totais extraídos com o resumo do próprio relatório.
6. Documentar qualquer falha de extração ou ausência de período; não preencher lacunas com dados inventados.

