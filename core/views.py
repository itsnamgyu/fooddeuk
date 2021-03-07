from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, OuterRef, Subquery
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView, FormView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from core.forms import VoteForm
from core.models import Photo, Vote


class LandingView(TemplateView):
    template_name = "core/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class IndexView(TemplateView):
    template_name = "core/index.html"


class PhotoListView(LoginRequiredMixin, TemplateView):
    template_name = "core/photo_list.html"

    def get_photo_list(self):
        photos = Photo.objects.all().annotate(bad=Count("vote", filter=Q(vote__selection=Vote.BAD)),
                                              okay=Count("vote", filter=Q(vote__selection=Vote.OKAY)),
                                              good=Count("vote", filter=Q(vote__selection=Vote.GOOD)))
        if self.request.GET.get("sort") == "rank":
            photos = photos.order_by("-average")
        votes = Vote.objects.filter(user=self.request.user).all()
        votes_by_photo = {vote.photo_id: vote for vote in votes}
        for photo in photos:
            photo.vote = votes_by_photo.get(photo.id)
        return photos

    def get_context_data(self, **kwargs):
        User = get_user_model()
        context = super().get_context_data(**kwargs)
        max_votes = Photo.objects.count() * User.objects.count()
        context["photo_list"] = self.get_photo_list()
        context["total_votes"] = Vote.objects.count()
        context["max_votes"] = max_votes
        context["progress"] = Vote.objects.count() / max_votes * 100
        context["users"] = User.objects.annotate(Count("vote")).order_by("-vote__count")
        context["sort_by_rank"] = self.request.GET.get("sort") == "rank"
        return context


class PhotoDetailView(LoginRequiredMixin, SingleObjectMixin, FormView):
    """
    self.object = Photo {
        next: next photo
        previous: previous photo
        vote: current user's vote on photo
    }
    """
    template_name = "core/photo_detail.html"
    model = Photo
    slug_url_kwarg = "slug"
    slug_field = "id"
    context_object_name = "photo"
    form_class = VoteForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_object(self, queryset=None):
        object = super().get_object(queryset)
        object.vote = object.vote_set.filter(user=self.request.user).first()
        return object

    def get_queryset(self):
        next_photo = Photo.objects.filter(id__gt=OuterRef("id")).order_by("id").values("id")[:1]
        previous_photo = Photo.objects.filter(id__lt=OuterRef("id")).order_by("-id").values("id")[:1]
        return Photo.objects.all().annotate().annotate(next=Subquery(next_photo)).annotate(
            previous=Subquery(previous_photo))

    def get_initial(self):
        initial = super().get_initial()
        initial["photo"] = self.object.id
        initial["user"] = self.request.user.id
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object.vote:
            kwargs.update({'instance': self.object.vote})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_id"] = self.object.next
        context["previous_id"] = self.object.previous
        return context

    def form_valid(self, form):
        form.save()
        self.object.update()
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.next:
            return reverse("core:photo-detail", args=[self.object.next])
        else:
            return reverse("core:photo-list")
