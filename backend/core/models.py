from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended user profile for storing additional user information.
    Automatically created when a User is created.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    target_identity = models.TextField(
        blank=True,
        default="",
        help_text='User\'s target identity statement (e.g., "I am a healthy person")',
    )
    onboarding_completed = models.BooleanField(
        default=False, help_text="Has the user completed the onboarding flow?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal to automatically create UserProfile when User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Signal to save UserProfile when User is saved."""
    if hasattr(instance, "profile"):
        instance.profile.save()
