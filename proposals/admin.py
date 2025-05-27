from django.contrib import admin
from .models import Client, Proposal


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin interface for the Client model.
    """

    list_display = (
        "company_name",
        "email",
        "phone_number",
        "added_by",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at", "added_by")
    search_fields = ("company_name", "email", "phone_number")
    ordering = ("company_name",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("added_by",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "company_name",
                    "address",
                    "phone_number",
                    "email",
                    "added_by",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        """
        Optimize queryset to reduce database queries.
        """
        return super().get_queryset(request).select_related("added_by")

    def get_readonly_fields(self, request, obj=None):
        """
        Make added_by read-only when editing an existing client.
        """
        if obj:  # Editing an existing object
            return self.readonly_fields + ("added_by",)
        return self.readonly_fields


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    """
    Admin interface for the Proposal model.
    """

    list_display = ("title", "client", "created_by", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at", "client", "created_by")
    search_fields = ("title", "description", "client__company_name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("client", "created_by")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "client",
                    "created_by",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        """
        Optimize queryset to reduce database queries.
        """
        return (
            super()
            .get_queryset(request)
            .select_related("client", "created_by")
            .prefetch_related("client__added_by")
        )

    def get_readonly_fields(self, request, obj=None):
        """
        Make created_by read-only when editing an existing proposal.
        """
        if obj:  # Editing an existing object
            return self.readonly_fields + ("created_by",)
        return self.readonly_fields