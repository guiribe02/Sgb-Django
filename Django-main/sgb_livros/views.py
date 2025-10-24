from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Livro
from .models import Autor
from django.contrib.auth.decorators import login_required
# Create your views here.


def livros(request):
    return render(request, 'livros.html')


def salvar_livro(request):
    if request.method == 'POST':
        titulo_livro = request.POST['titulo_livro']
        autor_livro = request.POST['autor_livro']
        editora = request.POST['editora']
        return render(request, 'livros.html', context={
            'titulo_livro': titulo_livro,
            'autor_livro': autor_livro,
            'editora': editora
        })
    return HttpResponse('Método não permitido', status=405)


def index(request):
    return render(request, 'index.html')

@login_required
def cadastro_livro(request):
    if request.method == 'POST':
        livro_id = request.POST['livro_id']
        titulo = request.POST['titulo']
        autor = request.POST['autor']
        ano_publicacao = request.POST['ano_publicacao']
        editora = request.POST['editora']
        if livro_id:  # Se o ID do livro for fornecido, atualize o livro existente. Ele edita
            livro = livro_id
            livro.titulo = titulo
            autor, created = Autor.objects.get_or_create(nome=autor)
            livro.autor = autor
            livro.ano_publicacao = ano_publicacao
            livro.editora = editora
            livro.save()
        else:  # Caso contrário, crie um novo livro. Ele cria
            Livro.objects.create(
                titulo = titulo,
                autor = autor,
                ano_publicacao = ano_publicacao,
                editora = editora
            )
        return redirect('cadastro_livro')
    # objects é um gerenciador de modelos padrão do Django que permite interagir/consultar com o banco de dados
    # all é uma função que recupera todos os registros da tabela livro - é o select do BD
    livros = Livro.objects.all()  # Recupera todos os livros do banco de dados
    autores = Autor.objects.all()
    return render(request, 'livros.html', {'livros': livros, 'autores': autores})

@login_required
def exclui_livro(request, livro_id):
    #get_objects_or_404 tenta recuperar o objeto com o ID fornecido buscando no banco de dados e, 
    # se não encontrar, retorna um erro 404. Se encontrar o objeto, ele o retorna para 
    # que possa ser usado na função.
    livro = get_object_or_404(Livro, id=livro_id)
    livro.delete()
    return redirect('cadastro_livro')

@login_required
def edita_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    livros = Livro.objects.all()  # Recupera todos os livros do banco de dados
    autores = Autor.objects.all()
    
    if request.method == 'POST':
        livro.titulo = request.POST['titulo']
        autor = request.POST['autor']
        autor, created = Autor.objects.get_or_create(nome=autor)
        livro.autor = request.POST['autor']
        livro.ano_publicacao = request.POST['ano_publicacao']
        livro.editora = request.POST['editora']
        livro.save()
        return redirect('cadastro_livro')
    return render(request, 'livros.html', {'livros': livros, 'livro_editar': livro, 'autores': autores})