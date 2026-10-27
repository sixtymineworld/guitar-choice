from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Count, Max, Min, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .constants import DSS_GENRE_NAMES, DSS_GENRE_TYPE_MAP
from .forms import CartQuantityForm, FeedbackForm, GuitarConfigForm, ReviewForm
from .models import Favorite, Guitar, GuitarOrder, Review


def _cart_items(request):
    if not request.user.is_authenticated:
        return GuitarOrder.objects.none()
    return GuitarOrder.objects.filter(
        user=request.user, status=GuitarOrder.Status.CART
    ).select_related("guitar")


def home(request):
    featured = list(Guitar.objects.filter(is_available=True)[:6])
    return render(request, "guitars/home.html", {"featured": featured})


class GuitarListView(ListView):
    model = Guitar
    template_name = "guitars/catalog.html"
    context_object_name = "guitars"
    paginate_by = 6

    def get_queryset(self):
        qs = Guitar.objects.all()
        query = self.request.GET.get("q", "").strip()[:100]
        selected_types = self.request.GET.getlist("type")
        valid_types = [t for t in selected_types if t in Guitar.GuitarType.values]
        min_price = self.request.GET.get("min_price", "").strip()
        max_price = self.request.GET.get("max_price", "").strip()
        sort = self.request.GET.get("sort", "").strip()
        in_stock = self.request.GET.get("in_stock", "").strip()

        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(brand__icontains=query) | Q(material__icontains=query) | Q(color__icontains=query))
        if valid_types:
            qs = qs.filter(guitar_type__in=valid_types)
        if in_stock == "1":
            qs = qs.filter(is_available=True)
        if min_price:
            try:
                min_val = Decimal(min_price)
                if min_val >= 0:
                    qs = qs.filter(price__gte=min_val)
            except (InvalidOperation, ValueError, TypeError):
                pass
        if max_price:
            try:
                max_val = Decimal(max_price)
                if max_val >= 0:
                    qs = qs.filter(price__lte=max_val)
            except (InvalidOperation, ValueError, TypeError):
                pass

        if sort == "price_asc":
            qs = qs.order_by("price", "id")
        elif sort == "price_desc":
            qs = qs.order_by("-price", "id")
        else:
            qs = qs.order_by("brand", "name")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()[:100]
        selected_types = [t for t in self.request.GET.getlist("type") if t in Guitar.GuitarType.values]
        min_price = self.request.GET.get("min_price", "").strip()
        max_price = self.request.GET.get("max_price", "").strip()
        sort = self.request.GET.get("sort", "").strip()
        in_stock = self.request.GET.get("in_stock", "").strip()

        counts_qs = Guitar.objects.values("guitar_type").annotate(total=Count("id"))
        counts_dict = {item["guitar_type"]: item["total"] for item in counts_qs}

        types_with_meta = [
            (value, label, counts_dict.get(value, 0))
            for value, label in Guitar.GuitarType.choices
        ]

        price_bounds = Guitar.objects.aggregate(
            min_p=Min("price"),
            max_p=Max("price")
        )
        catalog_min_price = int(price_bounds["min_p"] or 0)
        catalog_max_price = int(price_bounds["max_p"] or 150000)

        context["query"] = query
        context["selected_types"] = selected_types
        context["types"] = types_with_meta
        context["catalog_min_price"] = catalog_min_price
        context["catalog_max_price"] = catalog_max_price
        context["selected_min_price"] = min_price
        context["selected_max_price"] = max_price
        context["current_sort"] = sort
        context["in_stock"] = in_stock
        return context


class GuitarDetailView(DetailView):
    model = Guitar
    template_name = "guitars/detail.html"
    context_object_name = "guitar"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guitar = self.object
        similar = list(Guitar.objects.filter(guitar_type=guitar.guitar_type).exclude(pk=guitar.pk)[:3])
        if len(similar) < 3:
            needed = 3 - len(similar)
            excluded_ids = [guitar.pk] + [g.pk for g in similar]
            similar.extend(list(Guitar.objects.exclude(pk__in=excluded_ids)[:needed]))
        context["similar_guitars"] = similar
        if self.request.user.is_authenticated:
            context["is_favorite"] = Favorite.objects.filter(
                user=self.request.user, guitar=guitar
            ).exists()
        else:
            context["is_favorite"] = False
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            messages.info(request, "Будь ласка, увійдіть або зареєструйтесь, щоб додати інструмент до кошика.")
            return redirect(f"{reverse_lazy('guitars:login')}?next={self.object.get_absolute_url()}")

        if not self.object.is_available:
            messages.warning(request, f"Модель «{self.object.brand} {self.object.name}» наразі очікується на складі.")
            return redirect("guitars:guitar_detail", pk=self.object.pk)

        GuitarOrder.objects.create(
            user=request.user,
            guitar=self.object,
            status=GuitarOrder.Status.CART,
            quantity=1,
        )
        messages.success(request, f"«{self.object.brand} {self.object.name}» додано до вашого кошика!")
        return redirect("guitars:cart")


