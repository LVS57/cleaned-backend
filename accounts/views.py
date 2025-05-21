from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from accounts.models import Product
from .serializers import ProductSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tokens import account_activation_token
from rest_framework.views import APIView
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import redirect
from .tokens import account_activation_token

User = get_user_model()

class ActivateView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'detail': 'Account activated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid activation link'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(email=email, password=password, is_active=False)

        # Generate email activation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        current_site = get_current_site(request).domain
        activation_link = f'http://{current_site}/api/activate/{uid}/{token}/'

        # Send email
        send_mail(
            subject='Activate your QRSupplyScan account',
            message=f'Click the link to verify your account: {activation_link}',
            from_email='qrsupplyscan@example.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'detail': 'Registration successful. Check your email to activate your account.'}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        # Handle login logic
        return Response({'detail': 'Login successful', 'token': 'your_token'}, status=200)

# ✅ Landing endpoint that shows users and products
def index(request):
    User = get_user_model()

    # Get user emails (safe) — do not include passwords
    users = list(User.objects.values('email'))

    # Get product info
    products = list(Product.objects.values('name', 'description', 'quantity'))

    return JsonResponse({
        'registered_users': users,
        'products': products
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])

def create_product_from_qr(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Product created successfully", "product": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Product API ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
