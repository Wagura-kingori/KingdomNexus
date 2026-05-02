
from django.db.models import Sum, Avg

def calculate_class_ranking(exam, classroom):
    from exams.models import ExamResult
    #  Get results for this exam + class
    results = ExamResult.objects.filter(
        exam=exam,
        student__classroom=classroom
    )

    #  Compute totals and averages
    for result in results:
        # total score = sum of all subjects for that exam
        total = ExamResult.objects.filter(
            exam=exam,
            student=result.student
        ).aggregate(total=Sum('score'))['total']

        avg = ExamResult.objects.filter(
            exam=exam,
            student=result.student
        ).aggregate(avg=Avg('score'))['avg']

        result.total_score = total
        result.average_score = avg
        result.save()

    #  Assign positions
    # Order by total score descending
    ranked = results.order_by('-total_score')

    position = 1
    for res in ranked:
        res.position = position
        res.save()
        position += 1
