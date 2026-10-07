# Histórico e reaproveitamento

Resumo das experiências em alvos de laboratório para quem receber apenas este repositório. As evidências originais ficam fora deste pacote; os resultados abaixo não são certificação nem comprovação de adoção em uma empresa.

## O que já ocorreu

| Data | Rodada | Resultado registrado |
|---|---|---|
| 15/09/2026 | VAmPI REST local | 14 operações descobertas; baseline auditada com 11 pass e 2 partial |
| 15/09/2026 | Revisão da baseline | Login isolado e reimportação não comprovavam scan autenticado e correção |
| 15/09/2026 | Validação estendida | Autenticação/renovação, contrato, inventário, lifecycle, concorrência e integridade demonstrados localmente |
| 15/09/2026 | Juice Shop | Descoberta ampliada; análise anônima/timeboxed parcial |
| 15/09/2026 | crAPI | HTTP 500 no controle legítimo; teste cruzado inconclusivo/não concluído |
| 29–30/09/2026 | Organização | Visão de gestão e guia de estudo consolidados; sem nova execução |
| 07/10/2026 | Próxima entrega | Playground com dois serviços e evidências de desempenho/custo; em planejamento |

Não somar matrizes sobrepostas em percentual de conclusão. Sete categorias aplicáveis ao VAmPI foram classificadas como demonstradas por probes; três também detectadas por scanner. Isso não comprova cobertura geral. Rajada curta sem 429 não prova inexistência de limites; endpoint documentado não é shadow apenas por ser inseguro.

O laboratório demonstrou viabilidade com condições, não capacidade para milhares de serviços. Instalação de modelos com Claude foi relatada, mas não é dependência da execução deste pacote.

## Mapa das fontes locais

Identificadores dos conjuntos de laboratório de origem, sem caminhos privados. O código ainda não foi incorporado; seu acesso deve ser tratado com o mantenedor.

| Fonte | Reaproveitamento pretendido |
|---|---|
| dast-api-local/RESULTS.md e DECISION.md | Resultado e limites da baseline |
| dast-api-local/EXTENDED-LOCAL-VALIDATION.md | Autenticação, contrato, lifecycle e concorrência |
| dast-api-local/PROCESS-AND-REPRODUCTION.md | Procedimento existente, a auditar antes de portar |
| dast-api-local/scripts/ e config/ | Execução, limites, perfis e validações, após inspeção |
| dast-api-local/DAST-TECHNICAL-CAPABILITY-MAP.md | Catálogo dos mecanismos |
| dast-api-local/MARKET-EQUIVALENCE-TEST-PLAN.md | Critérios de avaliação ampliada |
| dast-target-catalog/RESULTS.md | Limitações Juice Shop/crAPI e comparabilidade |

Esses caminhos são referências de origem, não dependências obrigatórias para abrir os documentos deste repo. Quem precisar executar a versão anterior deve pedir acesso autorizado às fontes.

## Portabilidade sem copiar tudo

1. Inventariar somente dependências do runner e seu procedimento de reprodução.
2. Preservar versões/digests e registrar origem/hashes do código selecionado.
3. Remover dependência obrigatória do DefectDojo na primeira entrega, sem apagar sua prova histórica.
4. Excluir outputs, capturas, credenciais, dumps, código corporativo e downloads de terceiros.
5. Revisar licenças antes de redistribuir componentes; preferir imagens oficiais fixadas.
6. Validar em alvo sintético, sem acesso corporativo, antes de declarar o pacote executável.

A origem histórica permanece no vault; os planos deste pacote são mantidos aqui. Não duplicar um novo histórico de scans em Markdown: adicionar links às execuções autorizadas.
