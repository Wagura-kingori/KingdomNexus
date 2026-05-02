from django.contrib import admin
from .models import Project, School, GalleryImage, Sermon, Donation, PrayerRequest,Teacher, Student, Achievement
from django.contrib import admin



@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "contact_phone", "student_count", "teacher_count", "achievement_count")
    search_fields = ("name", "address", "contact_phone")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "admission_number", "school", "class_level", "age", "date_joined")
    list_filter = ("school", "class_level")
    search_fields = ("full_name", "admission_number")
    ordering = ("full_name",)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("full_name", "school", "subject", "staff_id", "hire_date")
    list_filter = ("school", "subject")
    search_fields = ("full_name", "staff_id")
    ordering = ("full_name",)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "school", "year")
    list_filter = ("school", "year")
    search_fields = ("title",)
    ordering = ("-year",)

@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "submitted_at", "is_read", "notified")
    list_filter = ("is_read", "submitted_at")
    search_fields = ("name", "email", "message", "subject")
    readonly_fields = ("submitted_at",)
    actions = ["mark_as_read"]

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} request(s) marked as read.")
    mark_as_read.short_description = "Mark selected requests as read"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'active', 'created_at')
    search_fields = ('title',)




@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')


@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'preacher')


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('amount', 'name', 'email', 'created_at')

