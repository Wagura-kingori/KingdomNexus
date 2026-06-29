from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from students.models import Classroom
from .models import (
    Room,
    MasterTimetableEntry,
    ClassroomTimetable,
    ClassroomTimetableEntry,
    Period,
    TimetableGenerationConfig,
    GenerationBreak,
    ClassroomSubjectConfig,
    TimetableGenerationJob,
)
from .serializers import (
    RoomSerializer,
    MasterTimetableEntrySerializer,
    ClassroomTimetableSerializer,
    ClassroomTimetableEntrySerializer,
    PeriodSerializer,
    TimetableGenerationConfigSerializer,
    GenerationBreakSerializer,
    ClassroomSubjectConfigSerializer,
    TimetableGenerationJobSerializer,
)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]


class MasterTimetableEntryViewSet(viewsets.ModelViewSet):
    queryset = MasterTimetableEntry.objects.all()
    serializer_class = MasterTimetableEntrySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        classroom_id = self.request.query_params.get('classroom_id')
        academic_year = self.request.query_params.get('academic_year')
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
        if academic_year:
            qs = qs.filter(academic_year=academic_year)
        return qs

    def perform_create(self, serializer):
        school_id = self.request.data.get('school')
        if school_id:
            serializer.save(school_id=school_id)
        else:
            classroom_id = self.request.data.get('classroom')
            if classroom_id:
                try:
                    classroom = Classroom.objects.select_related(
                        'class_grade__school'
                    ).get(id=classroom_id)
                    serializer.save(school=classroom.class_grade.school)
                except Classroom.DoesNotExist:
                    serializer.save()
            else:
                serializer.save()


class ClassroomTimetableViewSet(viewsets.ModelViewSet):
    queryset = ClassroomTimetable.objects.all()
    serializer_class = ClassroomTimetableSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        classroom_id = self.request.query_params.get('classroom_id')
        academic_year = self.request.query_params.get('academic_year')
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
        if academic_year:
            qs = qs.filter(academic_year=academic_year)
        return qs


class ClassroomTimetableEntryViewSet(viewsets.ModelViewSet):
    queryset = ClassroomTimetableEntry.objects.all()
    serializer_class = ClassroomTimetableEntrySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        timetable_id = self.request.query_params.get('timetable_id')
        if timetable_id:
            qs = qs.filter(timetable_id=timetable_id)
        return qs


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        school_id = self.request.query_params.get('school_id')
        if school_id:
            qs = qs.filter(school_id=school_id)
        return qs

    def perform_create(self, serializer):
        school_id = self.request.data.get('school')
        if school_id:
            serializer.save(school_id=school_id)
        else:
            serializer.save(school=None)


class TimetableGenerationConfigViewSet(viewsets.ModelViewSet):
    queryset = TimetableGenerationConfig.objects.all()
    serializer_class = TimetableGenerationConfigSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        school_id = self.request.query_params.get('school_id')
        academic_year = self.request.query_params.get('academic_year')
        if school_id:
            qs = qs.filter(school_id=school_id)
        if academic_year:
            qs = qs.filter(academic_year=academic_year)
        return qs

    def perform_create(self, serializer):
        school_id = self.request.data.get('school')
        if school_id:
            serializer.save(school_id=school_id)
        else:
            serializer.save()


class GenerationBreakViewSet(viewsets.ModelViewSet):
    queryset = GenerationBreak.objects.all()
    serializer_class = GenerationBreakSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        config_id = self.request.query_params.get('config_id')
        if config_id:
            qs = qs.filter(config_id=config_id)
        return qs


class ClassroomSubjectConfigViewSet(viewsets.ModelViewSet):
    queryset = ClassroomSubjectConfig.objects.all()
    serializer_class = ClassroomSubjectConfigSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        config_id = self.request.query_params.get('config_id')
        classroom_id = self.request.query_params.get('classroom_id')
        if config_id:
            qs = qs.filter(config_id=config_id)
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
        return qs


class TimetableGenerationJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimetableGenerationJob.objects.all()
    serializer_class = TimetableGenerationJobSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        school_id = self.request.query_params.get('school_id')
        if school_id:
            qs = qs.filter(school_id=school_id)
        return qs.order_by('-started_at')


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def available_slots(request):
    classroom_id = request.query_params.get('classroom_id')
    academic_year = request.query_params.get('academic_year', '2025-2026')

    if not classroom_id:
        return Response({'error': 'classroom_id is required'}, status=400)

    entries = MasterTimetableEntry.objects.filter(
        classroom_id=classroom_id,
        academic_year=academic_year,
    ).select_related('teacher', 'subject', 'classroom', 'room')

    serializer = MasterTimetableEntrySerializer(entries, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def trigger_generation(request):
    from .tasks import generate_master_timetable
    from schools.models import School

    school_id = request.data.get('school_id')
    academic_year = request.data.get('academic_year', '2025-2026')

    if not school_id:
        return Response({'error': 'school_id is required'}, status=400)

    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        return Response({'error': 'School not found'}, status=404)

    try:
        TimetableGenerationConfig.objects.get(
            school=school,
            academic_year=academic_year
        )
    except TimetableGenerationConfig.DoesNotExist:
        return Response(
            {'error': 'No generation config found. Please set up the timetable configuration first.'},
            status=400
        )

    job = TimetableGenerationJob.objects.create(
        school=school,
        academic_year=academic_year,
        status='pending',
    )

    task = generate_master_timetable.delay(job.id)
    job.task_id = task.id
    job.save()

    return Response({
        'job_id': job.id,
        'task_id': task.id,
        'status': 'pending',
        'message': 'Timetable generation started in the background.',
    })