# Implementação de Árvore-B (B-Tree) em Python

## Visão Geral
Este projeto oferece uma implementação completa de uma Árvore-B (B-Tree) em Python. Trata-se de uma estrutura de dados balanceada que mantém os dados ordenados e permite operações eficientes de inserção, remoção e busca. A implementação segue os princípios de Design by Contract utilizando a biblioteca `icontract` e inclui uma suíte abrangente de testes unitários.

## Funcionalidades
- **Operações completas da Árvore-B**:
  - Inserção com divisão automática de nós (split)
  - Remoção com fusão ou redistribuição de nós
  - Busca eficiente de chaves
- **Manutenção do Balanceamento**:
  - Rebalanceamento automático durante inserções e remoções
  - Todas as folhas permanecem no mesmo nível da árvore
- **Programação por Contratos (Design by Contract)**:
  - Pré-condições e invariantes validadas usando a biblioteca `icontract`

 
## Instalação e execução
 ```bash
 #Clone o repositório:
   git clone https://github.com/seuusuario/b_tree_project_full.git
   cd b_tree_project_full
 #Instale as dependencias:
   pip install -r requirements.txt
 #Executando os testes:
   python3 -m unittest discover tests
