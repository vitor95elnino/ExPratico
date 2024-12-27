import random

def carregar_txt():
    jogo_das_capitais = {}
    try:
        with open("jogo_das_capitais.txt", "r", encoding="utf-8") as file:
            for line in file:
                pais, capital = line.strip().split(",")
                jogo_das_capitais[pais] = capital
    except FileNotFoundError:
        print("Ficheiro não encontrado. A criar um novo ficheiro.")
        open("jogo_das_capitais.txt", "w").close()  # Cria um ficheiro vazio
    return jogo_das_capitais


def guardar_dados(jogo_das_capitais):
    with open("jogo_das_capitais.txt", "w", encoding="utf-8") as file:
        for pais, capital in jogo_das_capitais.items():
            file.write(pais + "," + capital + "\n")


def adicionar(jogo_das_capitais):
    while True:
        pais = input("Insira o nome do país: ").strip()
        if pais in jogo_das_capitais:
            print(pais +" já existe na base de dados.\n")
            continue
        capital = input("Insira o nome da capital de " + pais + ": ").strip()
        jogo_das_capitais[pais] = capital
        guardar_dados(jogo_das_capitais)
        print(pais + " e a sua capital " + capital + " foram adicionados!\n")
        continuar = input("Deseja adicionar mais países e capitais? (s/n): ")
        if continuar == 'n':
            break


def jogar_quiz(jogo_das_capitais):
    jogador = input("Insira o nome do Jogador: ")
    if not jogo_das_capitais:
        print("Não há dados disponiveis. Adicione países e capitais para começar a jogar. \n")
        return

    pontuacao = 0
    total_perguntas = len(jogo_das_capitais)
    perguntas = random.sample(list(jogo_das_capitais.items()), total_perguntas)

    for pais, capital in perguntas:
        resposta = input("Qual é a capital de "  + pais + "? ").strip()
        if resposta.lower() == capital.lower():
            print("Correto!")
            pontuacao += 1
        else:
           print("Errado. A capital é " + capital + ".")
    print(str(jogador) + " acertou " + str(pontuacao) + " em " + str(total_perguntas) + " capitais.\n")


def main():

    jogo_das_capitais = carregar_txt()

    while True:
        
        print ("\nMenu: Quiz das Capitais \n")
        print ("-> 1. Jogar")
        print ("-> 2. Adicionar País e Capital")
        print ("-> 3. Sair \n")
        
        opcao = int(input("Escolha uma opção: "))
        
        if opcao == 1:
            jogar_quiz(jogo_das_capitais)
        elif opcao == 2:
            adicionar(jogo_das_capitais)
        elif opcao == 3:
            print("Adeus, Volte mais Tarde")
            break
        else:
                print("Opção inválida. Tente novamente.")

if __name__ == '__main__':
    main()
