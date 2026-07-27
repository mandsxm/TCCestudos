from flask import Flask, render_template, request, jsonify, redirect, session, url_for #bibliotecas
#render_template: Renderiza arquivos HTML armazenados na pasta templates; Permite enviar dados do Python para o HTML.
#request: Acessa os dados enviados pelo navegador (formulários, parâmetros da URL, JSON etc.).
#jsonify: Converte dicionários ou listas do Python em uma resposta JSON. Muito utilizado em APIs.
#redirect: Redireciona o usuário para outra página
#session: Armazena informações do usuário durante a navegação, como login.
#url_for: Gera URLs automaticamente para rotas da aplicação. Evita escrever caminhos manualmente.
import mysql.connector #conectar com o banco de dados
import os #interage com o sistema operacional (pastas, arquivos) | usado para criar a pasta uploads caso ela não exista
import bcrypt #criptografia da senha
from werkzeug.utils import secure_filename #para segurança com nome dos arquivos enviados no sistema pelos usuários

app = Flask(__name__) #criação da aplicação principal flask
app.secret_key = "brasil" #cria uma senha que o flask usa para proteger dados sensíveis

# GERAR SENHA BCRYPT
def gerar_hash(senha_texto): #cria a função 'gerar_hash' que pega a 'senha_texto', a senha 123456
    senha_bytes = senha_texto.encode('utf-8') #bcrypt nao trabalha com string, e sim com bytes | aqui ele transforma a senha comum em bytes usando a codificação UTF-8 que transforma caracteres em numeros que o computador entende
    salt = bcrypt.gensalt() #gensalt() = generate salt | salt faz com que mesmo que dois users usem senhas iguais, tipo 123456, os hashes serão diferentes e não identicos. Assim, não é possível que alguém descubra o padrão entre as duas senhas iguais.
    senha_hash = bcrypt.hashpw(senha_bytes, salt) #pega os bytes gerado + o salt gerado e transforma na senha em hash | hashpw = hash password
    return senha_hash.decode('utf-8') #retorna o valor em bytes(linguegem que o pc entende) em uma string (texto comum que nóe entendemos) | processo inverso do encode
    #pq precisa do decode? | Pq o banco espera receber um 'VARCHAR', uma string de texto, não um objeto bytes do Python, então nós precisamos converter os bytes para uma string para que o banco de dados consiga receber esse dado

def verificar_senha(senha_digitada, hash_armazenado): #serve pra verificar a senha que foi digitada na hora do login, pra ver se a senha digitada bate com a senha hash
    if not hash_armazenado: #se não for a senha hash 
        return False #vai dar erro, login negado
    senha_bytes = senha_digitada.encode('utf-8') #converte a senha digitada na hora do login para bytes
    hash_bytes = hash_armazenado.encode('utf-8') #converte a senha que está armazenada para bytes (pq ela veio do banco de dados como texto na hora de verificar)
    return bcrypt.checkpw(senha_bytes, hash_bytes) #o checkpw (check password) pega a senha digitada, extrai o salt do hash_armazenado e cria um novo hash para a senha digitada usando esse mesmo salt, e comparar os dois hashs
        #se os hashs baterem, vai retornar true (senha correta), se não retorna false (senha incorreta)

# CONEXÃO
def get_db(): #abre e devolve uma conexão com banco de dados
    return mysql.connector.connect( #retorna a conexão com o banco
        host='127.0.0.1', #onde ta rodando, localhost
        user='root', #nome de user do mysql | root é o user sdmin padrao do mysql
        password='', #senha do user
        database='almoxarifado', #qual banco de dados quer usar depois de conectar
    )

# AUTORIZAÇÃO - necessário para que os usuarios só consigam ver o sistema se estiverem logados nele, para evitar que qualquer só coloque uma url e consiga entrar no sistema e ver os dados do almoxarifado
def login_required(): #vê se alguém ta logado
    return 'usuario' in session #vê se tem uma chave 'usuario' dentro da sessão | se a pessoa fez login, essa chave existe

def admin_required(): #vê se o usuario logado é um admin
    return session.get('tipo') == 'admin' #vê se o tipo (no banco de dados) do usuario dentro da sessão é 'admin'

# HOME
@app.route('/') #rota raiz do site, a primeira página quando abre o site, página inicial
def home(): #executa a função home
    return render_template('index.html') #retorna a página index.html

