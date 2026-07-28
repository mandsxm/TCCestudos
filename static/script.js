// MUDAR PARA TABELA
const botao = document.getElementById("btn-entrar"); //declara a variável botao (const = não pode mudar o valor depois de criada) | document = representa a página HTML que está carregada na tela | getElementById("btn-entrar") = vai buscar o elemento cujo o id no html é btn-entrar, trazendo uma referência a ele para que o JS possa manipular

botao?.addEventListener("click", () => { //?. = optional chaining, checa se o botao (btn-entrar) existe ou se é null | .addEventListener("click", () => { ... }) = escuta um evento, no caso "click", quando o botão for clicado algo vai acontecer | () => { ... } = forma de escrever uma função, sem nome, que só pode ser utilizada neste momento, não pode ser utilizada mais tarde
    window.location.href = "/tabela"; //equivalente ao redirect do PY | o window.location.href que ERA a página de login, vira a página /tabela | window.location = indica o endereço atual (url) que está sendo exibido no navegador | href = guarda essa url como texto 
}); //ao clicar no botão, o usuário vai para /tabela

// SALVAR + CARREGAR RASCUNHO
function salvarRascunho() { //function = função com nome, ou seja, pode ser chamada mais tarde | abre a função salvarRascunho
    const nome = document.getElementById("nome")?.value; //busca o elemento HTML com id="nome" e guarda o valor dentro da constante "nome" | value = guarda o que foi digitado naquele campo
    const qtde = document.getElementById("qtde")?.value;
    const responsavel = document.getElementById("responsavel")?.value;
    const preco = document.getElementById("preco")?.value;
    const estoque_min = document.getElementById("estoque_min")?.value;
    const descricao = document.getElementById("descricao")?.value;
    const categoria = document.getElementById("categoria")?.value;

    const dados = { //define a constante dados
        nome, //shorthand, atalho do JS para nome:nome | semelhante a dicionário no PY (chave:valor) mas aqui a chave e o valor são o mesmo | pq? nós definimos ali em cima que as constantes são = ao valor que bate com o Id no HTML (value), então, ficaria (nome:Chave Fenda)
        qtde, //quantidade:quantidade
        responsavel, //responsável:reponsável
        preco,
        estoque_min,
        descricao,
        categoria,
        tipoMovimentacao: window.tipoMovimentacao || "" //use o valor window.tipoMovimentacao se ela existir, ou(||) use uma string vazia("") | garante que tipoMovimentacao sempre tenha algum valor de texto, mesmo que window.tipoMovimentacao ainda não tenha sido definida.
    };

    localStorage.setItem("rascunho_editar", JSON.stringify(dados)); //localStorage = guarda dados no computador do próprio usuário | .setItem("rascunho_editar" = guarda algo dentro do pc do usuário(SETitem), mas só consegue guardar texto puro (string)
    //por isso usamos o JSON.stringify(dados), "dados" é um objeto que criamos e não uma string, então ele precisa ser convertido em uma string para que o .setItem funcione (transforma o objeto JavaScript em uma string de texto no formato JSON)
}

// EXCLUIR USUÁRIO 
window.excluirUsuario = async function (id) { //window.excluirUsuario = define a função excluirUsuario e faz com que ela seja acessível de qualquer lugar, incluindo de uma página de HTML | async function (id) = função assíncrona, faz uma requisição ao Flask, oq pode demorar, então ela serve para não travar o resto da página enquanto estiver carregando

    const confirmacao = confirm("Tem certeza que deseja excluir este usuário?"); //aparece uma mensagem pop-up de confirmação | o "confirm" faz aparecer o pop-up com os botões "Ok", true, ou "Cancelar", false, e guarda o valor booleano na constante confirmacao
    if (!confirmacao) return; // "!" = not (no PY) | "if not confirmacao return" | se não houve confirmação, para a função imediatamente, usuário não será excluído

    const resposta = await fetch(`/excluirUsuario/${id}`, { //fetch() = faz uma requisição HTTP (nesse caso o delete) | `/excluirUsuario/${id}` = equivalente a f-string, permite inserir uma variável dentro do texto usando ${}
        //fetch: essa URL gerada (/excluirUsuario/id) bate exatamente com a rota Flask @app.route('/excluirUsuario/<int:id>', methods=['DELETE'])
        //await (o outro lado de async) = diz "pause a execução dessa função aqui, espere essa operação terminar, e só então continue pra próxima linha"
        //precisa do await pq senão o js continuaria rodando o código sem saber se a exclusão tinha sido feita
        method: "DELETE" // essa requisição usa o método delete
    });

    const data = await resposta.json(); //interpreta o corpo da resposta como JSON, convertendo de volta pra um objeto JS utilizável (também demora, por isso o await / await espera a conversão terminar) = recebe em JSON e converte para um objeto JS

    if (data.success) { //se data for um sucesso
        alert("Usuário excluído com sucesso!"); //manda mensagem de sucesso
        location.reload(); //recarrega a página e atualiza removendo o usuário que seria excluído
    } else { //se não
        alert("Erro ao excluir usuário"); //manda mensagem de erro
    }
};

