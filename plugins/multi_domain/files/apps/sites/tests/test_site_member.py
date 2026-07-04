"""
Unit tests for SiteMember model and site management API.

Run with:
    make test ARGS='apps.sites.tests.test_site_member'
"""

import unittest

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

try:
    # Optional integration: the API-key app is not part of the free boilerplate.
    from apps.api.models import UserAPIKey

    HAS_API_KEYS = True
except ImportError:
    UserAPIKey = None
    HAS_API_KEYS = False
from apps.sites.models import SiteMember, SiteProfile

User = get_user_model()


class SiteMemberModelTest(TestCase):
    """Tests for SiteMember model."""

    def setUp(self):
        """Create test site and users."""
        self.site = Site.objects.create(domain="member-test.example.com", name="Member Test Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="Member Test",
            is_active=True,
            is_primary=True,
        )
        self.admin_user = User.objects.create_user(
            username="admin_member",
            email="admin@member.com",
            password="testpass123",
        )
        self.viewer_user = User.objects.create_user(
            username="viewer_member",
            email="viewer@member.com",
            password="testpass123",
        )

    def test_create_site_member(self):
        """Test creating a site member."""
        member = SiteMember.objects.create(
            site_profile=self.profile,
            user=self.admin_user,
            role=SiteMember.Role.ADMIN,
        )
        self.assertEqual(member.role, SiteMember.Role.ADMIN)
        self.assertFalse(member.is_owner)

    def test_create_site_owner(self):
        """Test creating a site owner."""
        member = SiteMember.objects.create(
            site_profile=self.profile,
            user=self.admin_user,
            role=SiteMember.Role.VIEWER,  # Should be upgraded to admin
            is_owner=True,
        )
        # Owner is always admin
        self.assertEqual(member.role, SiteMember.Role.ADMIN)
        self.assertTrue(member.is_owner)

    def test_unique_user_per_site(self):
        """Test that a user can only be a member once per site."""
        SiteMember.objects.create(
            site_profile=self.profile,
            user=self.admin_user,
            role=SiteMember.Role.ADMIN,
        )
        # ValidationError is raised by full_clean() before IntegrityError
        with self.assertRaises((ValidationError, IntegrityError)):
            SiteMember.objects.create(
                site_profile=self.profile,
                user=self.admin_user,
                role=SiteMember.Role.VIEWER,
            )

    def test_cannot_demote_owner(self):
        """Test that owner cannot be demoted."""
        member = SiteMember.objects.create(
            site_profile=self.profile,
            user=self.admin_user,
            role=SiteMember.Role.ADMIN,
            is_owner=True,
        )
        member.role = SiteMember.Role.VIEWER
        with self.assertRaises(ValidationError):
            member.save()

    def test_cannot_remove_owner_status(self):
        """Test that owner status cannot be removed."""
        member = SiteMember.objects.create(
            site_profile=self.profile,
            user=self.admin_user,
            role=SiteMember.Role.ADMIN,
            is_owner=True,
        )
        member.is_owner = False
        with self.assertRaises(ValidationError):
            member.save()

    def test_user_can_be_member_of_multiple_sites(self):
        """Test that a user can be member of multiple sites."""
        site2 = Site.objects.create(domain="member2.example.com", name="Member Test Site 2")
        profile2 = SiteProfile.objects.create(
            site=site2,
            site_name="Member Test 2",
            is_active=True,
        )

        member1 = SiteMember.objects.create(
            site_profile=self.profile,
            user=self.admin_user,
            role=SiteMember.Role.ADMIN,
        )
        member2 = SiteMember.objects.create(
            site_profile=profile2,
            user=self.admin_user,
            role=SiteMember.Role.VIEWER,
        )

        self.assertEqual(self.admin_user.site_memberships.count(), 2)
        self.assertEqual(member1.role, SiteMember.Role.ADMIN)
        self.assertEqual(member2.role, SiteMember.Role.VIEWER)


