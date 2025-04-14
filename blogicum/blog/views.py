from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Category, User, Comment
from .forms import PostCreateForm, CommentsForm, ProfileChangeForm


def post_filter():
    return Post.objects.filter(
        pub_date__lt=timezone.now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')


class BlogMixin:
    model = Post
    paginate_by = 10
    comment_count = None

    def get_queryset(self):
        return post_filter()


class BlogListView(BlogMixin, ListView):
    template_name = 'blog/index.html'


class ProfileListView(BlogMixin, ListView):
    template_name = 'blog/profile.html'

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs['slug'])
        if self.request.user == author:
            return Post.objects.filter(author=author).order_by('-pub_date')

        return Post.objects.filter(
            author=author,
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(
            User, username=self.kwargs['slug']
        )
        return context


class CategoryListView(BlogMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        return super().get_queryset().filter(
            category__title=get_object_or_404(
                Category.objects.filter(is_published=True),
                slug=self.kwargs['slug']
            ).title
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['slug']
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            args=[self.request.user.username]
        )

    def form_valid(self, form):
        fields = form.save(commit=False)
        fields.author = self.request.user
        fields.save()
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostCreateForm

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect(
                'blog:post_detail',
                pk=self.kwargs['pk']
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            args=[self.kwargs['pk']]
        )

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if (obj.author != self.request.user
                and (not obj.is_published
                     or not obj.category.is_published
                     or obj.pub_date > timezone.now())):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    current_post = None
    model = Comment
    form_class = CommentsForm

    def dispatch(self, request, *args, **kwargs):
        self.current_post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.current_post = self.current_post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.current_post.pk}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['text']
    context_object_name = 'comment'
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment, id=self.kwargs['slug'])

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != self.request.user:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.kwargs['pk']])


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    fields = ['text']
    context_object_name = 'comment'
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment, id=self.kwargs['slug'])

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.kwargs['pk']])


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.get_object())
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            args=[self.request.user.username]
        )


@login_required
def edit_profile(request):
    template_name = 'blog/user.html'
    form = ProfileChangeForm(request.POST or None, instance=request.user)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user.username)
    return render(request, template_name, context)
