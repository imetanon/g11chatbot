from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import User
from users.serializers import UserSerializer

@api_view(['GET'])
def user_list(request):
    """
    List all users, or create a new user.
    """
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
@api_view(['GET'])
def user_create(request):
    if request.method == 'GET':
        params = User._meta.fields
        for param in params:
            param = param.get_attname()
            if param == 'line_user_id':
                request.data[param] = request.query_params.get('customer_id', None)
            elif param == 'gender':
                gender = request.query_params.get('gender', 'U')
                if gender == 'ชาย':
                    gender = 'M'
                elif gender == 'หญิง':
                    gender = 'F'
                else:
                    gender = 'U'
                request.data[param] = gender
            else:
                request.data[param] = request.query_params.get(param, None)
            
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, line_user_id):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        user = User.objects.get(line_user_id=line_user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def check(request):
    line_user_id = request.query_params.get('customer_id', None)
    
    response = {
        'status_code': status.HTTP_404_NOT_FOUND,
        'message': ''
    }
    
    try:
        user = User.objects.get(line_user_id=line_user_id)
    except User.DoesNotExist:
        response['message'] = 'User Does not exist.'
        return Response(response,status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        
        response = {
            'status_code': status.HTTP_200_OK,
            'message': 'User exist.',
            'data': serializer.data,
            'intent': f"{{{{intent_googleplace}}}}"
        }
        
        return Response(response)