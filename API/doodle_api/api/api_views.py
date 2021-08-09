import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class UserActivationView(APIView):
    """
        Activates newly registered user by calling '/users/activation/' end point
        https://djoser.readthedocs.io/en/latest/base_endpoints.html
    """

    def get(self, request, uid, token, format=None):
        payload = {
            'uid': uid,
            'token': token
        }
        # call user activation endpoint
        url = 'http://localhost:8000/api/auth/users/activation/'
        response = requests.post(url, data=payload)

        if response.status_code == 204:
            return Response({'detail': 'Account activated successfully!'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
