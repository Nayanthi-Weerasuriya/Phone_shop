from django.shortcuts import render
from .models import Post
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404


# Create your views here.
def welcome(request):
    return render(request, 'blog/base.html')

def sit(request):
    return render(request, 'blog/sit.html')

def academic(request):
    return render(request, 'blog/academic.html')

def view_all(request):
    posts = Post.objects.all()
    return render(request, 'blog/viewall.html', {'posts': posts})


def create_post(request):
    if request.method == 'POST':
        title = request.POST['title']
        category = request.POST['category']
        content = request.POST['content']
        Post.objects.create(title=title, content=content, category = category)
        return redirect('viewall')
    return render(request, 'blog/create.html')

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('viewall')

def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.title = request.POST['title']
        post.category = request.POST['category']
        post.content = request.POST['content']
        post.save()
        return redirect('viewall')
    return render(request, 'blog/edit_post.html', {'post': post})