# LOGIN
@app.route('/login', methods=['POST']) #rota de login, metódo POST envia dados pro servidor por causa dos formulários
def login(): #executa a função login
    email = request.form.get('email') #recebe e devolve o email que foi enviado no formulário
    senha = request.form.get('senha') #recebe e devolve a senha que foi enviada no formulário

    conexao = get_db() #abre uma conexão com o banco
    cursor = conexao.cursor() #cria um cursor que vai excutar funções do banco (o raiozinho automático)

    cursor.execute(""" 
        SELECT * FROM usuarios 
        WHERE email = %s 
    """, (email,)) #o cursor vai executar o SELECT * FROM usuarios (busca todas as colunas da tabela) onde o email seja igual a algum valor
    #"%s" é um placeholder () que o mysql.connector reconhece e diz que ali tem um valor que vai ser enviado pra ele separadamente
    #o (email) é uma tupla, que é o valor que vai substituir o %s

    #PARA TESTE:
    user = cursor.fetchone() #vai pegar o primeiro item que aparecer na linha de user que bater com o "WHERE email"
    print(user) #vai printar a linha do resultado do user

    cursor.close() #fecha o cursor 
    conexao.close() #fecha a conexão
    #para não sobrecarregar o servidor

    if user and verificar_senha(senha, user[4]): #se o usuario existe e se a senha enviada bater com o hash | user[4] é a posição que o hash ta na coluna
        session['usuario'] = user[1] #guarda o usuario na sessão
        session['email'] = user[2] #guarda o email na sessão
        session['tipo'] = user[3] #guarda o tipo na sessão
        return redirect('/tabela') #redireciona para a página /tabela | redirect = redireciona para outra URL

    return render_template ('login_erro.html', erro=True) #se não estiver de acordo com o if, então retorna para a página de login_erro e diz que a variável erro é verdadeira

# LOGIN INCORRETO
@app.route('/login_erro.html') #rota do erro de login
def login_erro(): #executa a função do erro de login
    return render_template('login_erro.html') #retorna a página login_erro

# LOGOUT
@app.route('/logout') #rota de logout
def logout(): #executa a função logout
    session.clear() #limpa a sessão atual do usuário
    return redirect(url_for('home')) #redireciona para a url home (página de login) | url_for = gera uma url a partir do nome de uma função de rota

# TABELA
@app.route('/tabela') #rota de tabela
def tabela(): #executa a função tabela
    if not login_required(): #se o usuário não estiver logado
        return redirect('/') #redireciona para a página inicial

    conexao = get_db() #abre a conexão com o banco de dados
    cursor = conexao.cursor() #cria o cursor

    cursor.execute("SELECT * FROM estoque") #pede para executar essa função no banco de dados
    resultado = cursor.fetchall() #pega todas as linhas que a consulta encontrou

    cursor.close() #fecha o cursor
    conexao.close() #fecha a conexão

    return render_template('tabela.html', resultado=resultado) #redireciona para a página tabela.html e vai mostrar o resultado da consulta na página tabela JINJA2

# ENTRADA / SAÍDA ESTOQUE

