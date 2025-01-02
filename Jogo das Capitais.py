import random, os

def carregar_txt():
    """
    Abre o ficheiro jogo_das_capitais.txt e lê os valores de cada linha, divide em pais e capital, separados por uma virgula, 
    e guarda-os num dicionário , retorna os paises como chave e as capitais como valores. 
    Caso o ficheiro não exista, abre um novo ficheiro vazio. 
    """
    jogo_das_capitais = {}
    if os.path.exists("jogo_das_capitais.txt"):
        with open("jogo_das_capitais.txt", "r", encoding="utf-8") as file:
            for line in file:
                pais, capital = line.strip().split(",")
                jogo_das_capitais[pais] = capital
    else:
        print("Ficheiro não encontrado. A criar um novo ficheiro.")
        open("jogo_das_capitais.txt", "w").close()  

    return jogo_das_capitais


def guardar_dados(jogo_das_capitais):
    """
    Guarda no ficheiro jogo_das_capitais.txt os paises e as capitais, separados por uma virgula. 

    jogo_das_capitais: Dicionário com países como chaves e capitais como valores.
    """
    with open("jogo_das_capitais.txt", "w", encoding="utf-8") as file:
        for pais, capital in jogo_das_capitais.items():
            file.write(pais + "," + capital + "\n")


def adicionar(jogo_das_capitais):
    """
    Adiciona novos paises e capitais ao jogo (jogo_das_capitais.txt).
    Pede ao utilizador para inserir o nome do país e verefica se já existe no dicionario.
    Caso não exista, em seguida é pedido para inserir a capital. Caso seja inserido um pais já existente o processo volta ao inicio pedindo para insirir um novo país.
    No dicionario .txt está a informação(país,capital) que é guardada numa linha separada por uma virgula.
    Não aceita capitais nem paises "em branco" e numeros. Caso seja introduzido informa que o mesmo é invalido, e pede para ser insirido novamente. 
    No final é pedido ao utilizador se desaja continuar, caso este responda 'n' a função termina.
 
    """
    while True:
        
        #País
        while True:
            pais = input("Insira o nome do país: ").strip()
            if not pais or pais.isdigit():
                print("Insira o nome do país,o campo não pode estar vazio, ou conter números.\n")
                continue
            
            if pais in jogo_das_capitais:
                print(pais +" já existe na base de dados.\n")
                continue
            break

        #Capital    
        while True: 
            capital = input("Insira o nome da capital de " + pais + ": ").strip()
            if not capital or capital.isdigit():
                print("Insira uma capital Valida, este campo não pode ser vazio, ou conter números.\n")
            else:
                break

        jogo_das_capitais[pais] = capital
        guardar_dados(jogo_das_capitais)
        print(pais + " e a sua capital " + capital + " foram adicionados!\n")

        #Sair
        continuar = input("\nDeseja adicionar mais países e capitais? (s/n): ").strip()
        if continuar in ['s', 'n']:
            if continuar == 'n':
                break
        else:
            print("Opção Invalida. Deseja adicionar mais países e capitais? (s/n): ")  


def jogar_quiz(jogo_das_capitais):
    """
    Função para iniciar o jogo. 
    Verifica no dicionário se há pelo menos 10 paises e capitais no dicionário.
    Se não existir, o jogador é avisado que para começar a jogar terá que adcionar mais paises e capitais ao dicionário.
    Caso exista 10 ou mais, a função atráves do "random" seleciona aleatoriamente 10 paises e pergunta as suas capitais. 
    A função atrás da variavel pontuação, que inicia a 0, sempre que o jogador acerta uma capital, é adicionado +1 ponto a variavel pontuação, caso o jogador responda errado, é 
    mostrado no ecrã resposta errada e a respectiva resposta correta.
    No final é mostrado no ecrã quantas capitais o jogador respondeu correto(pontuação) e o total de perguntas (total_perguntas = len(jogo_das_capitais))
    """

    if len(jogo_das_capitais) < 10:
        print("Não há dados disponiveis. Adicione pelo menos 10 países e capitais para começar a jogar. \n")
        return
    nome = input("Insira o nome do Jogador: ")

    pontuacao = 0
    total_perguntas = min(10, len(jogo_das_capitais))
    perguntas = random.sample(list(jogo_das_capitais.items()), total_perguntas)

    for pais, capital in perguntas:
        resposta = input("Qual é a capital de "  + pais + "? ").strip()
        if resposta.lower() == capital.lower():
            print("Correto!\n")
            pontuacao += 1
        else:
           print("Errado. A capital é " + capital + ".\n")
    print(str(nome) + " acertou " + str(pontuacao) + " em " + str(total_perguntas) + " capitais.\n")


def main():
    """
    Função principal
    Começa por carregar os dados do dicionario.
    Exibe um menu de seleção(1,2,3)que permite:
        1 - Jogar: permite ao jogador começar o Quiz. 
        2- Adicionar: utiliza a função ... para permitir ao jogador adicionar novos países e capitais.
        3- Sair: sai do programa
        Caso de selecionar outra opção, aparece no ecrã a msg:"Opção inválida. Tente novamente."
    """
    jogo_das_capitais = carregar_txt()

    while True:
        
        print ("\nMenu: Quiz das Capitais \n")
        print ("-> 1 - Jogar")
        print ("-> 2 - Adicionar País e Capital")
        print ("-> 3 - Sair \n")
        
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