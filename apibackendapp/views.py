from django.shortcuts import render
from rest_framework import viewsets
from .models import Employee, Department
from django.contrib.auth.models import User
from .serializers import EmployeeSerializer, DepartmentSerializer, UserSerializer,SignupSerializer,LoginSerializer
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token



class SignupAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serializer = SignupSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user_id": user.id,
                "username": user.username,
                "token":token.key,
                "role": user.groups.all()[0].id if user.groups.exists() else None
                },status=status.HTTP_201_CREATED)
        else:
            response = {'status':status.HTTP_400_BAD_REQUEST,'data':serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]  
    def post(self,request):
        #Create an object for the LoginSerializer
        #By giving the data received to its constructor
        serializer = LoginSerializer(data = request.data)
        if serializer.is_valid():
            #Get the username, password from the validated data
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            #Try to authenticate the user using the username and password
            #If successfully authenticated, it will return back a vaild user object
            user = authenticate(request, username = username, password = password )
            if user is not None:
                #Get the token for the autheticated user
                token = Token.objects.get(user = user)
                response = {
                    "status": status.HTTP_200_OK,
                    "message": "success",
                    "username": user.username,
                    "role": user.groups.all()[0].id if user.groups.exists() else None,
                    "data": {
                        "Token": token.key
                    }
                }
                return Response(response, status=status.HTTP_200_OK) #login is successful
            else:
                response = {
                    "status": status.HTTP_401_UNAUTHORIZED,
                    "message": "Invaild username or password",
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED) #login failed 
        else:
            #If the request is not correct
            response = {'status':status.HTTP_400_BAD_REQUEST, 'data':serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    #permission_classes = []
    permission_classes = [IsAuthenticated]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['EmployeeName','Designation']
    permission_classes = []
    #permission_classes = [IsAuthenticated]



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    
    