def about(request):
    return render(request, "guitars/about.html")


def feedback(request):
    form = FeedbackForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Дякуємо! Ми отримали ваше звернення й відповімо найближчим часом.")
            return redirect("guitars:feedback")
        else:
            messages.error(request, "Будь ласка, перевірте коректність заповнення полів.")
    return render(request, "guitars/feedback.html", {"form": form})


def configurator(request):
    form = GuitarConfigForm(request.POST or None)
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.info(request, "Будь ласка, увійдіть або зареєструйтесь, щоб додати кастомну гітару до кошика.")
            return redirect(f"{reverse_lazy('guitars:login')}?next={reverse_lazy('guitars:configurator')}")

        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.status = GuitarOrder.Status.CART
            order.save()
            messages.success(request, f"Кастомну конфігурацію «{order.get_instrument_type_display()} ({order.get_body_shape_display()})» додано до кошика.")
            return redirect("guitars:cart")
        else:
            messages.error(request, "Будь ласка, оберіть коректні параметри конфігурації.")

    return render(request, "guitars/configurator.html", {
        "form": form,
        "price_data": {
            "base_craft": {str(k): float(v) for k, v in GuitarOrder.BASE_CRAFT_PRICES.items()},
            "config_options": GuitarOrder.CONFIG_OPTIONS,
            "type_surcharges": GuitarOrder.TYPE_SURCHARGES,
            "all_surcharges": GuitarOrder.ALL_SURCHARGES,
        },
    })


@login_required
def cart(request):
    items = list(_cart_items(request))
    return render(request, "guitars/cart.html", {
        "items": items,
        "total": sum(item.total_price for item in items),
        "items_count": sum(item.quantity for item in items),
    })


@require_POST
@login_required
def cart_update(request, pk):
    item = _cart_items(request).filter(pk=pk).first()
    if not item:
        messages.error(request, "Позицію не знайдено.")
        return redirect("guitars:cart")
    form = CartQuantityForm(request.POST)
    if form.is_valid():
        item.quantity = form.cleaned_data["quantity"]
        item.save()
        messages.success(request, "Кількість оновлено.")
    else:
        messages.error(request, "Вкажіть коректну кількість (від 1 до 20).")
    return redirect("guitars:cart")


@require_POST
@login_required
def cart_remove(request, pk):
    item = _cart_items(request).filter(pk=pk).first()
    if not item:
        messages.warning(request, "Позицію вже видалено.")
        return redirect("guitars:cart")
    item.delete()
    messages.success(request, "Позицію видалено з кошика.")
    return redirect("guitars:cart")


@require_POST
@login_required
def cart_checkout(request):
    with transaction.atomic():
        items = list(_cart_items(request).select_for_update())
        if not items:
            messages.warning(request, "Ваш кошик порожній.")
            return redirect("guitars:cart")

        unavailable = [item.guitar.name for item in items if item.guitar and not item.guitar.is_available]
        if unavailable:
            messages.error(
                request,
                f"На жаль, наступні моделі тимчасово недоступні: {', '.join(unavailable)}. Будь ласка, видаліть їх перед оформленням."
            )
            return redirect("guitars:cart")

        item_ids = [item.pk for item in items]
        GuitarOrder.objects.filter(pk__in=item_ids).update(status=GuitarOrder.Status.PLACED)
        messages.success(request, f"Замовлення успішно оформлено ({len(items)} поз.)! Ми зв’яжемося з вами для підтвердження.")
        return redirect("guitars:cart")


def favorites_list(request):
    if not request.user.is_authenticated:
        return render(request, "guitars/favorites.html", {
            "guitars": [],
            "favorites_count": 0,
            "is_anonymous": True,
        })

    favorites = Favorite.objects.filter(user=request.user).select_related("guitar")
    guitars = [fav.guitar for fav in favorites]
    return render(request, "guitars/favorites.html", {
        "guitars": guitars,
        "favorites_count": len(guitars),
        "is_anonymous": False,
    })