class SiteManagementAPITest(TestCase):
    """Tests for site management API endpoints."""

    def setUp(self):
        """Create test site, users, and API client."""
        self.client = APIClient()

        # Create site
        self.site = Site.objects.create(domain="api-manage.example.com", name="API Manage Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="API Manage Test",
            is_active=True,
            is_primary=True,
            features={"enable_blog": True},
        )

        # Create users
        self.admin_user = User.objects.create_user(
            username="api_admin",
            email="api_admin@test.com",
            password="testpass123",
        )
        self.viewer_user = User.objects.create_user(
            username="api_viewer",
            email="api_viewer@test.com",
            password="testpass123",
        )
        self.no_access_user = User.objects.create_user(
            username="no_access",
            email="no_access@test.com",
            password="testpass123",
        )
        self.superuser = User.objects.create_superuser(
            username="super",
            email="super@test.com",
            password="testpass123",
        )

        # Create memberships
        self.admin_member = SiteMember.objects.create(
            site_profile=self.profile,
            user=self.admin_user,
            role=SiteMember.Role.ADMIN,
            is_owner=True,
        )
        self.viewer_member = SiteMember.objects.create(
            site_profile=self.profile,
            user=self.viewer_user,
            role=SiteMember.Role.VIEWER,
        )

    def test_list_sites_unauthenticated(self):
        """Test that unauthenticated users cannot list sites."""
        url = reverse("sites:site-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_sites_authenticated_no_access(self):
        """Test that users without site access see empty list."""
        self.client.force_authenticate(user=self.no_access_user)
        url = reverse("sites:site-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Handle paginated response
        results = data.get("results", data) if isinstance(data, dict) else data
        self.assertEqual(len(results), 0)

    def test_list_sites_viewer(self):
        """Test that viewers can list their sites."""
        self.client.force_authenticate(user=self.viewer_user)
        url = reverse("sites:site-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Handle paginated response
        results = data.get("results", data) if isinstance(data, dict) else data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["site_name"], "API Manage Test")
        self.assertEqual(results[0]["user_role"], "viewer")

    def test_list_sites_admin(self):
        """Test that admins can list their sites."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Handle paginated response
        results = data.get("results", data) if isinstance(data, dict) else data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["user_role"], "admin")

    def test_list_sites_superuser_sees_all(self):
        """Test that superusers see all active sites."""
        self.client.force_authenticate(user=self.superuser)
        url = reverse("sites:site-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Handle paginated response
        results = data.get("results", data) if isinstance(data, dict) else data
        self.assertGreaterEqual(len(results), 1)
        # Superuser role is "superuser" - find our test site
        test_site = next((s for s in results if s["site_name"] == "API Manage Test"), None)
        self.assertIsNotNone(test_site)
        self.assertEqual(test_site["user_role"], "superuser")

    def test_retrieve_site_viewer(self):
        """Test that viewers can retrieve site details."""
        self.client.force_authenticate(user=self.viewer_user)
        url = reverse("sites:site-detail", kwargs={"pk": self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["site_name"], "API Manage Test")

    def test_retrieve_site_no_access(self):
        """Test that users without access cannot retrieve site."""
        self.client.force_authenticate(user=self.no_access_user)
        url = reverse("sites:site-detail", kwargs={"pk": self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_site_admin(self):
        """Test that admins can update site configuration."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-detail", kwargs={"pk": self.profile.pk})
        response = self.client.patch(url, {"site_name": "Updated Name"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.site_name, "Updated Name")

    def test_update_site_viewer_forbidden(self):
        """Test that viewers cannot update site configuration."""
        self.client.force_authenticate(user=self.viewer_user)
        url = reverse("sites:site-detail", kwargs={"pk": self.profile.pk})
        response = self.client.patch(url, {"site_name": "Updated Name"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_features(self):
        """Test updating feature flags."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-update-features", kwargs={"pk": self.profile.pk})
        response = self.client.patch(url, {"features": {"enable_shop": True, "enable_blog": False}}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.features["enable_shop"])
        self.assertFalse(self.profile.features["enable_blog"])

    def test_invalid_site_id_non_numeric(self):
        """Test that non-numeric site_id returns 400 error."""
        self.client.force_authenticate(user=self.admin_user)
        url = "/api/sites/manage/invalid/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invalid_site_id", str(response.data))

    def test_invalid_site_id_empty(self):
        """Test that empty site_id in URL returns 400 error."""
        self.client.force_authenticate(user=self.admin_user)
        url = "/api/sites/manage//members/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("site_id is required", str(response.data))

    # --- F1: member-add never mints/returns an API key ---

    def test_add_member_response_excludes_api_key(self):
        """F1: adding a member returns no api_key field (no key is minted for the user)."""
        new_user = User.objects.create_user(
            username="f1_new",
            email="f1_new@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-add-member", kwargs={"pk": self.profile.pk})
        response = self.client.post(url, {"email": new_user.email, "role": "viewer"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("api_key", response.json())
        self.assertTrue(SiteMember.objects.filter(site_profile=self.profile, user=new_user).exists())

    def test_add_member_rejects_create_api_key_flag(self):
        """F1: the removed create_api_key input has no effect and no key field is returned."""
        new_user = User.objects.create_user(
            username="f1_flag",
            email="f1_flag@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-add-member", kwargs={"pk": self.profile.pk})
        response = self.client.post(
            url,
            {"email": new_user.email, "role": "viewer", "create_api_key": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("api_key", response.json())

    # --- F2: create/destroy are superuser-only; site admins get a restricted serializer ---

    def test_create_site_forbidden_for_site_admin(self):
        """F2: a site admin (non-superuser) cannot create a site."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-list")
        response = self.client.post(url, {"site_name": "Rogue Site"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_site_forbidden_for_site_admin(self):
        """F2: a site admin (non-superuser) cannot delete a site."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-detail", kwargs={"pk": self.profile.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_site_admin_cannot_edit_security_fields(self):
        """F2: a site admin's update silently ignores security-critical fields."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-detail", kwargs={"pk": self.profile.pk})
        response = self.client.patch(
            url,
            {
                "site_name": "Admin Renamed",
                "custom_css": "body{display:none}",
                "head_scripts": [{"type": "inline", "content": "alert(1)"}],
                "auth_mode": "shared",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        # Allowed branding field changed.
        self.assertEqual(self.profile.site_name, "Admin Renamed")
        # Security-critical fields untouched.
        self.assertEqual(self.profile.custom_css, "")
        self.assertEqual(self.profile.head_scripts, [])
        self.assertEqual(self.profile.auth_mode, "isolated")

    def test_superuser_can_edit_security_fields(self):
        """F2: a superuser may edit security-critical fields."""
        self.client.force_authenticate(user=self.superuser)
        url = reverse("sites:site-detail", kwargs={"pk": self.profile.pk})
        response = self.client.patch(url, {"custom_css": "body{color:red}"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.custom_css, "body{color:red}")


@unittest.skipUnless(HAS_API_KEYS, "requires the optional apps.api key app")
class SiteMemberManagementAPITest(TestCase):
    """Tests for site member management API endpoints."""

    def setUp(self):
        """Create test site, users, and API client."""
        self.client = APIClient()

        # Create site
        self.site = Site.objects.create(domain="member-manage.example.com", name="Member Manage Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="Member Manage Test",
            is_active=True,
            is_primary=True,
        )

        # Create users
        self.admin_user = User.objects.create_user(
            username="member_admin",
            email="member_admin@test.com",
            password="testpass123",
        )
        self.viewer_user = User.objects.create_user(
            username="member_viewer",
            email="member_viewer@test.com",
            password="testpass123",
        )
        self.new_user = User.objects.create_user(
            username="new_member",
            email="new_member@test.com",
            password="testpass123",
        )

        # Create owner membership
        self.owner_member = SiteMember.objects.create(
            site_profile=self.profile,
            user=self.admin_user,
            role=SiteMember.Role.ADMIN,
            is_owner=True,
        )
        self.viewer_member = SiteMember.objects.create(
            site_profile=self.profile,
            user=self.viewer_user,
            role=SiteMember.Role.VIEWER,
        )

    def test_list_members(self):
        """Test listing site members (admin only)."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-list-members", kwargs={"pk": self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_list_members_viewer_forbidden(self):
        """Test that viewers cannot list members."""
        self.client.force_authenticate(user=self.viewer_user)
        url = reverse("sites:site-list-members", kwargs={"pk": self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_member(self):
        """Test adding a new member (no API key is minted or returned)."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-add-member", kwargs={"pk": self.profile.pk})
        response = self.client.post(url, {"email": "new_member@test.com", "role": "viewer"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SiteMember.objects.filter(site_profile=self.profile, user=self.new_user).exists())
        # F1: the response must NOT contain an API key, and no key may be created.
        data = response.json()
        self.assertNotIn("api_key", data)
        self.assertFalse(UserAPIKey.objects.filter(user=self.new_user).exists())

    def test_add_member_duplicate(self):
        """Test adding an existing member fails."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-add-member", kwargs={"pk": self.profile.pk})
        response = self.client.post(url, {"email": "member_viewer@test.com", "role": "admin"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_member_nonexistent_user(self):
        """Test adding a nonexistent user fails."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("sites:site-add-member", kwargs={"pk": self.profile.pk})
        response = self.client.post(url, {"email": "nonexistent@test.com", "role": "viewer"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_member_role(self):
        """Test updating a member's role."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse(
            "sites:site-update-member",
            kwargs={"pk": self.profile.pk, "user_id": self.viewer_user.id},
        )
        response = self.client.patch(url, {"role": "admin"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.viewer_member.refresh_from_db()
        self.assertEqual(self.viewer_member.role, SiteMember.Role.ADMIN)

    def test_cannot_demote_owner_via_api(self):
        """Test that owner cannot be demoted via API."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse(
            "sites:site-update-member",
            kwargs={"pk": self.profile.pk, "user_id": self.admin_user.id},
        )
        response = self.client.patch(url, {"role": "viewer"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_member(self):
        """Test removing a member."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse(
            "sites:site-remove-member",
            kwargs={"pk": self.profile.pk, "user_id": self.viewer_user.id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SiteMember.objects.filter(site_profile=self.profile, user=self.viewer_user).exists())

    def test_cannot_remove_owner(self):
        """Test that owner cannot be removed."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse(
            "sites:site-remove-member",
            kwargs={"pk": self.profile.pk, "user_id": self.admin_user.id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@unittest.skipUnless(HAS_API_KEYS, "requires the optional apps.api key app")
class SiteAPIKeyAuthTest(TestCase):
    """Tests for API key authentication with site access."""

    def setUp(self):
        """Create test site, user, and API key."""
        self.client = APIClient()

        # Create site
        self.site = Site.objects.create(domain="apikey-test.example.com", name="API Key Test Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="API Key Test",
            is_active=True,
            is_primary=True,
        )

        # Create user
        self.user = User.objects.create_user(
            username="apikey_user",
            email="apikey@test.com",
            password="testpass123",
        )

        # Create membership
        SiteMember.objects.create(
            site_profile=self.profile,
            user=self.user,
            role=SiteMember.Role.ADMIN,
        )

        # Create API key
        self.api_key, self.key = UserAPIKey.objects.create_key(
            name="Test API Key",
            user=self.user,
        )

    def test_list_sites_with_api_key(self):
        """Test listing sites using API key authentication."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Api-Key {self.key}")
        url = reverse("sites:site-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Handle paginated response
        results = data.get("results", data) if isinstance(data, dict) else data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["site_name"], "API Key Test")

    def test_retrieve_site_with_api_key(self):
        """Test retrieving site using API key authentication."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Api-Key {self.key}")
        url = reverse("sites:site-detail", kwargs={"pk": self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["site_name"], "API Key Test")

    def test_update_site_with_api_key(self):
        """Test updating site using API key authentication."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Api-Key {self.key}")
        url = reverse("sites:site-detail", kwargs={"pk": self.profile.pk})
        response = self.client.patch(url, {"site_name": "Updated via API Key"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.site_name, "Updated via API Key")

    def test_invalid_api_key_rejected(self):
        """Test that invalid API key is rejected."""
        self.client.credentials(HTTP_AUTHORIZATION="Api-Key invalid_key_here")
        url = reverse("sites:site-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