@app.route('/entrada', methods=['POST']) #rota de entrada com método POST que envia dados pro servidor
def entrada(): #executa a função entrada - função que processa esse envio

    #request.form = dicionário com os dados enviados no forms | .get('...') = busca o valor de cada campo de acordo com o name="" do HTML
    nome = request.form.get('nome') #vai pegar o nome enviado no formulário
    categoria = request.form.get('categoria') #vai pegar a categoria enviada no formulário
    qtde = request.form.get('qtde') #vai pegar a quantidade enviada no formulário
    responsavel = request.form.get('responsavel') #vai pegar o responsável enviado no formulário
    estoque_min = request.form.get('estoque_min') #vai pegar o estoque mínimo enviado no formulário
    preco = request.form.get('preco') #vai pegar o preço enviado no formulário
    descricao = request.form.get('descricao') #vai pegar a descrição enviada no formulário
    tipo = request.form.get('tipo') #vai pegar o tipo enviado no formulário
    imagem = request.files.get("imagem") #vai pegar o arquivo da a imagem enviado no formulário, se foi enviado algo

    if imagem: #se a imagem existe (se foi enviada)| verifica se realmente foi enviada uma imagem ou não
        nome_arquivo = secure_filename(imagem.filename) #pega o nome do arquivo e aplica o secure_filename (vai limpar o nome para evitar que seja um nome maliciose que sobreponha algum arquivo do sistema | remove caracteres perigosos)

        pasta = os.path.join("static", "uploads") #os.path.join(...) = monta um caminho de pasta juntando pedaços | ao invés de precisar escrever manualmente "static/uploads", ele faz isso automaticamente | ele mostra onde as imagens enviadas vão ser armazenadas dentro do sistema
        os.makedirs(pasta, exist_ok=True) #os.makedirs = ele cria a pasta caso ela não exista | (pasta, exist_ok=True) = confere se as pastas "static/uploads" existe, se existir nao precisa criar

        caminho_salvar = os.path.join(pasta, nome_arquivo) #cria o caminho completo de onde o arquivo vai ficar juntando o caminhos das pastas static/uploads com o nome do arquivo enviado já limpo com secure_filename
        imagem.save(caminho_salvar) #salva a imagem no caminho criado

        caminho_imagem = url_for('static', filename=f'uploads/{nome_arquivo}') #cria a url (caminho web) do caminho do arquivo salvo, que é o valor que vai ser salvo dentro da tabela no site | o f'{}' é uma string formatada do py, que permite colocar uma variável dentro de {}
    else: #se não houver imagem enviada
        conexao = get_db() #abre a conexão com o banco de dados
        cursor = conexao.cursor() #abre o cursor - raiozinho automático

        cursor.execute("SELECT imagem FROM estoque WHERE nome = %s", (nome,)) # cursor vai selecionar a imagem da tabela estoque a coluna imagem em que o item bate com o nome enviado no forms 
        foto = cursor.fetchone() #pega o primeiro resultado | a primeira imagem, que vai formar uma tupla de valor único
        caminho_imagem = foto[0] #pega o único valor de dentro da tupla (o caminho da imagem que já estava salva) | resultado: o item vai continuar com a imagem que já estava salva antes, não vai adicionar nenhuma outra imagem
        cursor.close() #fecha o cursor
        conexao.close() #fecha a conexão com o banco

    if not nome or not qtde or not responsavel or not tipo: #se não foi enviado nome, quantidade, responsável ou tipo:
        return jsonify({"success": False, "erro": "Campos obrigatórios"}), 400 #retorna uma mensagem escrito que o campo é obrigatório | erro 400 = bad request (requisição inválida), o que foi enviado ta errado
    qtde = int(qtde) #qtde = número inteiro | converte a string de qtde em um número inteiro para contas matemáticas

    conexao = get_db() #abre conexão com o banco de dados
    cursor = conexao.cursor() #abre o cursor

    cursor.execute("SELECT qtde, preco FROM estoque WHERE nome = %s", (nome,)) #cursor executa a busca de quantidade e preço da tabela estoque em que o nome bate com o nome enviado no forms
    item = cursor.fetchone() #cursor seleciona o primeiro resultado | tupla com dois elementos | primeira consulta pra ver se o item existe


    if item: #se existir o item

        cursor.execute(""" 
            SELECT categoria, estoque_min, descricao, preco
            FROM estoque
            WHERE nome = %s
        """, (nome,)) #segunda consulta | cursor vai executar a busca de categoria, estoque mínimo, descrição e preço da tabela estoque onde o nome bate com o nome enviado no forms

        dados = cursor.fetchone() #cursor vai pegar o primeiro resultado | tupla com 4 elementos

        categoria_atual, estoque_min_atual, descricao_atual, preco_atual = dados #desempacota a tupla para atribuir uma variável pra cada elemento da tupla

        categoria = categoria if categoria else categoria_atual #categoria vai valer como categoria que veio do forms se a categoria existir, se não a categoria vai continuar valendo como a categoria que estava salva no banco, sem ser alterada

        estoque_min = ( 
            int(estoque_min) #transforma a string enviada no forms em um número inteiro para matemática
            if estoque_min #se foi enviado um estoque_min no forms
            else estoque_min_atual #se não foi enviado um estoque_min, continua valendo o valor que já estava no banco de dadso sem ser alterado
        )

        descricao = descricao if descricao else descricao_atual #se foi enviado uma descrição no forms, usa ela, se não deixa com o valor que já tava no banco

        if preco: #se um preço foi enviado
            preco = float(preco) #transforma a string dele em decimal
        else: #se não foi enviado
            preco = 0 #preço será igual a 0 - zera o preço - não vai ter definição de preço já que nada foi enviado

