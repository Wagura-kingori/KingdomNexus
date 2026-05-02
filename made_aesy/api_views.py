from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def test_api(request):
    data = {"message": "API is working!"}
    return Response(data)
