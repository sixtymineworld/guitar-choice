from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .forms import CartQuantityForm, CatalogSearchForm, FeedbackForm, GuitarConfigForm, ReviewForm
from .models import Guitar, GuitarOrder, Review


def _session_key(request):
    """Return the visitor's session key, ensuring the session is saved in the store."""
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def _cart_items(request):
    return GuitarOrder.objects.filter(
        session_key=_session_key(request), status=GuitarOrder.Status.CART
    ).select_related("guitar")


def home(request):
    return render(request, "guitars/home.html", {"featured": Guitar.objects.filter(is_available=True)[:3]})


class GuitarListView(ListView):
    """Catalog of guitars with search, type filter, and pagination (B6.1, B6.3, B6.4)."""
    model = Guitar
    template_name = "guitars/catalog.html"
    context_object_name = "guitars"
    paginate_by = 6

    def get_queryset(self):
        qs = Guitar.objects.all()
        query = self.request.GET.get("q", "").strip()[:100]
        selected_types = self.request.GET.getlist("type")
        valid_types = [t for t in selected_types if t in Guitar.GuitarType.values]

        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(brand__icontains=query) | Q(material__icontains=query))
        if valid_types:
            qs = qs.filter(guitar_type__in=valid_types)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()[:100]
        selected_types = [t for t in self.request.GET.getlist("type") if t in Guitar.GuitarType.values]

        counts_qs = Guitar.objects.values("guitar_type").annotate(total=Count("id"))
        counts_dict = {item["guitar_type"]: item["total"] for item in counts_qs}

        types_with_meta = [
            (value, label, counts_dict.get(value, 0))
            for value, label in Guitar.GuitarType.choices
        ]
        context["query"] = query
        context["selected_types"] = selected_types
        context["types"] = types_with_meta
        return context


