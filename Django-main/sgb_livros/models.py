from django.db import models

class Autor(models.Model):
    nome = models.CharField(max_length=150)
    data_nascimento = models.DateField(blank=True, null=True)
    nacionalidade = models.CharField(max_length=50, blank=True, null=True)


class Livro(models.Model): #models.model indica que a classe Livro é um modelo do Django é padrão
    titulo = models.CharField(max_length=200) #CharField é um campo de texto com tamanho máximo definido
    autor = models.ForeignKey(Autor, related_name='livros', on_delete=models.CASCADE, null=True, blank=True) #ForeignKey cria uma relação muitos-para-um com o modelo Autor
    ano_publicacao = models.PositiveIntegerField()
    editora = models.CharField(max_length=100, blank=True, null=True) #blank e null permitem que o campo seja opcional
    def __str__(self):
        return self.titulo