// EXCLUIR ITEM
window.excluirItem = async function (id) { //cria a função excluirItem (disponível globalmente por causa do window. = janela do navegador inteira | significa que ela fica acessível de qualquer lugar, não só no script.js, mas também de dentro do HTML, em atributos como onclick.), que recebe o id do item a ser excluído | async pq ela vai precisar "esperar" uma resposta do servidor

    const confirmacao = confirm("Tem certeza que deseja excluir este item?"); //mostra o pop-up de confirmação
    if (!confirmacao) return; //se não houve confirmação, para aí e não exclui nada

    const resposta = await fetch(`/excluir/${id}`, { //manda uma requisição DELETE pro Flask, pra rota /excluir/<id> (que apaga item do estoque) | await = o JS vai esperar a resposta do servidor antes de seguir em frente
        method: "DELETE" //essa requisição usa o método delete
    });

    const data = await resposta.json(); //pega a resposta do Flask que chega em formato JSON (tipo {"success": true}) e converte pra um objeto JS que pode ser utilizado aqui

    if (data.success) { //se data for um sucesso
        alert("Item excluído com sucesso!"); //manda mensagem de sucesso
        location.reload(); //recarrega a página e atualiza removendo o item que seria excluído
    } else { //se não
        alert("Erro ao excluir"); //manda mensagem de erro
    }
};

