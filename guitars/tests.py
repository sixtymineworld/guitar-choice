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

    def test_models_and_relationships(self):
        self.assertIn("Fender Stratocaster Standard", str(self.guitar1))
        self.assertEqual(self.guitar1.get_absolute_url(), f"/guitars/{self.guitar1.pk}/")

        self.assertEqual(self.review1.user, self.user1)
        self.assertEqual(self.review1.guitar, self.guitar1)
        self.assertIn("alex", str(self.review1))

        feedback = Feedback.objects.create(name="Олег", email="oleg@example.com", message="Привіт, потрібна допомога.")
        self.assertIn("Олег", str(feedback))

        order = GuitarOrder.objects.create(guitar=self.guitar1, status=GuitarOrder.Status.PLACED, quantity=1)
        self.assertIn(f"Замовлення №{order.pk}", str(order))

    def test_custom_templatetags(self):
        self.assertEqual(format_uah(28000), "28 000 ₴")
        stars_html = render_stars(4)
        self.assertIn("★★★★☆", stars_html)

    def test_forms_and_validators(self):
        with self.assertRaises(ValidationError):
            validate_no_spam_links("Дивіться ціни на http://spam.com !")
        self.assertIsNone(validate_no_spam_links("Чудова гітара, рекомендую всім!"))

        invalid_form = ReviewForm(data={"rating": 5, "comment": "Коротко"})
        self.assertFalse(invalid_form.is_valid())
        self.assertIn("Відгук повинен містити щонайменше 10 символів.", invalid_form.errors["comment"])

        filter_form = CatalogSearchForm(data={"q": "Fender"})
        self.assertTrue(filter_form.is_valid())

    def test_catalog_views_and_pagination(self):
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

        search_res = self.client.get(reverse("guitars:catalog"), {"q": "Gibson"})
        self.assertEqual(search_res.status_code, 200)
        self.assertEqual(len(search_res.context["guitars"]), 1)
        self.assertEqual(search_res.context["guitars"][0].brand, "Gibson")

        sort_asc_res = self.client.get(reverse("guitars:catalog"), {"sort": "price_asc"})
        self.assertEqual(sort_asc_res.status_code, 200)
        prices_asc = [g.price for g in sort_asc_res.context["guitars"]]
        self.assertEqual(prices_asc, sorted(prices_asc))

        sort_desc_res = self.client.get(reverse("guitars:catalog"), {"sort": "price_desc"})
        self.assertEqual(sort_desc_res.status_code, 200)
        prices_desc = [g.price for g in sort_desc_res.context["guitars"]]
        self.assertEqual(prices_desc, sorted(prices_desc, reverse=True))

        price_filter_res = self.client.get(reverse("guitars:catalog"), {"min_price": "20000", "max_price": "50000"})
        self.assertEqual(price_filter_res.status_code, 200)
        for g in price_filter_res.context["guitars"]:
            self.assertTrue(Decimal("20000") <= g.price <= Decimal("50000"))

        detail_res = self.client.get(self.guitar1.get_absolute_url())
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, "Stratocaster Standard")

    def test_review_permissions_and_crud(self):
        create_url = reverse("guitars:review_create", kwargs={"pk": self.guitar1.pk})
        anon_res = self.client.get(create_url)
        self.assertEqual(anon_res.status_code, 302)

        self.client.force_login(self.user2)
        post_res = self.client.post(create_url, {"rating": 5, "comment": "Дуже крутий звук, рекомендую!"})
        self.assertEqual(post_res.status_code, 302)
        new_review = Review.objects.filter(guitar=self.guitar1, user=self.user2).first()
        self.assertIsNotNone(new_review)
        self.assertEqual(new_review.user, self.user2)

        update_url = reverse("guitars:review_update", kwargs={"pk": self.review1.pk})
        forbidden_res = self.client.get(update_url)
        self.assertEqual(forbidden_res.status_code, 403)

        self.client.force_login(self.user1)
        owner_res = self.client.get(update_url)
        self.assertEqual(owner_res.status_code, 200)

    def test_staff_roles_and_access(self):
        staff_url = reverse("guitars:staff_orders")
        self.client.force_login(self.user1)
        res = self.client.get(staff_url)
        self.assertEqual(res.status_code, 403)

        self.client.force_login(self.staff_user)
        res_staff = self.client.get(staff_url)
        self.assertEqual(res_staff.status_code, 200)

    def test_logout_post_only(self):
        self.client.force_login(self.user1)
        logout_url = reverse("guitars:auth_logout")
        get_res = self.client.get(logout_url)
        self.assertEqual(get_res.status_code, 405)

        post_res = self.client.post(logout_url)
        self.assertEqual(post_res.status_code, 302)

