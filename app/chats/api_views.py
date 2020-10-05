from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import LogSerializer
from .models import Log


@api_view(['GET'])
def log_list(request):
    """
    List all users, or create a new user.
    """
    if request.method == 'GET':
        logs = Log.objects.all()
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def log_create(request):
    if request.method == 'GET':
        params = Log._meta.fields
        for param in params:
            param = param.get_attname()
            if param == 'line_user_id':
                request.data[param] = request.query_params.get(
                    'customer_id', None)
            else:
                request.data[param] = request.query_params.get(param, None)

        serializer = LogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
