# Autômatos - Conversão, Inserção, Minimização, Equivalência e Máquina de Turing

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

Neste caso, ao salvar o AFN, vai para a parte de validar a palavra em AFN e depois ao clicar no botão de "converter para AFD", basta inserir a mesma palavra inserida na página anterior e verificar se a mesma é válida ou não.


### Verificação de Palavras

A aplicação permite verificar se uma palavra é aceita por um autômato determinístico (AFD) e autômato finito não-determinístico (AFN) inserido pelo usuário. A verificação é feita através da simulação do autômato para a palavra fornecida.

### Máquina de Turing

A Máquina de Turing é um modelo teórico de computação que serve como uma base para entender a computabilidade e a complexidade de algoritmos. No contexto deste projeto, a implementação da Máquina de Turing permite simular o processamento de cadeias de caracteres, avaliando sua aceitação por meio de estados e transições definidas.

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
    pip install -r requirements.txt
    ```

3. **Execute a Aplicação**:

    ```bash
    python app.py
    ```

3. **Acesse o App**:

    Abra o navegador e vá para [http://127.0.0.1:5000](http://127.0.0.1:5000).


