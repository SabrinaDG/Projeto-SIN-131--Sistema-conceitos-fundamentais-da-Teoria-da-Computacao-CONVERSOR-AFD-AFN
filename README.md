# Autômatos - Conversão, Inserção e Minimização

Este projeto implementa funcionalidades relacionadas a autômatos finitos determinísticos (AFD) e não-determinísticos (AFN), utilizando Flask para o backend e HTML com Bootstrap para o frontend.

## Funcionalidades Implementadas

### Conversão de AFN para AFD

A aplicação permite a conversão de um autômato não-determinístico (AFN) para um autômato determinístico (AFD). A conversão é realizada através do algoritmo de subconjuntos.

### Inserção de AFD

Os usuários podem inserir um autômato finito determinístico (AFD) através de um formulário que solicita o alfabeto, estados, estado inicial, estados finais e regras de transição.

### Minimização de AFD

A funcionalidade de minimização de AFD é implementada utilizando o algoritmo de equivalência de estados. O algoritmo agrupa estados equivalentes para obter um AFD minimizado.

### Equivalência entre AFN e AFD

Por meio de inerção de palavra, verifica-se eles são equivalentes ou não

A diferença na maneira como as transições dos autômatos são tratadas em cada código impactou a capacidade de conversão de AFN para AFD no Arquivo Projeto-SIN-131--Sistema-conceitos-fundamentais-da-Teoria-da-Computacao. Enquanto o Arquivo Projeto-SIN-131--Sistema-conceitos-fundamentais-da-Teoria-da-Computacao-CONVERSOR-AFD-AFN organiza as transições de maneira que facilita a construção do AFD, o Arquivo Projeto-SIN-131--Sistema-conceitos-fundamentais-da-Teoria-da-Computacao armazena as transições em um formato que não se ajusta bem à lógica de conversão, resultando em dificuldades na criação do AFD equivalente. 

### Verificação de Palavras

A aplicação permite verificar se uma palavra é aceita por um autômato determinístico (AFD) inserido pelo usuário. A verificação é feita através da simulação do autômato para a palavra fornecida.

## Funcionamento da Aplicação

A aplicação utiliza Flask como servidor web. Os templates HTML são renderizados com Bootstrap para estilização.

## Instalação

1. **Clone o Repositório**:

    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2. **Instale as Dependências**:

    ```bash
    pip install
    ```

3. **Acesse o App**:

    Abra o navegador e vá para [http://127.0.0.1:5000](http://127.0.0.1:5000).


