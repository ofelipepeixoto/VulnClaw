# Radar / Carlos Felipe — fork de estudo

Este é um fork público de [Netw0rkNoob/VulnClaw](https://github.com/Netw0rkNoob/VulnClaw).
O código original e seu copyright continuam com seus autores. A licença MIT
upstream foi preservada. Este fork não representa autoria exclusiva de Carlos
Felipe nem uma versão homologada para produção.

## Escopo das correções

A [PR #1](https://github.com/ofelipepeixoto/VulnClaw/pull/1) parte do main auditado
`0b34878f84b089b21fcf85ecd445315f14df0672` e contém:

- Tokens web inválidos falham de forma segura, sem criação de credencial durante
  a verificação. O armazenamento segue `VULNCLAW_CONFIG_DIR`; tokens antigos em
  outro diretório não são migrados automaticamente.
- Fetch verifica TLS por padrão e não repete falhas de certificado com
  verificação desligada. A opção explícita `verify_tls=false` continua sendo
  uma escolha de laboratório.
- Regressões com ASGI e MockTransport, sem alvos externos.

A PR registra validação local do código no commit
`30f9b051253625f73f84e11d66086780e967887c`: **1.943 testes passaram, 7 foram
ignorados**, incluindo 26 regressões novas; Ruff, builds e limites de execução
também passaram. Esse é um registro de execução local anterior, não o resultado
de CI deste commit documental.

Em 17/10/2026, a API de Actions informou permissões habilitadas, mas listou zero
workflows e zero execuções para o commit da PR. Consultar/habilitar `ci.yml`
retornou 404. Portanto, CI do fork permanece sem confirmação. Não substituir
esse requisito pelo CI upstream de outro commit. Se a interface Actions exibir
um aviso de habilitação do fork, o mantenedor deve revisá-lo antes de habilitar.
O workflow herdado inclui upload Codecov/OIDC; revisar essa integração antes
de usá-la neste fork.

## Aproveitamento no Radar

O [estudo no Radar Integration Hub, PR #13](https://github.com/ofelipepeixoto/radar-integration-hub/pull/13)
é uma implementação autoral offline sobre a governança já existente, sem copiar
o engine. Compara propostas com e sem digest/origem de evidência e verifica
alteração de conteúdo, versão, aprovação humana fictícia e replay.

## Pendências

Redirecionamentos fora do escopo, confiança em loopback/Host, dados sensíveis nos
relatórios, criação atômica de token, isolamento do processo e os avisos de
dependências continuam pendentes. Não foram homologados Docker, modelos reais,
identidade real, clientes, VPS compartilhada ou produção. Esses pontos impedem
tratar as duas correções como hardening completo.

Direção e alterações preparadas para Carlos Felipe / Radar, com assistência de
IA. A autoria do upstream continua identificada pelo histórico e pela licença.