def favorite_toggle(request, pk):
    guitar = get_object_or_404(Guitar, pk=pk)
    if not request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("format") == "json":
            return JsonResponse({
                "status": "unauthorized",
                "login_url": f"{reverse_lazy('guitars:login')}?next={guitar.get_absolute_url()}",
                "message": "Увійдіть в акаунт, щоб додавати гітари до обраного.",
            }, status=401)
        messages.info(request, "Будь ласка, увійдіть, щоб додавати інструменти до вподобаних.")
        return redirect(f"{reverse_lazy('guitars:login')}?next={guitar.get_absolute_url()}")

    fav, created = Favorite.objects.get_or_create(user=request.user, guitar=guitar)
    if not created:
        fav.delete()
        is_favorite = False
        action_msg = f"Модель «{guitar.brand} {guitar.name}» видалено з вподобаних."
    else:
        is_favorite = True
        action_msg = f"Модель «{guitar.brand} {guitar.name}» додано до вподобаних!"

    count = Favorite.objects.filter(user=request.user).count()

    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("format") == "json" or request.POST.get("format") == "json":
        return JsonResponse({
            "status": "ok",
            "is_favorite": is_favorite,
            "favorites_count": count,
            "guitar_id": guitar.pk,
            "message": action_msg,
        })

    messages.success(request, action_msg)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or guitar.get_absolute_url()
    return redirect(next_url)


def dss_recommend(request):
    try:
        genre = (request.GET.get("genre") or "rock").strip().lower()
        shape = (request.GET.get("shape") or "any").strip().lower()
        budget = (request.GET.get("budget") or "any").strip().lower()

        valid_types = set(Guitar.GuitarType.values)
        target_type = None
        if shape in valid_types:
            target_type = shape
        elif genre in DSS_GENRE_TYPE_MAP:
            target_type = DSS_GENRE_TYPE_MAP[genre]

        guitars = Guitar.objects.filter(is_available=True)
        if not guitars.exists():
            guitars = Guitar.objects.all()

        if not guitars.exists():
            return JsonResponse({"success": False, "message": "Наразі в каталозі немає доступних гітар."})

        matched_type_guitars = guitars.filter(guitar_type=target_type) if target_type else guitars
        candidates = matched_type_guitars if matched_type_guitars.exists() else guitars

        if budget == "low":
            budget_cand = candidates.filter(price__lte=15000).order_by("-price")
            selected_guitar = budget_cand.first() or candidates.order_by("price").first()
        elif budget == "mid":
            budget_cand = candidates.filter(price__gt=15000, price__lte=30000).order_by("price")
            selected_guitar = budget_cand.first() or candidates.order_by("price").first()
        elif budget == "high":
            budget_cand = candidates.filter(price__gt=30000).order_by("price")
            selected_guitar = budget_cand.first() or candidates.order_by("-price").first()
        else:
            selected_guitar = candidates.first()

        if not selected_guitar:
            return JsonResponse({"success": False, "message": "Моделей не знайдено за вказаними критеріями."})

        genre_str = DSS_GENRE_NAMES.get(genre, genre.capitalize())
        why = f"Найкращий вибір під стиль «{genre_str}» у вашому бюджеті."

        return JsonResponse({
            "success": True,
            "guitar": {
                "id": selected_guitar.pk,
                "name": selected_guitar.name,
                "brand": selected_guitar.brand,
                "type_display": selected_guitar.get_guitar_type_display(),
                "price": float(selected_guitar.price),
                "color": selected_guitar.color,
                "material": selected_guitar.material,
                "description": selected_guitar.description,
                "image_url": selected_guitar.image_url,
                "detail_url": selected_guitar.get_absolute_url(),
                "config_url": "/configurator/",
            },
            "reason": why,
        })
    except Exception:
        return JsonResponse({"success": False, "message": "Сталася внутрішня помилка при підборі гітари."}, status=500)


@require_POST
def auth_logout(request):
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Ви вийшли з облікового запису.")
    return redirect(next_url)


class UserRegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "guitars/register.html"
    success_url = reverse_lazy("guitars:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(self.request, f"Вітаємо, {user.username}! Ваш акаунт успішно створено.")
        return redirect(self.success_url)


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "guitars/review_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.guitar = get_object_or_404(Guitar, pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["guitar"] = self.guitar
        return context

    def form_valid(self, form):
        form.instance.guitar = self.guitar
        form.instance.user = self.request.user
        messages.success(self.request, "Дякуємо! Ваш відгук успішно опубліковано.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.guitar.get_absolute_url()


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "guitars/review_form.html"

    def test_func(self):
        review = self.get_object()
        return review.user == self.request.user or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["guitar"] = self.object.guitar
        return context

    def form_valid(self, form):
        messages.success(self.request, "Відгук успішно оновлено.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.guitar.get_absolute_url()


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = "guitars/review_confirm_delete.html"

    def test_func(self):
        review = self.get_object()
        return review.user == self.request.user or self.request.user.is_staff

    def form_valid(self, form):
        messages.info(self.request, "Відгук успішно видалено.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.guitar.get_absolute_url()


class StaffOrdersListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = GuitarOrder
    template_name = "guitars/staff_orders.html"
    context_object_name = "orders"

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return GuitarOrder.objects.all().select_related("guitar").order_by("-created_at")