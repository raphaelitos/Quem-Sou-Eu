# Quem Sou Eu? – Jogo em Rede com Python e Sockets

Este projeto é um jogo interativo de adivinhação chamado **"Quem Sou Eu?"**, desenvolvido em Python com comunicação entre **duas máquinas via sockets**. O projeto foi criado como parte da disciplina de **Redes de Computadores**, com o objetivo de explorar conceitos de comunicação cliente-servidor.

---

## Sobre o Jogo

O jogo consiste em dois jogadores: um define uma "personalidade" (pessoa famosa, personagem, etc.) e o outro tenta adivinhar fazendo perguntas de sim/não, com base nas respostas recebidas. A comunicação entre os jogadores acontece via rede local (TCP/IP).

---

## Objetivos do Projeto

- Implementar comunicação cliente-servidor usando **sockets TCP em Python**
- Aplicar conceitos de redes: IP, porta, conexão, troca de mensagens
- Criar uma interface de interação simples e funcional entre os dois jogadores
- Promover a experiência de desenvolvimento de aplicações distribuídas

---

## Tecnologias Utilizadas

- **Python 3.x**
- `socket` – Comunicação TCP/IP entre cliente e servidor
- `threading` – Gerenciamento de múltiplas conexões (para versões futuras)
- `json` – Estruturação das mensagens trocadas
- Interface em **linha de comando (terminal)**

---

## 📁 Estrutura do Projeto

```
Quem-Sou-Eu/
├── client.py         # Código do cliente (jogadores)
├── game.py         # Código das regras de jogo (Quem sou eu)
├── protocol.py
├── server.py        # Código do servidor que hospeda as partidas
├── README.md
```

---

## Como Executar

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/Quem-Sou-Eu.git
cd Quem-Sou-Eu
```

### 2. Executar o servidor

```bash
python3 server.py
```

### 3. Executar o cliente

```bash
python3 client.py
```

> Certifique-se de que as máquinas estão na **mesma rede local** e que o **IP e porta** do servidor estão corretamente configurados no cliente. É possível usar VPN para conexões entre as máquinas.