class GuitarDetailView(DetailView):
    """Detail view for a single guitar with order handling and similar models (B6.1, B6.4, B6.5)."""
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
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_available:
            messages.warning(request, f"Модель «{self.object.brand} {self.object.name}» наразі очікується на складі.")
            return redirect("guitars:guitar_detail", pk=self.object.pk)

        GuitarOrder.objects.create(
            session_key=_session_key(request),
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
        if form.is_valid():
            order = form.save(commit=False)
            order.session_key = _session_key(request)
            order.status = GuitarOrder.Status.CART
            order.save()
            messages.success(request, f"Кастомну конфігурацію «{order.get_instrument_type_display()} ({order.get_body_shape_display()})» додано до кошика.")
            return redirect("guitars:cart")
        else:
            messages.error(request, "Будь ласка, оберіть коректні параметри конфігурації.")

    return render(request, "guitars/configurator.html", {
        "form": form,
        # Дані для живого підрахунку ціни та динамічних списків на сторінці
        "price_data": {
            "base_craft": {str(k): float(v) for k, v in GuitarOrder.BASE_CRAFT_PRICES.items()},
            "config_options": GuitarOrder.CONFIG_OPTIONS,
            "type_surcharges": GuitarOrder.TYPE_SURCHARGES,
            "all_surcharges": GuitarOrder.ALL_SURCHARGES,
        },
    })


def cart(request):
    items = list(_cart_items(request))
    return render(request, "guitars/cart.html", {
        "items": items,
        "total": sum(item.total_price for item in items),
        "items_count": sum(item.quantity for item in items),
    })


@require_POST
def cart_update(request, pk):
    item = _cart_items(request).filter(pk=pk).first()
    if not item:
        messages.error(request, "Позицію не знайдено або термін дії сесії закінчився.")
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
def cart_remove(request, pk):
    item = _cart_items(request).filter(pk=pk).first()
    if not item:
        messages.warning(request, "Позицію вже видалено.")
        return redirect("guitars:cart")
    item.delete()
    messages.success(request, "Позицію видалено з кошика.")
    return redirect("guitars:cart")


@require_POST
def cart_checkout(request):
    with transaction.atomic():
        items = list(_cart_items(request).select_for_update())
        if not items:
            messages.warning(request, "Ваш кошик порожній.")
            return redirect("guitars:cart")

        # Перевірка чи всі обрані каталожні моделі досі доступні для замовлення
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


def dss_recommend(request):
    """Decision Support System (СППР) recommendation engine for guitars."""
    try:
        genre = (request.GET.get("genre") or "rock").strip().lower()
        shape = (request.GET.get("shape") or "any").strip().lower()
        budget = (request.GET.get("budget") or "any").strip().lower()

        genre_type_map = {
            "rock": Guitar.GuitarType.ELECTRIC,
            "metal": Guitar.GuitarType.ELECTRIC,
            "blues": Guitar.GuitarType.ELECTRIC,
            "acoustic": Guitar.GuitarType.ACOUSTIC,
            "indie": Guitar.GuitarType.ACOUSTIC,
            "classical": Guitar.GuitarType.CLASSICAL,
            "bass": Guitar.GuitarType.BASS,
        }

        valid_types = set(Guitar.GuitarType.values)
        target_type = None
        if shape in valid_types:
            target_type = shape
        elif genre in genre_type_map:
            target_type = genre_type_map[genre]

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

        genre_names = {
            "rock": "Рок / Альтернатива",
            "metal": "Метал / Важкий рок",
            "blues": "Блюз / Джаз / Фанк",
            "acoustic": "Акустичний поп / Інді",
            "indie": "Інді / Авторська пісня",
            "classical": "Класика / Фламенко",
            "bass": "Бас / Ритм-секція",
        }
        genre_str = genre_names.get(genre, genre.capitalize())
        why = (
            f"СППР проаналізував ваші критерії: напрямок «{genre_str}» та бюджетні орієнтири. "
            f"Модель {selected_guitar.brand} {selected_guitar.name} ({selected_guitar.get_guitar_type_display()}) "
            f"має найкращий баланс акустичних характеристик, матеріалу ({selected_guitar.material}) "
            f"та цінової категорії для вашого стилю гри."
        )

        return JsonResponse({
            "success": True,
            "guitar": {
                "id": selected_guitar.pk,
                "name": selected_guitar.name,
                "brand": selected_guitar.brand,
                "type_display": selected_guitar.get_guitar_type_display(),
                "price": float(selected_guitar.price),
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
def auth_login(request):
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"

    if not username or not password:
        err = "Будь ласка, введіть ім'я користувача та пароль."
        if is_ajax:
            return JsonResponse({"success": False, "error": err})
        messages.error(request, err)
        return redirect(next_url)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        if is_ajax:
            return JsonResponse({"success": True, "username": user.username})
        messages.success(request, f"Вітаємо, {user.username}! Ви успішно увійшли.")
        return redirect(next_url)
    else:
        err = "Невірний логін або пароль."
        if is_ajax:
            return JsonResponse({"success": False, "error": err})
        messages.error(request, err)
        return redirect(next_url)


@require_POST
def auth_register(request):
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip()
    password = request.POST.get("password", "")
    password_confirm = request.POST.get("password_confirm", "")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"

    if len(username) < 3:
        err = "Ім'я користувача має містити щонайменше 3 символи."
        if is_ajax:
            return JsonResponse({"success": False, "error": err})
        messages.error(request, err)
        return redirect(next_url)

    if User.objects.filter(username__iexact=username).exists():
        err = "Користувач із таким іменем вже зареєстрований."
        if is_ajax:
            return JsonResponse({"success": False, "error": err})
        messages.error(request, err)
        return redirect(next_url)

    if len(password) < 6:
        err = "Пароль має містити щонайменше 6 символів."
        if is_ajax:
            return JsonResponse({"success": False, "error": err})
        messages.error(request, err)
        return redirect(next_url)

    if password != password_confirm:
        err = "Паролі не збігаються."
        if is_ajax:
            return JsonResponse({"success": False, "error": err})
        messages.error(request, err)
        return redirect(next_url)

    user = User.objects.create_user(username=username, email=email, password=password)
    login(request, user)
    if is_ajax:
        return JsonResponse({"success": True, "username": user.username})
    messages.success(request, f"Акаунт «{user.username}» успішно створено! Ласкаво просимо.")
    return redirect(next_url)


@require_POST
def auth_logout(request):
    """Logout view, strictly restricted to POST (B7.1)."""
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Ви вийшли з облікового запису.")
    return redirect(next_url)


class UserRegisterView(CreateView):
    """User registration based on UserCreationForm (B7.1)."""
    form_class = UserCreationForm
    template_name = "guitars/register.html"
    success_url = reverse_lazy("guitars:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Вітаємо, {user.username}! Ваш акаунт успішно створено.")
        return redirect(self.success_url)


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Create a review for a guitar; assigns author in form_valid (B6.1, B7.2, B7.3)."""
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
    """Update a review; only allowed for the review owner or staff (B6.1, B7.3)."""
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
    """Delete a review; only allowed for the review owner or staff (B6.1, B7.3)."""
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
    """Privileged orders management view for staff users only (B7.4, B7.5)."""
    model = GuitarOrder
    template_name = "guitars/staff_orders.html"
    context_object_name = "orders"

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return GuitarOrder.objects.all().select_related("guitar").order_by("-created_at")


