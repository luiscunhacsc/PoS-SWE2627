# Segurança e privacidade

## Ativos e fronteiras

Ativos: integridade de stock/vendas/caixa, passwords, sessões, histórico de operação e disponibilidade do PoS. Superfícies: API HTTP, JavaScript no navegador, ficheiro SQLite e backups, dependências de instalação, consola de logs. A fronteira principal separa navegador não confiável de servidor. Outra separa aplicação de acesso direto ao disco: quem pode alterar o SQLite pode contornar os controlos da aplicação.

## Implementado

- Passwords do seed com `werkzeug.security.generate_password_hash` (scrypt por omissão na versão fixada); nenhuma password de produção no código. Password seed explicitamente pública.
- Tokens aleatórios de 256 bits, hash SHA-256 na base, cookie HttpOnly/SameSite Strict, 8h de expiração, logout e rotação no novo login.
- CSRF por sessão, validação do header Origin, escritas apenas JSON, ausência de CORS e hosts permitidos.
- Autorização no backend por papel, loja e dono do turno; a interface apenas reflete permissões.
- Queries parametrizadas, constraints SQL, transações, limite 64 KiB, validação de tipo exato (booleans não contam como inteiros).
- CSP sem inline scripts/estilos, sem CDN; escape de texto ao criar HTML; headers nosniff, DENY e referrer same-origin.
- Cinco tentativas de login por IP/utilizador em cinco minutos; mensagem de credencial inválida uniforme e comparação de hash mesmo para utilizador inexistente.
- Erros inesperados não expõem stack traces ao cliente; logs não incluem body, passwords, tokens ou valores de cookies.
- Auditoria de login/logout, abertura/fecho, vendas, anulações e ajustes; não há endpoint para editar/apagar auditoria.

As recomendações sobre CSRF, headers, cookies e recursos foram confrontadas com a [documentação oficial Flask](https://flask.palletsprojects.com/en/stable/web-security/). Isto não equivale a uma auditoria de segurança externa ou aprovação OWASP ASVS.

## Limitações e operação segura da demonstração

O serviço liga-se a loopback e usa HTTP local. `Secure` e HSTS são ativados apenas com `POS_COOKIE_SECURE=1`; não ativar esta opção sem HTTPS. Não existe reverse proxy/TLS configurado. A senha comum seed é intencionalmente inadequada para contas reais. Não há alteração/reset de passwords, MFA, SSO, provisioning, gestão de privilégios ou revogação global por utilizador na interface.

Rate limit é por par IP/utilizador, não impede força bruta distribuída ou spray entre nomes. Não há WAF, limitação global de pedidos ou auditoria de login falhado por evento. Buckets de tentativas ficam temporariamente na base. Audit não é append-only ao nível do sistema operativo nem resistente a administradores do disco. Logs não têm rotação central automática.

Dependências fixadas e verificadas por `pip-audit`; ver relatório de testes. Uma consulta sem vulnerabilidades conhecidas não demonstra ausência de defeitos, nem substitui pentest. CI configurado para verificar dependências runtime e produzir SBOM CycloneDX; ferramentas de desenvolvimento também constam no lock, mas o scan de entrega incide no runtime.

## Privacidade — análise académica inspirada em DPIA

Finalidade: treino, demonstração e validação técnica. Dados: nomes/utilizadores de personagens, transações fictícias, token hash, CSRF, função/loja e bucket de autenticação. Não há clientes identificados, emails, contactos, NIFs, números de cartão ou informação bancária. O bucket de tentativas é derivado por hash do IP e username; isso não é uma técnica geral de anonimização.

Minimização: não se exige identificação do comprador; nenhum serviço analítico externo; fonts locais; acesso restrito por loja. Retenção técnica: sessões 8h e tentativas 5 min; limpeza no login. Vendas, audit e backups são conservados enquanto existir a base da demonstração. Não foi implementado um motor de retenção/apagamento.

Riscos se forem introduzidos dados reais: associação de comportamento a trabalhadores, exposição de credenciais, acesso a backups, retenção indefinida. Controlos presentes: RBAC, minimização, cookies e proteção de passwords. Trabalho necessário antes de dados reais: definir responsáveis, base de tratamento, transparência, prazos e direitos aplicáveis com revisão competente; proteger/expirar backups e validar políticas. Não se afirma conformidade RGPD a partir desta simulação.

## Resposta a incidente

Interromper a instância se houver suspeita de acesso indevido; preservar base/logs e request IDs; investigar a cópia; revogar sessões comprometidas com manutenção controlada; restaurar uma cópia íntegra e corrigir a causa antes de reabrir. Não foi realizado exercício formal de resposta a incidente.
