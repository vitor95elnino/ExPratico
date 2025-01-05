import random, os

def carregar_txt():
    """
    Esta função, carrega um dicionário de países e capitais a partir de um ficheiro .txt .
    O codigo verifica se existe um ficheiro chamada "jogo_das_capitais.txt".
    Se o ficheiro existir, lê o conteúdo e carrega as informações para um dicionário.
    Se o ficheiro não existir, cria um novo ficheiro vazio, com o nome"jogo_das_capitais.txt e retorna um dicionário vazio."
    O ficheiro deve ter cada linha no formato "país,capital", separado por uma vírgula.

    Neste dicionário os paises são chaves e as capitais os valores.
    """
    jogo_das_capitais = {}
    if os.path.exists("jogo_das_capitais.txt"):
        with open("jogo_das_capitais.txt", "r", encoding="utf-8") as file:
            for line in file:
                pais, capital = line.strip().split(",")
                jogo_das_capitais[pais.lower()] = capital.lower()
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
    Esta função permite ao jogador adicionar novos paises e capitais ao dicionário.
    É Pedido ao jogador para inserir o nome do país e verefica se já existe no dicionario. 
    No caso de ser inserido um pais já existente o processo volta ao inicio pedindo para insirir um novo país.
    Caso não exista, em seguida é pedido para inserir a capital.
    No dicionario está a informação(país,capital) que é guardada numa linha separada por uma virgula.
    Não aceita capitais nem paises em branco e numeros. Caso seja introduzido informa que o mesmo é invalido, e pede para ser insirido novamente. 
    A função 'ver_paises_capitais' permite ao jogador ver o dicionário.
    Este ciclo termina quando o jogador não adicionar mais países e capitais.
    """
    while True:
        
        #País
        while True:
            pais = input("Insira o nome de um país: ").strip().lower()
            if not pais or pais.isdigit():
                print("-> Insira o nome de um país,o campo não pode estar vazio, ou conter números.\n")
                continue
            
            if pais in jogo_das_capitais:
                print(pais +" já existe na base de dados.\n")
                continue
            break

        #Capital    
        while True: 
            capital = input("Insira a capital de " + pais + ": ").strip().lower()
            if not capital or capital.isdigit():
                print("-> Insira uma capital valida, este campo não pode ser vazio, ou conter números.\n")
            else:
                break

        jogo_das_capitais[pais] = capital
        guardar_dados(jogo_das_capitais)
        print("A capital do "+ pais + ", " + capital + " foram adicionadas!\n")
        # Ver Dicionário
        while True:
            opcao = input("\n-> Deseja ver o dicionário ? (s/n): ").strip()
            if opcao == 's':
                ver_paises_capitais(jogo_das_capitais)
                break
            elif opcao == 'n':
                break
            else:
                print("-> Opção inválida. Deseja ver o dicionário ? (s/n): ")

        #Sair
        continuar = input("\n-> Deseja adicionar mais países e capitais? (s/n): ").strip()
        if continuar in ['s', 'n']:
            if continuar == 'n':
                break
        else:
            print("-> Opção Invalida. Deseja adicionar mais países e capitais? (s/n): ")  


def jogar_jogo(jogo_das_capitais, nome=None):
    """
    Função para iniciar o jogo. 
    Verifica se o dicionário tem pelo menos 10 paises e capitais.
    Se não existir, o jogador é avisado que para começar a jogar terá que adicionar mais paises e capitais ao dicionário e é chamada a função adicionar.
    Caso existam pelo menos 10, é usado um random para seleciona aleatoriamente 10 paises e perguntar as suas capitais. 
    Por cada resposta certa o jogador recebe 1 ponto. Esse ponto é somado a variavel pontuacao que inicia a 0.
    O jogador é informado sempre que acerta ou erra uma capital.
    Por ultimo é mostrado no ecrã quantas capitais o jogador respondeu correto(pontuação) e o total de perguntas (total_perguntas = len(jogo_das_capitais)), 
    é perguntado ao jogador se deseja continuar, caso o jogador continue a jogar, o nome do jogador fornecido no parâmetro 'nome' é reutilizado.
    """

    if len(jogo_das_capitais) < 10:
        print("Não há dados disponiveis. Precisa de ter 10 países e as respetivas capitais para começar a jogar. \n")
        adicionar(jogo_das_capitais)
        return

    if nome is None:
        while True:
            nome = input("Insira o nome do Jogador: ").strip().lower()
            if nome:
                break
            else:
                print("Insira o nome do Jogador, este campo não pode estar em branco.\n")

    pontuacao = 0
    total_capitais = min(10, len(jogo_das_capitais))
    perguntas = random.sample(list(jogo_das_capitais.items()), total_capitais)

    for pais, capital in perguntas:
        resposta = input("\nQual é a capital de "  + pais + "? ").strip().lower()
        if resposta.lower() == capital:
            print("Correto!")
            pontuacao += 1
        else:
           print("Errado.\nA capital é " + capital + ".")
    print("\n"+ str(nome) + " acertou em " + str(pontuacao) + " de " + str(total_capitais) + " capitais.\n")

    while True:
        continuar = input("\n->"+nome+ " deseja continuar a jogar ? (s/n): ").strip().lower()
        if continuar in ['s', 'n']:
            if continuar == 's':
                jogar_jogo(jogo_das_capitais, nome)
                break
            elif continuar == 'n':
                break
        else:
            print("Opção Invalida. Deseja adicionar mais países e capitais? (s/n): ")  


def ver_paises_capitais(jogo_das_capitais):
    """
    Função para visualizar conteúdo do dicionário.
    Exibe no ecrã o conteúdo do dicionario 'jogo_das_capitais', após ser exibido no ecrã aguarda uma instrução do utilizador para avançar.
    """
    with open("jogo_das_capitais.txt", "r", encoding="utf-8") as file:
        conteudo = file.read()
        print("\nConteúdo do arquivo jogo_das_capitais.txt:\n")
        print(conteudo)

    while True:
        voltar = input("\nPressione ENTER para voltar atrás ")
        return 
        

def main():
    """
    Função principal
    Começa por carregar os dados do dicionario.
    Exibe um menu de seleção(1,2,3,4)que permite:
        1- Jogar: Permite ao jogador começar a jogar. 
        2- Adicionar: Permite ao jogador adicionar novos países e capitais ao dicionário. 
        3- Ver dicionário: Chama a função ver_paises_capitais para o jogador ver o dicionário.
        4- Sair: Sai do programa.
        Caso de selecionar outra opção, aparece no ecrã a msg:"Opção inválida. Tente novamente."
    """
    jogo_das_capitais = carregar_txt()

    while True:
        
        print("\nBem-Vindo ao Jogo das Capitais! \n")
        print("Selecione uma das opções para começar.\n")
        print("-> 1 - Jogar")
        print("-> 2 - Adicionar País e Capital")
        print("-> 3 - Ver dicionário")
        print("-> 4 - Sair \n")
        
        opcao = int(input("Escolha uma opção: "))
        
        if opcao == 1:
            jogar_jogo(jogo_das_capitais)
        elif opcao == 2:
            adicionar(jogo_das_capitais)
        elif opcao == 3:
            ver_paises_capitais(jogo_das_capitais)
        elif opcao == 4:
            print("Adeus, Volte mais Tarde")
            break
        else:
                print("Opção inválida. Tente novamente.")


if __name__ == '__main__':
    main()