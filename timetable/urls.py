# from django.urls import path
# from . import views

# app_name = "timetable"

# urlpatterns = [
#     path("", views.timetable_list, name="timetable_list"),

#     # setup
#     path("classroom/<int:classroom_id>/setup/",
#          views.setup_timetable,
#          name="setup_timetable"),

#     # generate
#     path("classroom/<int:classroom_id>/generate/",
#          views.generate_timetable,
#          name="generate_timetable"),

#     # view
#     path("classroom/<int:classroom_id>/view/",
#          views.view_timetable,
#          name="view_timetable"),

#     # list
#     path("classrooms/",
#          views.timetable_list,
#          name="list"),

#     # teacher workload
#     path("teacher/workload/",
#          views.teacher_workload,
#          name="teacher_workload"),

#     # V2 endpoints
#     path("classroom/<int:classroom_id>/preview/",
#          views.preview_timetable,
#          name="preview_timetable"),

#     path("classroom/<int:classroom_id>/ajax-save/",
#          views.ajax_save_subject_config,
#          name="ajax_save_subject_config"),
#     path("classroom/<int:classroom_id>/conflicts/",
#      views.conflict_dashboard,
#      name="conflict_dashboard"),
#      path(
#     "ajax/teachers/",
#     views.ajax_subject_teachers,
#     name="ajax_subject_teachers"
# ),
# ]