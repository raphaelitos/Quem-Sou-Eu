# 🎮 Quem Sou Eu? – Jogo em Rede com Python e Sockets

Este projeto é um jogo interativo de adivinhação chamado **"Quem Sou Eu?"**, desenvolvido em Python com comunicação entre **duas máquinas via sockets**. O projeto foi criado como parte da disciplina de **Redes de Computadores**, com o objetivo de explorar conceitos de comunicação cliente-servidor.

---

## 🧠 Sobre o Jogo

O jogo consiste em dois jogadores: um define uma "personalidade" (pessoa famosa, personagem, etc.) e o outro tenta adivinhar fazendo perguntas de sim/não, com base nas respostas recebidas. A comunicação entre os jogadores acontece via rede local (TCP/IP).

---

## 📌 Objetivos do Projeto

- Implementar comunicação cliente-servidor usando **sockets TCP em Python**
- Aplicar conceitos de redes: IP, porta, conexão, troca de mensagens
- Criar uma interface de interação simples e funcional entre os dois jogadores
- Promover a experiência de desenvolvimento de aplicações distribuídas

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- Biblioteca padrão `socket`
- (Opcional) `threading` para múltiplas conexões
- Execução em terminal

---

## 📁 Estrutura do Projeto

```

quem-sou-eu/
├── cliente.py         # Código do cliente (jogador que adivinha)
├── servidor.py        # Código do servidor (jogador que escolhe)
├── README.md

````

---

## 🚀 Como Executar

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/Quem-Sou-Eu.git
cd quem-sou-eu
````

### 2. Executar o servidor (máquina 1)

```bash
python servidor.py
```

### 3. Executar o cliente (máquina 2)

```bash
python cliente.py
```

> Certifique-se de que ambas as máquinas estão na **mesma rede local** e que o **IP e porta** do servidor estão corretamente configurados no cliente.

