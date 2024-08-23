from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, get_user_model
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import PendingUser
from .serializers import *
from rest_framework.authtoken.models import Token
import logging

# class based views starts here
logger = logging.getLogger(__name__)
class AuthViews(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        action = request.data.get('action')
        if action == 'signup':
            return self.signup(request)
        elif action == 'login':
            return self.login(request)
        # elif action == 'change_password':
        #     return self.change_password(request)
        # elif action == 'forgot_password':
        #     return self.forgot_password(request)
        # elif action == 'reset_password':
        #     return self.reset_password(request)
        # elif action == 'logout':
        #     return self.logout(request)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    def signup(self, request):
        try:
            serializer = SignUpSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                pending_user = PendingUser(
                    email=data['email'],
                    username=data['username'],
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    mobile_number=data.get('mobile_number', '')

                )
                pending_user.save()
                subject = 'Signup Request Received'
                message = 'Thank you for signing up! Please wait for admin approval before you can log in.'
                recipient_list = [pending_user.email]
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
                return Response({'message': 'Signup request submitted. Await approval.'},
                                status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error during signup: {e}", exc_info=True)
            return Response({'message': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




    def login(self, request):
        try:
            if request.method == 'POST':
                serializer = EmailLoginSerializer(data=request.data)
                if serializer.is_valid():
                    email = serializer.validated_data['email']
                    password = serializer.validated_data['password']
                    try:
                        user = User.objects.get(email=email)
                        if user.is_suspended:
                            if user.suspension_end_date and user.suspension_end_date > timezone.now():
                                return Response({'message': 'Your account is suspended. Please contact Admin.'},
                                                status=403)

                        user = authenticate(request, username=user.username, password=password)
                    except User.DoesNotExist:
                        user = None

                    if user is not None:
                        login(request, user)
                        token, created = Token.objects.get_or_create(user=user)
                        return Response({'message': 'Login successful', 'username': user.username, 'token': token.key},
                                        status=200)
                    else:
                        return Response({'message': 'Invalid credentials'}, status=401)
                else:
                    return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({'message': 'Something went wrong', 'error': str(e)}, status=500)

    def change_password(self, request):
        try:
            if request.method == 'POST':
                serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response({'message': 'Password updated successfully'}, status=200)
                else:
                    return Response(serializer.errors, status=400)
        except:
            return Response({'message': 'Something went wrong'}, status=500)

    def forgot_password(self, request):
        try:
            email = request.data.get('email')

            if not email:
                return Response({'message': 'Email is required'}, status=400)

            user = get_user_model().objects.filter(email=email).first()

            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(user.pk.to_bytes(4, 'big'))
                reset_password_link = f'http://127.0.0.1:8000/reset-password/{uid}/{token}/'
                print(f'Reset password link: {reset_password_link}')
                return Response({'message': 'Password reset link has been sent to your mail'}, status=200)
            else:
                return Response({'message': 'User not found'}, status=404)

        except:
            return Response({'error': 'Something went wrong'}, status=500)

    def reset_password(self, request):
        try:
            uid = request.data.get('uid')
            token = request.data.get('token')
            new_password = request.data.get('new_password')

            if not all([uid, token, new_password]):
                return Response({'message': 'UID, token, and new password are required'}, status=400)
            else:
                try:
                    uid = urlsafe_base64_decode(uid)
                    user = get_user_model().objects.get(pk=int.from_bytes(uid, 'big'))

                    if default_token_generator.check_token(user, token):
                        user.set_password(new_password)
                        user.save()
                        return Response({'message': 'Password reset successfully'}, status=200)
                    else:
                        return Response({'message': 'Invalid token'}, status=400)

                except (TypeError, ValueError, OverflowError):
                    return Response({'message': 'Invalid UID format'}, status=400)
                except get_user_model().DoesNotExist:
                    return Response({'message': 'User not found'}, status=400)

        except:
            return Response({'error': 'Something went wrong'}, status=500)

    def logout(self, request):
        try:
            if request.method == 'POST':
                # Deleted the token associated with the user
                Token.objects.filter(user=request.user).delete()
                return Response({'message': 'Logout successful'}, status=200)
            else:
                return Response({'message': 'Method not allowed'}, status=405)
        except:
            return Response({'message': 'Something went wrong'}, status=500)