# ENTRADA (SOMA)
    if tipo == "entrada": #se o tipo foi de entrada de item do estoque | o "tipo" vem do js

        if item: #se o item existe no estoque
            qtde_atual, preco_atual = item #pega a quantidade e preço atual do item

            nova_qtde = qtde_atual + qtde #faz a soma da quantidade de antes e quanto foi adicionado
            novo_preco = float(preco_atual) + float(preco) #faz a soma do preço de antes e quanto foi adicionado
            
            cursor.execute("""
                UPDATE estoque
                SET qtde = %s,
                    estoque_min = %s,
                    categoria = %s,
                    preco = %s,
                    descricao = %s,
                    imagem = %s
                WHERE nome = %s
            """, (nova_qtde, estoque_min, categoria, novo_preco, descricao, caminho_imagem, nome)) #cursor vai atualizar no estoque os valores novos desse item
            conexao.commit() #autoriza a atualização dos valores do banco de dados
        else: #se não existe no estoque ainda
            cursor.execute("""
                INSERT INTO estoque
                (responsavel, nome, categoria, qtde, estoque_min, descricao, preco, imagem)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (responsavel, nome, categoria, qtde, estoque_min, descricao, preco, caminho_imagem)) #o cursor vai inserir no banco os valores que foram enviados no forms

        conexao.commit() #autoriza a atualização dos valores do banco de dados

# SAÍDA (SUBTRAI)
    elif tipo == "saida": #se o tipo foi de saída de item do estoque | o "tipo" vem do js | elif = else if (se a condição anterior if tipo == entrada for falsa)

        cursor.execute(
            "SELECT qtde, preco FROM estoque WHERE nome = %s",
            (nome,) #o cursor vai pegar a quantidade e o preço do estoque onde o o nome bata com o que foi enviado no forms
        )

        produto = cursor.fetchone() #cursor vai pegar o primeiro resultado do banco, que será o produto

        if not produto: #se não tiver um produto no banco com esse nome
            return jsonify({
                "success": False,
                "erro": "Produto não encontrado"
            }), 404 #vai enviar uma mensagem de produto não encontrado | 404 = Not Found (não encontrado)

        qtde_atual, preco_atual = produto #produto é uma tupla com dois valores dentro, quantidade atual e preço atual | desempacota a tupla e atribui uma variável a elas | extrai os valores da tupla de dentro dela atribuindo uma variável pra cada uma separadamente

        if qtde_atual < qtde: #se a quantidade atual for menor que a quantidade enviada no forms
            return jsonify({
                "success": False,
                "erro": "Estoque insuficiente"
            }), 400 #retorna uma mensagem que o estoque é insuficiente, não tem como pegar aquela quantidade daquele item pq não tem o suficiente no estoque
                    #400 = Bad Request (o que foi enviado ta errado)
                    
        nova_qtde = qtde_atual - qtde #o valor da nova quantidade após a saída de item será a quantidade atual - a quantidade enviada no forms
        novo_preco = float(preco_atual) - float(preco) #o novo preço desse item no estoque é o preço atual - o preço enviado no forms | o float() converte a string enviada no forms, para um número decimal para que possa realizar equações matemáticas

        if novo_preco < 0: #se o preço for menor que zero
            novo_preco = 0 #então o valor do produto no estoque será 0

        cursor.execute("""
            UPDATE estoque
            SET qtde = %s,
                estoque_min = %s,
                categoria = %s,
                preco = %s,
                descricao = %s,
                imagem = %s
            WHERE nome = %s
        """, ( #o cursor vai atualizar os itens no estoque onde o nome do item bate com o que foi enviado no forms
            nova_qtde,
            estoque_min,
            categoria,
            novo_preco,
            descricao,
            caminho_imagem,
            nome
        )) ##os valores da tupla preenchem os %s do SQL, na mesma ordem | usar tupla separada (em vez de colar os valores direto no texto do SQL) evita SQL Injection, porque o valor nunca é tratado como parte do comando, só como dado

        conexao.commit() #autoriza a atualização dos valores do banco de dados

    else: #se não for nem entrada nem saída de item | esse return acontece ANTES do cursor.close()/conexao.close() lá embaixo, então nesse caminho a conexão nunca é fechada
        return jsonify({"success": False, "erro": "Tipo inválido"}), 400 #400 = Bad Request (oq foi enviado ta errado)

    cursor.close() #fecha o cursor
    conexao.close() #fecha a conexão

    return jsonify({"success": True}), 200 #se tudo deu certo, sem erros com entrada e saída, retorna uma resposta de sucesso | 200 = diz que está tudo certo

# EXCLUIR ITEM
@app.route('/excluir/<int:id>', methods=['DELETE']) #cria a rota escluir | /<int:id> = aqui vai vir um valor dinâmico que será interpretado como um número inteiro e vai ficar disponível dentro da função id (serve para que essa rota funcione para todo os itens e não precise criar uma rota para cada item) | method DELETE = quero remover algo
def excluir(id): #define a função excluir | o flask já entrega esse valor requisitado convertido para um número inteiro

    conexao = get_db() #abre a conexão no banco
    cursor = conexao.cursor() #abre o cursor no banco

    cursor.execute("DELETE FROM estoque WHERE id = %s", (id,)) #cursor deleta do estoque onde o id bate com o valor recebido (id do item no estoque do site que queremos excluir) | neste caso, é melhor usar o id pq ele é único para cada item
    conexao.commit() #autoriza as atualizações no banco

    cursor.close() #fecha o cursor
    conexao.close() #fecha a conexão

    return jsonify({"success": True}) #retorna a resposta que deu certo | js vai interpretar que a ação foi um sucesso | código 200 implícito

# EDITAR
@app.route('/editar') #cria a rota de editar
def editar(): #define função editar
    if not login_required(): #confere se a pessoa está logada antes de deixar ter acesso a página | LOGIN_required e não ADMIN_required significa que qualquer usuario pode ter acesso a página
        return redirect('/') #redireciona o usuário pra tela inicial

    return render_template('editar.html')#mostra a tela editar pro usuário

# ACESSO
@app.route('/acesso') #cria a rota acesso com método GET
def acesso(): #define a função acesso
    if not login_required(): #se não tiver logado
        return redirect('/') #volta pra página inicial

    if not admin_required(): #se não tiver logado como admin
        return "Acesso negado" #acesso negado

    conexao = get_db() #abre a conexão com banco
    cursor = conexao.cursor() #abre o cursor

    cursor.execute("SELECT * FROM usuarios") #cursor vai selecionar tudo da tabela usuários
    resultado = cursor.fetchall() #pega tudo que tiver na tabela usuarios e guardar na variável resultado

    cursor.close() #fecha o cursor
    conexao.close() #fecha a conexão com o banco

    return render_template('acesso.html', resultado=resultado) #carrega a página de acesso | "resultado=resultado" = disponibiliza a lista do resultado para o jinja2 ({% for %} dentro do HTML) colocar os dados na tabela do site

# EXCLUIR USUÁRIO
@app.route('/excluirUsuario/<int:id>', methods=['DELETE']) #cria a rota excluirUsuario | /<int:id> = aqui vai vir um valor dinâmico que será interpretado como um número inteiro e vai ficar disponível dentro da função id (serve para que essa rota funcione para todo os itens e não precise criar uma rota para cada item) | method DELETE = quero remover algo
def excluir_usuario(id): #define a função excluir_usuario

    conexao = get_db() #abre a conexão com o banco
    cursor = conexao.cursor() #abre o cursor

    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,)) #o cursor vai deletar da tabela usuário o id que bater com o id do usuário que foi selecionado lá no site

    conexao.commit() #vai autorizar a atualização no banco

    cursor.close() #fecha o cursor
    conexao.close() #fecha a conexão

    return jsonify({"success": True}) #avisa o js que deu tudo certo | código 200 implícito

# CADASTRO
@app.route('/cadastro', methods=['GET', 'POST']) #cria a rota cadastro | método GET (só mostra a página) e POST (recebe dados)
def cadastro(): #define a função cadastro

    if not login_required(): #se não estiver logado
        return redirect('/') #vai para a página inicial

    if not admin_required(): #se não estiver logado como admin
        return "Acesso negado" #acesso negado a página

    if request.method == 'GET': #request.method = diz qual método HTTP ta sendo utilizado nessa requisição específica (o resto continua POST)
        return render_template('cadastro.html') #carrega a página de cadastro

    usuario = request.form.get('user') #recebe "user" do formulário
    email = request.form.get('email') #recebe "email" do formulário
    senha = request.form.get('senha') #recebe "senha" do formulário
    perfil = request.form.get('perfil') #recebe "perfil" do formulário

    senha_criptografada = gerar_hash(senha) #gera o hash para a senha enviada no forms

    conexao = get_db() #abre conexão com o banco
    cursor = conexao.cursor() #abre o cursor

    cursor.execute("""
        INSERT INTO usuarios (user, email, senha, tipo)
        VALUES (%s, %s, %s, %s)
    """, (usuario, email, senha_criptografada, perfil)) #cursor vai inserir os dados recebidos no forms e a senha já criptografada no banco

    conexao.commit() #aceita a atualização no banco
    cursor.close() #fecha o cursor
    conexao.close() #fecha a conexão

    return redirect('/acesso') #redireciona para a página acesso

# RODAR
if __name__ == '__main__': #esse arquivo está sendo executado diretamente ou está sendo importado por outro arquivo | se está sendo executado diretamente ele executa (liga), se não ele não executa
    app.run(debug=True, host="0.0.0.0", port=5000) #liga o servidor
