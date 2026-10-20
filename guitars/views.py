from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from .forms import CartQuantityForm, FeedbackForm, GuitarConfigForm
from .models import Guitar, GuitarOrder


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


def catalog(request):
    guitars = Guitar.objects.all()
    query = request.GET.get("q", "").strip()[:100]
    selected_type = request.GET.get("type", "").strip()

    if query:
        guitars = guitars.filter(Q(name__icontains=query) | Q(brand__icontains=query) | Q(material__icontains=query))
    if selected_type and selected_type in Guitar.GuitarType.values:
        guitars = guitars.filter(guitar_type=selected_type)

    return render(request, "guitars/catalog.html", {
        "guitars": guitars,
        "query": query,
        "selected_type": selected_type,
        "types": Guitar.GuitarType.choices,
    })


def guitar_detail(request, pk):
    guitar = Guitar.objects.filter(pk=pk).first()
    if not guitar:
        messages.error(request, "Запитувану модель гітари не знайдено.")
        return redirect("catalog")

    if request.method == "POST":
        if not guitar.is_available:
            messages.warning(request, f"Модель «{guitar.brand} {guitar.name}» наразі очікується на складі.")
            return redirect("guitar_detail", pk=guitar.pk)

        GuitarOrder.objects.create(
            session_key=_session_key(request),
            guitar=guitar,
            status=GuitarOrder.Status.CART,
            quantity=1,
        )
        messages.success(request, f"«{guitar.brand} {guitar.name}» додано до вашого кошика!")
        return redirect("cart")

    similar = list(Guitar.objects.filter(guitar_type=guitar.guitar_type).exclude(pk=guitar.pk)[:3])
    if len(similar) < 3:
        needed = 3 - len(similar)
        excluded_ids = [guitar.pk] + [g.pk for g in similar]
        similar.extend(list(Guitar.objects.exclude(pk__in=excluded_ids)[:needed]))

    return render(
        request,
        "guitars/detail.html",
        {
            "guitar": guitar,
            "similar_guitars": similar,
        },
    )


def about(request):
    return render(request, "guitars/about.html")


def feedback(request):
    form = FeedbackForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Дякуємо! Ми отримали ваше звернення й відповімо найближчим часом.")
            return redirect("feedback")
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
            return redirect("cart")
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
        return redirect("cart")
    form = CartQuantityForm(request.POST)
    if form.is_valid():
        item.quantity = form.cleaned_data["quantity"]
        item.save()
        messages.success(request, "Кількість оновлено.")
    else:
        messages.error(request, "Вкажіть коректну кількість (від 1 до 20).")
    return redirect("cart")


@require_POST
def cart_remove(request, pk):
    item = _cart_items(request).filter(pk=pk).first()
    if not item:
        messages.warning(request, "Позицію вже видалено.")
        return redirect("cart")
    item.delete()
    messages.success(request, "Позицію видалено з кошика.")
    return redirect("cart")


@require_POST
def cart_checkout(request):
    with transaction.atomic():
        items = list(_cart_items(request).select_for_update())
        if not items:
            messages.warning(request, "Ваш кошик порожній.")
            return redirect("cart")

        # Перевірка чи всі обрані каталожні моделі досі доступні для замовлення
        unavailable = [item.guitar.name for item in items if item.guitar and not item.guitar.is_available]
        if unavailable:
            messages.error(
                request,
                f"На жаль, наступні моделі тимчасово недоступні: {', '.join(unavailable)}. Будь ласка, видаліть їх перед оформленням."
            )
            return redirect("cart")

        item_ids = [item.pk for item in items]
        GuitarOrder.objects.filter(pk__in=item_ids).update(status=GuitarOrder.Status.PLACED)
        messages.success(request, f"Замовлення успішно оформлено ({len(items)} поз.)! Ми зв’яжемося з вами для підтвердження.")
        return redirect("cart")


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


def auth_logout(request):
    next_url = request.META.get("HTTP_REFERER") or "/"
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Ви вийшли з облікового запису.")
    return redirect(next_url)

