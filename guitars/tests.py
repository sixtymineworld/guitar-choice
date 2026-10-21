from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from guitars.forms import CatalogSearchForm, ReviewForm
from guitars.models import Feedback, Guitar, GuitarOrder, Review
from guitars.templatetags.guitar_tags import format_uah, render_stars
from guitars.validators import validate_no_spam_links


class RequirementsTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="alex", password="password123")
        self.user2 = User.objects.create_user(username="maria", password="password123")
        self.staff_user = User.objects.create_user(username="admin_staff", password="password123", is_staff=True)

        self.guitar1 = Guitar.objects.create(
            name="Stratocaster Standard",
            brand="Fender",
            guitar_type=Guitar.GuitarType.ELECTRIC,
            price=Decimal("28000.00"),
            description="Легендарна електрогітара для року та блюзу.",
            material="Вільха",
            strings_count=6,
            is_available=True,
        )
        self.guitar2 = Guitar.objects.create(
            name="Les Paul Classic",
            brand="Gibson",
            guitar_type=Guitar.GuitarType.ELECTRIC,
            price=Decimal("45000.00"),
            description="Потужний звук махагоні.",
            material="Махагоні",
            strings_count=6,
            is_available=True,
        )
        self.review1 = Review.objects.create(
            guitar=self.guitar1,
            user=self.user1,
            rating=5,
            comment="Фантастичний інструмент, грати одне задоволення!",
        )

    def test_b3_models_and_relationships(self):
        """В3.1, В3.2: 4 доменні моделі, зв'язок через ForeignKey, поле власника, __str__()."""
        # 4 Domain models: Guitar, GuitarOrder, Feedback, Review
        self.assertIn("Fender Stratocaster Standard", str(self.guitar1))
        self.assertEqual(self.guitar1.get_absolute_url(), f"/guitars/{self.guitar1.pk}/")

        self.assertEqual(self.review1.user, self.user1)
        self.assertEqual(self.review1.guitar, self.guitar1)
        self.assertIn("alex", str(self.review1))

        feedback = Feedback.objects.create(name="Олег", email="oleg@example.com", message="Привіт, потрібна допомога.")
        self.assertIn("Олег", str(feedback))

        order = GuitarOrder.objects.create(guitar=self.guitar1, status=GuitarOrder.Status.PLACED, quantity=1)
        self.assertIn(f"Замовлення №{order.pk}", str(order))

    def test_b4_custom_templatetags(self):
        """В4.3: Власні DTL-теги."""
        self.assertEqual(format_uah(28000), "28 000 ₴")
        stars_html = render_stars(4)
        self.assertIn("★★★★☆", stars_html)

    def test_b5_forms_and_validators(self):
        """В5.1, В5.2, В5.3: ModelForm, чиста форма, кастомний валідатор."""
        # Standalone validator
        with self.assertRaises(ValidationError):
            validate_no_spam_links("Дивіться ціни на http://spam.com !")
        self.assertIsNone(validate_no_spam_links("Чудова гітара, рекомендую всім!"))

        # ReviewForm explicit fields and validation in Ukrainian
        invalid_form = ReviewForm(data={"rating": 5, "comment": "Коротко"})
        self.assertFalse(invalid_form.is_valid())
        self.assertIn("Відгук повинен містити щонайменше 10 символів.", invalid_form.errors["comment"])

        # Non-model form
        filter_form = CatalogSearchForm(data={"q": "Fender"})
        self.assertTrue(filter_form.is_valid())

    def test_b6_generic_views_and_pagination(self):
        """В6.1, В6.3, В6.4, В6.5: ListView з пагінацією та get_queryset, DetailView з <int:pk>."""
        # Create additional guitars to verify pagination (paginate_by = 6)
        for i in range(10):
            Guitar.objects.create(
                name=f"Guitar Model {i}",
                brand="Yamaha",
                guitar_type=Guitar.GuitarType.ACOUSTIC,
                price=Decimal("12000.00"),
                description="Акустична гітара",
                material="Ялина",
            )
        response = self.client.get(reverse("guitars:catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["guitars"]), 6)

        # Search filter via get_queryset
        search_res = self.client.get(reverse("guitars:catalog"), {"q": "Gibson"})
        self.assertEqual(search_res.status_code, 200)
        self.assertEqual(len(search_res.context["guitars"]), 1)
        self.assertEqual(search_res.context["guitars"][0].brand, "Gibson")

        # DetailView with <int:pk>
        detail_res = self.client.get(self.guitar1.get_absolute_url())
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, "Stratocaster Standard")

    def test_b7_permissions_and_review_crud(self):
        """В7.1, В7.2, В7.3: Автентифікація, автопризначення власника, заборона чужого редагування."""
        # Review Create: anonymous user is redirected to login (LoginRequiredMixin)
        create_url = reverse("guitars:review_create", kwargs={"pk": self.guitar1.pk})
        anon_res = self.client.get(create_url)
        self.assertEqual(anon_res.status_code, 302)

        # Authenticated user creates review -> owner assigned in form_valid
        self.client.force_login(self.user2)
        post_res = self.client.post(create_url, {"rating": 5, "comment": "Дуже крутий звук, рекомендую!"})
        self.assertEqual(post_res.status_code, 302)
        new_review = Review.objects.filter(guitar=self.guitar1, user=self.user2).first()
        self.assertIsNotNone(new_review)
        self.assertEqual(new_review.user, self.user2)

        # User2 tries to edit User1's review -> 403 Forbidden (UserPassesTestMixin)
        update_url = reverse("guitars:review_update", kwargs={"pk": self.review1.pk})
        forbidden_res = self.client.get(update_url)
        self.assertEqual(forbidden_res.status_code, 403)

        # User1 (owner) can edit own review
        self.client.force_login(self.user1)
        owner_res = self.client.get(update_url)
        self.assertEqual(owner_res.status_code, 200)

    def test_b7_staff_roles_and_access(self):
        """В7.4, В7.5: Ролі та захист на сервері."""
        staff_url = reverse("guitars:staff_orders")
        # Regular user denied 403
        self.client.force_login(self.user1)
        res = self.client.get(staff_url)
        self.assertEqual(res.status_code, 403)

        # Staff user allowed 200
        self.client.force_login(self.staff_user)
        res_staff = self.client.get(staff_url)
        self.assertEqual(res_staff.status_code, 200)

    def test_b7_logout_post_only(self):
        """В7.1: Вихід лише через POST."""
        self.client.force_login(self.user1)
        logout_url = reverse("guitars:auth_logout")
        # GET is rejected with 405 Method Not Allowed
        get_res = self.client.get(logout_url)
        self.assertEqual(get_res.status_code, 405)

        # POST succeeds
        post_res = self.client.post(logout_url)
        self.assertEqual(post_res.status_code, 302)