// JS PRINCIPAL
window.addEventListener("DOMContentLoaded", () => { //ouve o evento "DOMContentLoaded" que garante que tudo comece a rodar depois que toda a página HTML carregue
    //DOM = Document Object Model | É uma interface de programação que transforma toda a página HTML em uma estrutura de árvore, permitindo que linguagens como o JavaScript modifiquem o conteúdo, os estilos e a estrutura do site.

    const btnEntrada = document.getElementById("btnEntrada"); //busca no HTML o elemento com o id btnEntrada e guarda na constante
    const btnSaida = document.getElementById("btnSaida"); //busca no HTML o elemento com o id btnSaida e guarda na constante
    const btnRegistrar = document.getElementById("btnRegistrar"); //busca no HTML o elemento com o id btnRegistrar e guarda na constante
    const btnUpload = document.getElementById("btnUpload"); //busca no HTML o elemento com o id btnUpload e guarda na constante
    const fileInput = document.getElementById("fileInput"); //busca no HTML o elemento com o id fileInput e guarda na constante

    window.tipoMovimentacao = ""; //guarda uma informação que várias partes diferentes do código vão precisar consultar e alterar - que tipo de movimentação ta selecionada? entrada ou saída
    //começa vazia (""), pq como a tela acabou de carregar, nenhuma movimentação foi selecionada

    function limparSelecao() { //função limparSelecao - quando a pessoa clica em entrada ou saída, o botão selecionado é destacado, se a pessoa clica em entrada depois clica em saída, o destaque de entrada precisa sair, e só o destaque de saída que está selecionado fica
        btnEntrada?.classList.remove("btn-selecionado"); //.classList = a lista de classes (class) CSS do elemento | .remove("btn-selecionado") = tira essa classe específica da lista, se ela estiver lá
        btnSaida?.classList.remove("btn-selecionado"); //.classList = a lista de classes (class) CSS do elemento | .remove("btn-selecionado") = tira essa classe específica da lista, se ela estiver lá
    }

    // CARREGAR RASCUNHO
    const rascunho = JSON.parse(localStorage.getItem("rascunho_editar")); //busca o que foi guardado no localStorage, GETitem, e o resultado chega em uma string de texto (LocalStorage = que guarda dados no pc do usuário)
    //JSON.parse vai pegar a string encontrada que está em formato JSON e vai converter para um objeto JS que o código consegue usar
    //resumo: busca o rascunho salvo (como texto) e já converte ele de volta pra um objeto utilizável, guardando tudo isso na constante rascunho.

    if (rascunho && document.getElementById("nome")) { //se existir um rascunho and(&&) existir um elemento com o id="nome" | garante que o código só tente preencher esse campos se eles existirem na página atual

        document.getElementById("nome").value = rascunho.nome || ""; //pega o elemento HTML com o id "nome" e atribui um novo valor a propriedade .value, ou seja, preenche o campo do formulário com o conteúdo salvo
        document.getElementById("qtde").value = rascunho.qtde || "";
        document.getElementById("responsavel").value = rascunho.responsavel || "";
        document.getElementById("preco").value = rascunho.preco || "";
        document.getElementById("estoque_min").value = rascunho.estoque_min || "";
        document.getElementById("descricao").value = rascunho.descricao || "";
        document.getElementById("categoria").value = rascunho.categoria || "";

        window.tipoMovimentacao = rascunho.tipoMovimentacao || ""; //pega de dentro do objeto 'rascunho', o valor guardado na chave 'tipoMovimentacao' (qual movimentacao a pessoa escolheu nesse momento do rascunho), se não tinha nada salvo, deixa como uma string vazia
        //e guarda esse resultado na variável global (window) tipoMovimentacao, para o resto do código saber qual opção estava selecionada antes da pessoa sair da página
    }

    limparSelecao(); //chama a função limparSelecao que foi criada antes | function limparSelecao() { ... } = define a função e explica o que ela faz mas sem executar nada ainda, agora ela foi chamada pela primeira vez

    if (window.tipoMovimentacao === "entrada") { //se o tipo de movimentação que foi salvo for uma entrada | === compara não só o valor, mas também o tipo do dado
        document.getElementById("btnEntrada")?.classList.add("btn-selecionado"); //busca o btnEntrada e adiciona a classe de "botão selecionado" de estilização (CSS) | aparece ele como se estivesse selecionado
    }

    if (window.tipoMovimentacao === "saida") { //se o tipo de movimentação que foi salvo for uma saída | === compara não só o valor, mas também o tipo do dado
        document.getElementById("btnSaida")?.classList.add("btn-selecionado"); //busca o btnSaida e adiciona a classe de "botão selecionado" de estilização (CSS) | aparece ele como se estivesse selecionado
    }

    document.addEventListener("input", salvarRascunho); //quem está escutando o envento é document (a página toda, não só um elemento, como um botão) | adicione o evento input(escrever = o navegador dispara enquanto a pessoa digita cada caractere) | o document escuta o que está sendo digitado | guarda a função salvarRascunho para ser usada depois
    //resumo: toda vez que a pessoa digitar qualquer coisa em qualquer campo do formulário, salvarRascunho() é chamada automaticamente, salvando o progresso no localStorage

    btnEntrada?.addEventListener("click", () => { //no botão entrada (?. = confere se o botão existe ali, se não existe, nada acontece), adicione o evento click | escuta o click no botão
        window.tipoMovimentacao = "entrada"; //atualiza a movimentação | agora a movimentação selecionada é entrada
        limparSelecao(); //chama a função limparSelecao | remove o destaque visual dos dois botões
        btnEntrada.classList.add("btn-selecionado"); //adiciona a class de botão selecionado no btnEntrada
        salvarRascunho(); //chama a função salvarRascunho | salva isso
    });

    btnSaida?.addEventListener("click", () => { //no botão saida (?. = confere se o botão existe ali, se não existe, nada acontece), adicione o evento click | escuta o click no botão
        window.tipoMovimentacao = "saida"; //atualiza a movimentação | agora a movimentação selecionada é saida
        limparSelecao(); //chama a função limparSelecao | remove o destaque visual dos dois botões
        btnSaida.classList.add("btn-selecionado"); //adiciona a class de botão selecionado no btnSaida
        salvarRascunho(); //chama a função salvarRascunho | salva isso
    });

    btnRegistrar?.addEventListener("click", async () => { //no botão Registrar, adicione o evento click | async = permite usar await (pausa a execução esperando algo terminar, tipo uma requisição pro Flask)

        if (!window.tipoMovimentacao) { //se NÂO foi selecionado uma movimentação | ! = not
            alert("Selecione Entrada ou Saída."); //manda uma mensagem pedindo pra selecionar uma movimentação
            return; //a função para aqui | o registro não foi enviado pq a movimentação não foi selecionada
        }

        const nome = document.getElementById("nome").value; //busca cada campo pelo id e pega o que está digitado nele (.value), guardando em constantes.
        const qtde = document.getElementById("qtde").value;
        const responsavel = document.getElementById("responsavel").value;
        const preco = document.getElementById("preco").value;
        const estoque_min = document.getElementById("estoque_min").value;
        const descricao = document.getElementById("descricao").value;
        const categoria = document.getElementById("categoria").value;
        const imagem = fileInput?.files?.[0]; //no arquivo enviado (?. = protege caso a página não tivesse campo pra enviar arquivo), no .files que é uma lista (com apenas um arquivo que foi enviado), (?. = checa se a lista não é nula - vazia) pega o primeiro item na lista ([0] = primeira posição na lista)

        const formData = new FormData(); //new = cria uma instância nova pra algo | cria um exemplar novo e vazio de FormData | FormData empacota tanto strings quanto arquivos, no formato que o Flask espera receber

        formData.append("nome", nome); //append = adiciona um campo dentro do FormData | "nome", = nome do campo | nome = valor do campo
        formData.append("qtde", qtde);
        formData.append("responsavel", responsavel);
        formData.append("preco", preco);
        formData.append("estoque_min", estoque_min);
        formData.append("descricao", descricao);
        formData.append("categoria", categoria);
        formData.append("tipo", window.tipoMovimentacao); //adiciona o tipo de movimentação
        //o Flask vai receber esse valores e saber identificar eles

        if (imagem && imagem.size > 0) { //se a imagem e o tamanho da imagem forem maior que 0 | checa se o arquivo enviado tem um conteúdo| o primeiro 'imagem' checa se algum arquivo foi enviado | o imagem.size é o tamanho do arquivo em bytes
            formData.append("imagem", imagem); //vai adicionar a imagem no FormData | significa que a imagem existe
        }

        fetch("/entrada", { //fetch = faz uma requisição HTTP | /entrada = URL de destino | envia os dados do formulário (texto + imagem) pro Flask, na rota /entrada
            method: "POST", //diz que o método usado é POST
            body: formData //body = corpo da requisição - os dados que estão sendo enviados junto com a requisição, no caso o FormData
        })
        .then(res => res.json()) //.then = quando a requisição terminar, realize... | res = resposta | return resposta.json() | quando a resposta chega, pega ela (res), converte o corpo da resposta de JSON pra objeto JS
        .then(data => { //quando a conversão pra json terminar, recebe o objeto convertido e nomeia de data

            const msg = document.getElementById("mensagem"); //busca no HTML um elemento com id "mensagem"

            if (data.success) { //checa a propriedade success do objeto data que veio da resposta do Flask
                localStorage.removeItem("rascunho_editar"); //remove o que está guardado - se o registro já foi salvo no banco, o rascunho dele não precisa mais existir
                msg.innerText = "Registro salvo com sucesso ✔"; //o elemento id="mensagem", mostra uma mensagem visível no HTML 
                msg.style.color = "green"; //cor da mensagem que aparece no HTML - altera um elemento no CSS já no JS

                setTimeout(() => { //executa uma função depois de um tempo determinado ter passado, em vez de executar imediatamente
                    window.location.href = "/tabela"; //a função manda o navegador pra "/tabela"
                }, 1000); //1000 milissegundos - 1 segundo  | espera esse tempo para a pessoa ver a mensagem antes de ser redirecionada para /tabela

            } else { //se a propriedade data.success for falso (Flask indicou que deu erro)
                msg.innerText = data.erro || "Erro ao salvar"; //manda a mensagem de erro
                msg.style.color = "red"; //manda a mensagem em vermelho
            }
        })
        .catch(() => { //quando algo dá errado em qualquer um dos passos anteriores (o fetch, ou qualquer um dos .then) | ex: erro de conexão ou rede
            const msg = document.getElementById("mensagem"); //busca o elemento de mensagem 
            msg.innerText = "Erro ao conectar com o servidor."; //manda mensagem de erro
            msg.style.color = "red"; //cor da mensagem vermelho
        });
    });

    btnUpload?.addEventListener("click", () => { //adiciona evento de click no btnUpload | ?. = protege caso o botão não exista
        fileInput?.click(); //.click() = simula um click, como se o JS tivesse clicado no fileInput (o <input type="file"> escondido)
    });

    fileInput?.addEventListener("change", () => { //change = quando o valor de um elemento muda de forma "completa" | quando a pessoa termina de escolher o arquivo na janela do sistema operacional
        const msg = document.getElementById("mensagem"); //busca o elemento com id "mensagem"

        if (fileInput.files.length > 0) { //se a quantidade de arquivos na lista .files for maior que 0 - se a pessoa realmente selecionou um arquivo
            msg.innerText = "Imagem adicionada com sucesso ✔"; //manda mensagem de imagem adicionada
            msg.style.color = "green"; //cor da mensagem verde
        }
    });
})
